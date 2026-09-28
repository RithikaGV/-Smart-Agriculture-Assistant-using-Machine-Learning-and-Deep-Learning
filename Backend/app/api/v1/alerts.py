from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Alert, Plant, Sensor, Grower, Farm, HydroponicSystem
from app.schemas.schemas import AlertResponse
from app.api.deps import get_current_grower

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    current_grower: Optional[Grower] = Depends(get_current_grower)
):
    if not current_grower:
        current_grower = db.query(Grower).first()

    farm_ids = [f.id for f in db.query(Farm).filter(Farm.grower_id == current_grower.id).all()]
    sys_ids = [s.id for s in db.query(HydroponicSystem).filter(HydroponicSystem.farm_id.in_(farm_ids)).all()] if farm_ids else []
    plant_ids = [p.id for p in db.query(Plant).filter(Plant.system_id.in_(sys_ids)).all()] if sys_ids else []

    alerts = db.query(Alert).filter(Alert.plant_id.in_(plant_ids), Alert.resolved == False).all() if plant_ids else []
    results = []
    for a in alerts:
        plant = db.query(Plant).filter(Plant.id == a.plant_id).first()
        plant_name = plant.name if plant else "Hydroponic Plant"
        results.append(AlertResponse(
            id=a.id,
            plantId=a.plant_id,
            plantName=plant_name,
            severity=a.severity,
            type=a.type,
            title=a.title,
            description=a.description,
            remedyText=a.remedy_text,
            remedyAction=a.remedy_action,
            timestamp=a.timestamp,
            resolved=a.resolved
        ))
    return results

@router.post("/{alert_id}/remedy")
def apply_remedy(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    plant = db.query(Plant).filter(Plant.id == alert.plant_id).first()
    if plant:
        action = alert.remedy_action
        if action == "COOLING_AND_REFILL":
            plant.temperature = 24.5
            plant.water_level = 88.0
            plant.status = "Healthy"
        elif action == "ADD_ALKALI":
            plant.ph = 6.2
            plant.status = "Healthy"
        elif action == "ACTIVATE_DEHUMIDIFIER":
            plant.humidity = 64.0
            plant.status = "Healthy"
        elif action == "RECONNECT_SENSOR":
            sensor = db.query(Sensor).filter(Sensor.plant_id == plant.id, Sensor.sensor_type == "waterLevel").first()
            if sensor:
                sensor.connected = True
                sensor.battery = 90
                sensor.status_text = "Connected and battery level good"

    alert.resolved = True
    db.commit()

    return {
        "status": "success",
        "message": f"Applied remedy '{alert.remedy_action}' for alert '{alert.title}'",
        "alert_id": alert.id,
        "resolved": True
    }
