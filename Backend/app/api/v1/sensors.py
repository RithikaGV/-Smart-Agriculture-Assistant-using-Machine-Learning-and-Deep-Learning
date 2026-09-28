from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Sensor, SensorReading, Plant, Alert
from app.schemas.schemas import SensorConnectRequest, SensorReadingIngest, SensorReadingResponse

router = APIRouter(prefix="/sensors", tags=["sensors"])

def check_and_create_alerts(plant: Plant, db: Session):
    # Temperature & Water critical alert
    if plant.temperature > 32.0 or plant.water_level < 20.0:
        plant.status = "Critical"
        existing = db.query(Alert).filter(Alert.plant_id == plant.id, Alert.resolved == False, Alert.severity == "critical").first()
        if not existing:
            alert = Alert(
                plant_id=plant.id,
                grower_id=plant.grower_id,
                severity="critical",
                type="Temperature & Water Level",
                title=f"High Temperature ({plant.temperature}°C) & Low Water ({plant.water_level}%)",
                description=f"Temperature has reached {plant.temperature}°C and water level dropped to {plant.water_level}%. High risk of heat stress.",
                remedy_text="Turn on the evaporative cooling fan and trigger automated pump refill.",
                remedy_action="COOLING_AND_REFILL",
                timestamp="Just now"
            )
            db.add(alert)
    # pH Warning
    elif plant.ph < 5.5 or plant.ph > 7.0:
        plant.status = "Needs Attention"
        existing = db.query(Alert).filter(Alert.plant_id == plant.id, Alert.resolved == False, Alert.type == "pH Acidic Level").first()
        if not existing:
            alert = Alert(
                plant_id=plant.id,
                grower_id=plant.grower_id,
                severity="warning",
                type="pH Acidic Level",
                title=f"Water pH Imbalance (pH {plant.ph})",
                description=f"pH has moved to {plant.ph}. Ideal range is 5.8 - 6.5 for optimal nutrient absorption.",
                remedy_text="Add 15ml of Alkali Buffer (pH Up solution) to balance acidity.",
                remedy_action="ADD_ALKALI",
                timestamp="Just now"
            )
            db.add(alert)
    elif plant.humidity > 85.0:
        plant.status = "Needs Attention"
        existing = db.query(Alert).filter(Alert.plant_id == plant.id, Alert.resolved == False, Alert.type == "Humidity Risk").first()
        if not existing:
            alert = Alert(
                plant_id=plant.id,
                grower_id=plant.grower_id,
                severity="warning",
                type="Humidity Risk",
                title=f"High Air Humidity ({plant.humidity}%)",
                description=f"Relative humidity at {plant.humidity}%. Elevated risk of foliar mold.",
                remedy_text="Activate air circulation de-humidifiers and open ventilation louvers.",
                remedy_action="ACTIVATE_DEHUMIDIFIER",
                timestamp="Just now"
            )
            db.add(alert)
    else:
        plant.status = "Healthy"

@router.post("/connect")
def connect_sensor(req: SensorConnectRequest, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == req.plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    sensor = db.query(Sensor).filter(Sensor.plant_id == req.plant_id, Sensor.sensor_type == req.sensor_type).first()
    if not sensor:
        sensor = Sensor(
            plant_id=req.plant_id,
            sensor_type=req.sensor_type,
            address=req.address,
            connected=True,
            battery=95,
            status_text="Connected and battery level good"
        )
        db.add(sensor)
    else:
        sensor.address = req.address
        sensor.connected = True
        sensor.battery = 95
        sensor.status_text = "Connected and battery level good"

    db.commit()
    db.refresh(sensor)
    return {
        "message": f"Successfully connected {req.sensor_type} sensor ({req.address}) to plant {plant.name}",
        "sensor": {
            "id": sensor.id,
            "sensor_type": sensor.sensor_type,
            "address": sensor.address,
            "connected": sensor.connected,
            "battery": sensor.battery
        }
    }

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest_sensor_reading(reading: SensorReadingIngest, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == reading.plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    sensor = None
    if reading.sensor_address:
        sensor = db.query(Sensor).filter(Sensor.address == reading.sensor_address).first()
    if not sensor:
        sensor = db.query(Sensor).filter(Sensor.plant_id == plant.id, Sensor.sensor_type == reading.sensor_type).first()
    if not sensor:
        sensor = Sensor(
            plant_id=plant.id,
            sensor_type=reading.sensor_type,
            address=reading.sensor_address or f"SENSOR-{reading.sensor_type.upper()[:4]}",
            connected=True,
            battery=90,
            status_text="Connected"
        )
        db.add(sensor)
        db.flush()

    db_reading = SensorReading(
        sensor_id=sensor.id,
        plant_id=plant.id,
        grower_id=plant.grower_id,
        sensor_type=reading.sensor_type,
        value=reading.value,
        unit=reading.unit,
        extra_metadata=reading.extra_data
    )
    db.add(db_reading)

    stype = reading.sensor_type.lower()
    if stype in ["temperature", "temp"]:
        plant.temperature = reading.value
    elif stype in ["ph"]:
        plant.ph = reading.value
    elif stype in ["humidity"]:
        plant.humidity = reading.value
    elif stype in ["waterlevel", "water_level", "water"]:
        plant.water_level = reading.value

    check_and_create_alerts(plant, db)

    db.commit()
    db.refresh(db_reading)

    return {
        "status": "success",
        "reading_id": db_reading.id,
        "plant_id": plant.id,
        "plant_status": plant.status,
        "metrics": {
            "temperature": plant.temperature,
            "ph": plant.ph,
            "humidity": plant.humidity,
            "waterLevel": plant.water_level
        }
    }

@router.get("/history/{plant_id}", response_model=List[SensorReadingResponse])
def get_sensor_history(plant_id: str, db: Session = Depends(get_db)):
    readings = db.query(SensorReading).filter(SensorReading.plant_id == plant_id).order_by(SensorReading.timestamp.desc()).limit(100).all()
    return readings
