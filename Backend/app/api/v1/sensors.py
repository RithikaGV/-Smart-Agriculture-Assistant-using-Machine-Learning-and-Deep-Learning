from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Sensor, SensorReading, Plant, Alert, PlantServerConnection
from app.schemas.schemas import SensorConnectRequest, SensorReadingIngest, SensorReadingResponse

router = APIRouter(prefix="/sensors", tags=["sensors"])

METRIC_ALERT_RULES = (
    {
        "attribute": "temperature",
        "type": "Temperature",
        "label": "Temperature",
        "unit": "°C",
        "healthy_min": 18.0,
        "healthy_max": 26.0,
        "critical_min": 15.0,
        "critical_max": 30.0,
        "legacy_types": ("Temperature & Water Level",),
        "remedies": {
            "low": ("Raise the grow-area temperature and check airflow.", "ADJUST_TEMPERATURE"),
            "high": ("Increase cooling and airflow around the plant.", "ADJUST_TEMPERATURE"),
        },
    },
    {
        "attribute": "ph",
        "type": "pH",
        "label": "Water pH",
        "unit": "",
        "healthy_min": 5.5,
        "healthy_max": 6.5,
        "critical_min": 5.0,
        "critical_max": 7.0,
        "legacy_types": ("pH Acidic Level",),
        "remedies": {
            "low": ("Add pH Up in small measured doses and retest.", "ADD_ALKALI"),
            "high": ("Add pH Down in small measured doses and retest.", "ADD_ACID"),
        },
    },
    {
        "attribute": "humidity",
        "type": "Humidity",
        "label": "Humidity",
        "unit": "%",
        "healthy_min": 50.0,
        "healthy_max": 70.0,
        "critical_min": 40.0,
        "critical_max": 80.0,
        "legacy_types": ("Humidity Risk",),
        "remedies": {
            "low": ("Increase humidification and check ventilation settings.", "ACTIVATE_HUMIDIFIER"),
            "high": ("Improve ventilation or activate dehumidification.", "ACTIVATE_DEHUMIDIFIER"),
        },
    },
    {
        "attribute": "water_level",
        "type": "Water Level",
        "label": "Water level",
        "unit": "%",
        "healthy_min": 40.0,
        "healthy_max": 100.0,
        "critical_min": 20.0,
        "critical_max": 100.0,
        "remedies": {
            "low": ("Refill the reservoir and verify the pump is operating.", "REFILL_RESERVOIR"),
            "high": ("Check the reservoir level and recalibrate its sensor.", "CHECK_WATER_SENSOR"),
        },
    },
)


def _metric_severity(value: Optional[float], rule: dict) -> Optional[str]:
    if value is None:
        return None
    if value < rule["critical_min"] or value > rule["critical_max"]:
        return "critical"
    if value < rule["healthy_min"] or value > rule["healthy_max"]:
        return "warning"
    return None


def _sync_metric_alert(plant: Plant, db: Session, rule: dict, severity: Optional[str]) -> None:
    alert_types = (rule["type"], *rule.get("legacy_types", ()))
    existing_alerts = (
        db.query(Alert)
        .filter(
            Alert.plant_id == plant.id,
            Alert.resolved == False,
            Alert.type.in_(alert_types),
        )
        .all()
    )

    if severity is None:
        for alert in existing_alerts:
            alert.resolved = True
        return

    value = getattr(plant, rule["attribute"])
    direction = "low" if value < rule["healthy_min"] else "high"
    remedy_text, remedy_action = rule["remedies"][direction]
    healthy_range = f"{rule['healthy_min']:g}-{rule['healthy_max']:g}{rule['unit']}"
    title = f"{'Critical' if severity == 'critical' else 'Warning'}: {rule['label']} {direction} ({value:g}{rule['unit']})"
    description = f"{rule['label']} is {value:g}{rule['unit']}; the healthy range is {healthy_range}."

    if existing_alerts:
        alert = existing_alerts[0]
        for duplicate in existing_alerts[1:]:
            duplicate.resolved = True
    else:
        alert = Alert(plant_id=plant.id, grower_id=plant.grower_id)
        db.add(alert)

    alert.severity = severity
    alert.type = rule["type"]
    alert.title = title
    alert.description = description
    alert.remedy_text = remedy_text
    alert.remedy_action = remedy_action
    alert.timestamp = "Just now"


def check_and_create_alerts(plant: Plant, db: Session):
    severities = []
    for rule in METRIC_ALERT_RULES:
        severity = _metric_severity(getattr(plant, rule["attribute"]), rule)
        _sync_metric_alert(plant, db, rule, severity)
        if severity:
            severities.append(severity)

    if "critical" in severities:
        plant.status = "Critical"
    elif severities:
        plant.status = "Needs Attention"
    elif any(getattr(plant, rule["attribute"]) is not None for rule in METRIC_ALERT_RULES):
        plant.status = "Healthy"
    else:
        plant.status = "Waiting for data"

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
    if reading.plant_id:
        plant = db.query(Plant).filter(Plant.id == reading.plant_id).first()
    elif reading.server_url:
        connections = db.query(PlantServerConnection).filter(
            PlantServerConnection.source_url == reading.server_url
        ).all()
        if len(connections) > 1:
            raise HTTPException(
                status_code=409,
                detail="This server is assigned to multiple plants; use the app-managed collector.",
            )
        plant = db.query(Plant).filter(Plant.id == connections[0].plant_id).first() if connections else None
    else:
        raise HTTPException(status_code=400, detail="Provide a plant ID or a registered server URL.")

    if not plant:
        raise HTTPException(status_code=404, detail="No plant is registered with this ID or server URL.")

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

    stype = reading.sensor_type.strip().lower()
    if stype in ["temperature", "temp", "dht_temp"]:
        plant.temperature = reading.value
    elif stype == "ph":
        plant.ph = reading.value
    elif stype in ["humidity", "dht_humidity"]:
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
