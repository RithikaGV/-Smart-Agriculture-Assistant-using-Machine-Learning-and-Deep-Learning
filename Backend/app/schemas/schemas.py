from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# --- AUTH & GROWER SCHEMAS ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class GrowerSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: Optional[str] = "Plot 42, Agritech Innovation Hub"
    state: Optional[str] = "Karnataka"
    country: Optional[str] = "India"
    pincode: Optional[str] = "560100"
    farmType: Optional[str] = "Smart Hydroponics & IoT Greenhouse"

class GrowerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    farmType: Optional[str] = None

class GrowerResponse(BaseModel):
    id: str
    name: str
    email: str
    address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    memberSince: Optional[str] = "2024"
    farmType: Optional[str] = "Smart Hydroponics & IoT Greenhouse"

    class Config:
        from_attributes = True

# --- FARM SCHEMAS ---

class FarmCreate(BaseModel):
    name: str
    location: Optional[str] = "Greenhouse Alpha"
    description: Optional[str] = "Primary Automated Hydroponic Greenhouse"

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class FarmResponse(BaseModel):
    id: str
    grower_id: str
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- HYDROPONIC SYSTEM SCHEMAS ---

class SystemCreate(BaseModel):
    farm_id: str
    name: str
    system_type: Optional[str] = "NFT Hydroponic Bay"
    capacity: Optional[int] = 50

class SystemUpdate(BaseModel):
    name: Optional[str] = None
    system_type: Optional[str] = None
    capacity: Optional[int] = None

class SystemResponse(BaseModel):
    id: str
    farm_id: str
    name: str
    system_type: str
    capacity: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- SENSOR SCHEMAS ---

class SensorDetail(BaseModel):
    connected: bool = True
    battery: int = 90
    address: str
    statusText: Optional[str] = "Connected and battery level good"

class SensorsConfig(BaseModel):
    temperature: Optional[SensorDetail] = None
    ph: Optional[SensorDetail] = None
    waterLevel: Optional[SensorDetail] = None
    humidity: Optional[SensorDetail] = None
    extra_sensors: Optional[Dict[str, SensorDetail]] = None

class SensorConnectRequest(BaseModel):
    plant_id: str
    sensor_type: str  # e.g., temperature, ph, waterLevel, humidity, ec, co2
    address: str

class SensorReadingIngest(BaseModel):
    plant_id: str
    sensor_address: Optional[str] = None
    sensor_type: str  # e.g. temperature, ph, waterLevel, humidity, or custom
    value: float
    unit: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None

class SensorReadingResponse(BaseModel):
    id: str
    plant_id: str
    sensor_type: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# --- PLANT SCHEMAS ---

class PlantMetrics(BaseModel):
    temperature: float = 24.0
    ph: float = 6.2
    humidity: float = 65.0
    waterLevel: float = 90.0

class GrowthHistoryItem(BaseModel):
    day: str
    heightCm: float
    ph: float
    temp: float
    humidity: float
    water: float

class PlantCreate(BaseModel):
    system_id: Optional[str] = None
    name: str
    species: str
    location: Optional[str] = "Greenhouse Alpha - Bay 1"
    image: Optional[str] = None
    notes: Optional[str] = "Newly added hydroponic crop"
    sensors: Optional[Dict[str, Any]] = None

class PlantUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    location: Optional[str] = None
    image: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    metrics: Optional[PlantMetrics] = None
    sensors: Optional[Dict[str, Any]] = None

class PlantResponse(BaseModel):
    id: str
    system_id: Optional[str] = None
    name: str
    species: str
    location: Optional[str] = None
    image: Optional[str] = None
    status: str
    metrics: PlantMetrics
    sensors: Dict[str, Any]
    growthHistory: List[GrowthHistoryItem] = []
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- ALERT SCHEMAS ---

class AlertResponse(BaseModel):
    id: str
    plantId: str
    plantName: str
    severity: str
    type: str
    title: str
    description: str
    remedyText: str
    remedyAction: str
    timestamp: str
    resolved: bool = False

    class Config:
        from_attributes = True

class RemedyRequest(BaseModel):
    alert_id: str

# --- DASHBOARD SCHEMAS ---

class DashboardStats(BaseModel):
    totalFarms: int
    totalSystems: int
    totalPlants: int
    healthyCount: int
    needsAttentionCount: int
    criticalCount: int
    activeAlertsCount: int
    avgTemperature: float
    avgPh: float
    avgHumidity: float
    avgWaterLevel: float

# --- ML PREDICTION SCHEMAS ---

class DiseasePredictionRequest(BaseModel):
    image_url: Optional[str] = None

class DiseasePredictionResponse(BaseModel):
    name: str
    scientificName: str
    confidence: float
    cause: str
    preventiveMeasures: List[str]
    plantType: Optional[str] = "Hydroponic Crop"
