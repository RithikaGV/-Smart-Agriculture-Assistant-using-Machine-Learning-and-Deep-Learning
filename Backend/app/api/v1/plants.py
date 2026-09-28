import os
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Plant, Sensor, SensorReading, HydroponicSystem, Farm, Grower
from app.schemas.schemas import PlantCreate, PlantUpdate, PlantResponse, PlantMetrics
from app.api.deps import get_current_grower, require_current_grower
from app.db.exporter import export_readable_data

router = APIRouter(prefix="/plants", tags=["plants"])

def ensure_grower_system(grower: Grower, db: Session) -> HydroponicSystem:
    farm = db.query(Farm).filter(Farm.grower_id == grower.id).first()
    if not farm:
        farm = Farm(grower_id=grower.id, name=f"{grower.name}'s Farm", location="Primary Greenhouse")
        db.add(farm)
        db.flush()

    sys_obj = db.query(HydroponicSystem).filter(HydroponicSystem.farm_id == farm.id).first()
    if not sys_obj:
        sys_obj = HydroponicSystem(farm_id=farm.id, grower_id=grower.id, name="NFT System 1", system_type="NFT Hydroponics")
        db.add(sys_obj)
        db.flush()
    return sys_obj

def build_plant_response(p: Plant, db: Session) -> PlantResponse:
    sensors_dict = {}
    db_sensors = db.query(Sensor).filter(Sensor.plant_id == p.id).all()
    
    for stype in ["temperature", "ph", "waterLevel", "humidity"]:
        sensors_dict[stype] = {
            "connected": False,
            "battery": 0,
            "address": "",
            "statusText": "Not Connected"
        }
        
    for s in db_sensors:
        sensors_dict[s.sensor_type] = {
            "connected": s.connected,
            "battery": s.battery,
            "address": s.address,
            "statusText": s.status_text
        }

    readings = db.query(SensorReading).filter(SensorReading.plant_id == p.id).order_by(SensorReading.timestamp.asc()).all()
    history = []
    if readings:
        grouped = {}
        for r in readings:
            day_str = r.timestamp.strftime("Day %d")
            if day_str not in grouped:
                grouped[day_str] = {"day": day_str, "heightCm": 15, "ph": p.ph, "temp": p.temperature, "humidity": p.humidity, "water": p.water_level}
            if r.sensor_type == "ph":
                grouped[day_str]["ph"] = r.value
            elif r.sensor_type in ["temp", "temperature"]:
                grouped[day_str]["temp"] = r.value
            elif r.sensor_type == "humidity":
                grouped[day_str]["humidity"] = r.value
            elif r.sensor_type in ["water", "waterLevel"]:
                grouped[day_str]["water"] = r.value
        history = list(grouped.values())
    
    if not history:
        history = [
            {"day": "Day 1", "heightCm": 10, "ph": p.ph, "temp": p.temperature, "humidity": p.humidity, "water": p.water_level},
            {"day": "Day 5", "heightCm": 18, "ph": p.ph, "temp": p.temperature, "humidity": p.humidity, "water": p.water_level}
        ]

    return PlantResponse(
        id=p.id,
        system_id=p.system_id,
        name=p.name,
        species=p.species,
        location=p.location or "Greenhouse Bay 1",
        image=p.image,
        status=p.status or "Healthy",
        metrics=PlantMetrics(
            temperature=p.temperature or 24.0,
            ph=p.ph or 6.2,
            humidity=p.humidity or 65.0,
            waterLevel=p.water_level or 90.0
        ),
        sensors=sensors_dict,
        growthHistory=history,
        notes=p.notes or ""
    )

@router.get("", response_model=List[PlantResponse])
def get_plants(
    system_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_grower: Optional[Grower] = Depends(get_current_grower)
):
    if not current_grower:
        return []

    query = db.query(Plant).filter(Plant.grower_id == current_grower.id)
    if system_id:
        query = query.filter(Plant.system_id == system_id)
        
    plants = query.all()
    return [build_plant_response(p, db) for p in plants]

@router.post("", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(
    plant_in: PlantCreate,
    db: Session = Depends(get_db),
    current_grower: Grower = Depends(require_current_grower)
):
    sys_obj = ensure_grower_system(current_grower, db)
    system_id = plant_in.system_id or sys_obj.id

    plant = Plant(
        grower_id=current_grower.id,
        system_id=system_id,
        name=plant_in.name,
        species=plant_in.species,
        location=plant_in.location,
        image=plant_in.image,
        notes=plant_in.notes,
        status="Healthy"
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)

    if plant_in.sensors:
        for stype, sdata in plant_in.sensors.items():
            if isinstance(sdata, dict):
                s = Sensor(
                    plant_id=plant.id,
                    sensor_type=stype,
                    address=sdata.get("address", f"SENSOR-{stype.upper()[:4]}"),
                    connected=sdata.get("connected", True),
                    battery=sdata.get("battery", 90),
                    status_text=sdata.get("statusText", "Connected and battery level good")
                )
                db.add(s)
        db.commit()

    export_readable_data(db)
    return build_plant_response(plant, db)

@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(plant_id: str, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return build_plant_response(plant, db)

@router.put("/{plant_id}", response_model=PlantResponse)
def update_plant(plant_id: str, plant_in: PlantUpdate, db: Session = Depends(get_db), current_grower: Grower = Depends(require_current_grower)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.grower_id == current_grower.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if plant_in.name is not None:
        plant.name = plant_in.name
    if plant_in.species is not None:
        plant.species = plant_in.species
    if plant_in.location is not None:
        plant.location = plant_in.location
    if plant_in.image is not None:
        plant.image = plant_in.image
    if plant_in.status is not None:
        plant.status = plant_in.status
    if plant_in.notes is not None:
        plant.notes = plant_in.notes

    if plant_in.metrics is not None:
        plant.temperature = plant_in.metrics.temperature
        plant.ph = plant_in.metrics.ph
        plant.humidity = plant_in.metrics.humidity
        plant.water_level = plant_in.metrics.waterLevel

    if plant_in.sensors is not None:
        for stype, sdata in plant_in.sensors.items():
            if isinstance(sdata, dict):
                sensor = db.query(Sensor).filter(Sensor.plant_id == plant.id, Sensor.sensor_type == stype).first()
                if not sensor:
                    sensor = Sensor(plant_id=plant.id, sensor_type=stype, address="")
                    db.add(sensor)
                sensor.connected = sdata.get("connected", True)
                sensor.battery = sdata.get("battery", 90)
                sensor.address = sdata.get("address", sensor.address)
                sensor.status_text = sdata.get("statusText", "Connected and battery level good")

    db.commit()
    db.refresh(plant)
    export_readable_data(db)
    return build_plant_response(plant, db)

@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: str, db: Session = Depends(get_db), current_grower: Grower = Depends(require_current_grower)):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.grower_id == current_grower.id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    db.delete(plant)
    db.commit()
    export_readable_data(db)
    return None

@router.get("/export/readable")
def get_readable_export(db: Session = Depends(get_db)):
    from app.db.exporter import EXPORT_JSON_PATH
    export_readable_data(db)
    if os.path.exists(EXPORT_JSON_PATH):
        with open(EXPORT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Export not available"}
