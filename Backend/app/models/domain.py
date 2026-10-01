import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Grower(Base):
    __tablename__ = "growers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    member_since = Column(String, default="2024")
    farm_type = Column(String, default="Smart Hydroponics & IoT Greenhouse")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    farms = relationship("Farm", back_populates="grower", cascade="all, delete-orphan")
    plants = relationship("Plant", back_populates="grower", cascade="all, delete-orphan")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String, primary_key=True, default=lambda: f"farm-{uuid.uuid4().hex[:8]}")
    grower_id = Column(String, ForeignKey("growers.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    grower = relationship("Grower", back_populates="farms")
    systems = relationship("HydroponicSystem", back_populates="farm", cascade="all, delete-orphan")


class HydroponicSystem(Base):
    __tablename__ = "hydroponic_systems"

    id = Column(String, primary_key=True, default=lambda: f"sys-{uuid.uuid4().hex[:8]}")
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    grower_id = Column(String, ForeignKey("growers.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    system_type = Column(String, default="NFT Hydroponic Bay")
    capacity = Column(Integer, default=50)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    farm = relationship("Farm", back_populates="systems")
    plants = relationship("Plant", back_populates="system", cascade="all, delete-orphan")


class Plant(Base):
    __tablename__ = "plants"

    id = Column(String, primary_key=True, default=lambda: f"plant-{uuid.uuid4().hex[:8]}")
    grower_id = Column(String, ForeignKey("growers.id"), nullable=False, index=True)
    system_id = Column(String, ForeignKey("hydroponic_systems.id"), nullable=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    location = Column(String, nullable=True)
    image = Column(Text, nullable=True)
    status = Column(String, default="Waiting for data")
    notes = Column(Text, nullable=True)
    
    # Current Metrics
    temperature = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    water_level = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    grower = relationship("Grower", back_populates="plants")
    system = relationship("HydroponicSystem", back_populates="plants")
    sensors = relationship("Sensor", back_populates="plant", cascade="all, delete-orphan")
    readings = relationship("SensorReading", back_populates="plant", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="plant", cascade="all, delete-orphan")
    server_connection = relationship("PlantServerConnection", back_populates="plant", uselist=False, cascade="all, delete-orphan")


class PlantServerConnection(Base):
    __tablename__ = "plant_server_connections"

    id = Column(String, primary_key=True, default=lambda: f"server-{uuid.uuid4().hex[:8]}")
    plant_id = Column(String, ForeignKey("plants.id"), nullable=False, unique=True, index=True)
    server_ip = Column(String, nullable=False)
    source_url = Column(Text, nullable=False)
    raw_csv_path = Column(Text, nullable=False)
    cleaned_csv_path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plant = relationship("Plant", back_populates="server_connection")


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(String, primary_key=True, default=lambda: f"sensor-{uuid.uuid4().hex[:8]}")
    plant_id = Column(String, ForeignKey("plants.id"), nullable=False)
    sensor_type = Column(String, nullable=False)
    address = Column(String, nullable=False)
    connected = Column(Boolean, default=True)
    battery = Column(Integer, default=90)
    status_text = Column(String, default="Connected and battery level good")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plant = relationship("Plant", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(String, primary_key=True, default=lambda: f"reading-{uuid.uuid4().hex[:8]}")
    sensor_id = Column(String, ForeignKey("sensors.id"), nullable=True)
    plant_id = Column(String, ForeignKey("plants.id"), nullable=False)
    grower_id = Column(String, ForeignKey("growers.id"), nullable=False, index=True)
    sensor_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    extra_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sensor = relationship("Sensor", back_populates="readings")
    plant = relationship("Plant", back_populates="readings")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=lambda: f"alert-{uuid.uuid4().hex[:8]}")
    plant_id = Column(String, ForeignKey("plants.id"), nullable=False)
    grower_id = Column(String, ForeignKey("growers.id"), nullable=False, index=True)
    severity = Column(String, default="warning")
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    remedy_text = Column(Text, nullable=False)
    remedy_action = Column(String, nullable=False)
    timestamp = Column(String, default="Just now")
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plant = relationship("Plant", back_populates="alerts")
