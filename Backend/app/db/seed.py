import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.domain import Base, Grower, Farm, HydroponicSystem, Plant, Sensor, SensorReading, Alert
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)
LEGACY_DEMO_PLANT_IDS = (
    "plant-1",
    "plant-2",
    "plant-3",
    "plant-ac0e2912",
    "plant-c4a7005f",
    "plant-b4446894",
    "plant-355a6028",
    "plant-0afeffc1",
    "plant-f2debd1f",
)

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if grower exists
        grower = db.query(Grower).filter(Grower.email == "rajesh.kumar@smartagri.org").first()
        if not grower:
            logger.info("Seeding initial data into database...")
            grower = Grower(
                id="grower-1",
                name="Dr. Rajesh Kumar",
                email="rajesh.kumar@smartagri.org",
                hashed_password=get_password_hash("password123"),
                address="Plot 42, Agritech Innovation Hub, Sector 18",
                state="Karnataka",
                country="India",
                pincode="560100",
                member_since="2024",
                farm_type="Smart Hydroponics & IoT Greenhouse"
            )
            db.add(grower)
            db.flush()

            # Seed Farm
            farm = Farm(
                id="farm-1",
                grower_id=grower.id,
                name="Greenhouse Alpha",
                location="Agritech Hub, Sector 18",
                description="Primary IoT Automated Hydroponic Greenhouse"
            )
            db.add(farm)
            db.flush()

            # Seed Systems
            sys1 = HydroponicSystem(
                id="sys-1",
                farm_id=farm.id,
                grower_id=grower.id,
                name="NFT Channel System A",
                system_type="Nutrient Film Technique (NFT)",
                capacity=100
            )
            sys2 = HydroponicSystem(
                id="sys-2",
                farm_id=farm.id,
                grower_id=grower.id,
                name="Vertical Aeroponic Tower B",
                system_type="Vertical Tower Aeroponics",
                capacity=60
            )
            db.add_all([sys1, sys2])
            db.flush()

            # Seed Plants
            plants_data = [
                {
                    "id": "plant-1",
                    "system_id": sys1.id,
                    "name": "Hydroponic Roma Tomato",
                    "species": "Tomato (Solanum lycopersicum)",
                    "location": "Greenhouse Alpha - Bay 1",
                    "image": "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=800&q=80",
                    "status": "Healthy",
                    "temp": 24.2,
                    "ph": 6.3,
                    "humidity": 68.0,
                    "water": 85.0,
                    "notes": "Optimal nutrient intake. High fruit yield anticipated.",
                    "sensors": {
                        "temperature": ("BLE-TEMP-089A", True, 92),
                        "ph": ("I2C-PH-401X", True, 88),
                        "waterLevel": ("ADC-WTR-202B", True, 15),
                        "humidity": ("BLE-HUM-011C", True, 94)
                    }
                },
                {
                    "id": "plant-2",
                    "system_id": sys1.id,
                    "name": "Red Bell Pepper Batch",
                    "species": "Bell Pepper (Capsicum annuum)",
                    "location": "Greenhouse Alpha - Bay 3",
                    "image": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=800&q=80",
                    "status": "Needs Attention",
                    "temp": 31.8,
                    "ph": 5.1,
                    "humidity": 78.0,
                    "water": 32.0,
                    "notes": "Temperature rising. Water level sensor disconnected. Requires pH adjustment.",
                    "sensors": {
                        "temperature": ("BLE-TEMP-112B", True, 74),
                        "ph": ("I2C-PH-109Z", True, 65),
                        "waterLevel": ("ADC-WTR-999X", False, 0),
                        "humidity": ("BLE-HUM-304D", True, 81)
                    }
                },
                {
                    "id": "plant-3",
                    "system_id": sys2.id,
                    "name": "Crisp Butterhead Lettuce",
                    "species": "Lettuce (Lactuca sativa)",
                    "location": "Vertical Farm Tower B",
                    "image": "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=800&q=80",
                    "status": "Healthy",
                    "temp": 21.5,
                    "ph": 6.0,
                    "humidity": 62.0,
                    "water": 94.0,
                    "notes": "Exemplary growth under LED spectrum lights.",
                    "sensors": {
                        "temperature": ("BLE-TEMP-887K", True, 96),
                        "ph": ("I2C-PH-554M", True, 91),
                        "waterLevel": ("ADC-WTR-331L", True, 89),
                        "humidity": ("BLE-HUM-220P", True, 93)
                    }
                }
            ]

            for pdata in ():
                plant = Plant(
                    id=pdata["id"],
                    grower_id=grower.id,
                    system_id=pdata["system_id"],
                    name=pdata["name"],
                    species=pdata["species"],
                    location=pdata["location"],
                    image=pdata["image"],
                    status=pdata["status"],
                    temperature=pdata["temp"],
                    ph=pdata["ph"],
                    humidity=pdata["humidity"],
                    water_level=pdata["water"],
                    notes=pdata["notes"]
                )
                db.add(plant)
                db.flush()

                # Add Sensors
                for stype, sinfo in pdata["sensors"].items():
                    addr, conn, batt = sinfo
                    sensor = Sensor(
                        plant_id=plant.id,
                        sensor_type=stype,
                        address=addr,
                        connected=conn,
                        battery=batt,
                        status_text="Connected and battery level good" if conn else "Not Connected"
                    )
                    db.add(sensor)
                    db.flush()

                    # Add initial reading
                    val = pdata["temp"] if stype == "temperature" else (pdata["ph"] if stype == "ph" else (pdata["humidity"] if stype == "humidity" else pdata["water"]))
                    unit = "°C" if stype == "temperature" else ("%" if stype in ["humidity", "waterLevel"] else "pH")
                    reading = SensorReading(
                        sensor_id=sensor.id,
                        plant_id=plant.id,
                        grower_id=grower.id,
                        sensor_type=stype,
                        value=val,
                        unit=unit
                    )
                    db.add(reading)

            # Seed Alerts
            alerts_data = [
                {
                    "id": "alert-2",
                    "plant_id": "plant-2",
                    "severity": "warning",
                    "type": "pH Acidic Level",
                    "title": "Water Acidic (pH 5.1)",
                    "description": "pH has dropped to 5.1 (Ideal Range: 5.8 - 6.5). Nutrient absorption is impaired.",
                    "remedy_text": "Add 15ml of Alkali Buffer (pH Up solution) to balance acidity back to ~6.2.",
                    "remedy_action": "ADD_ALKALI",
                    "timestamp": "35 minutes ago"
                },
                {
                    "id": "alert-4",
                    "plant_id": "plant-2",
                    "severity": "info",
                    "type": "Sensor Disconnected",
                    "title": "Water Level Sensor Disconnected",
                    "description": "Telemetry offline for address ADC-WTR-999X.",
                    "remedy_text": "Check physical sensor cable wiring or reconnect sensor module via My Plants setup.",
                    "remedy_action": "RECONNECT_SENSOR",
                    "timestamp": "2 hours ago"
                }
            ]

            for adata in ():
                alert = Alert(
                    id=adata["id"],
                    plant_id=adata["plant_id"],
                    grower_id=grower.id,
                    severity=adata["severity"],
                    type=adata["type"],
                    title=adata["title"],
                    description=adata["description"],
                    remedy_text=adata["remedy_text"],
                    remedy_action=adata["remedy_action"],
                    timestamp=adata["timestamp"]
                )
                db.add(alert)

            db.commit()
            logger.info("Database seeding completed successfully.")
            from app.db.exporter import export_readable_data
            export_readable_data(db)

        for plant in db.query(Plant).filter(Plant.id.in_(LEGACY_DEMO_PLANT_IDS)).all():
            db.delete(plant)
        db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
