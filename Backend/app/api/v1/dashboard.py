from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.domain import Farm, HydroponicSystem, Plant, Alert, Grower
from app.schemas.schemas import DashboardStats
from app.api.deps import get_current_grower

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_grower: Optional[Grower] = Depends(get_current_grower)
):
    if not current_grower:
        current_grower = db.query(Grower).first()

    farm_ids = [f.id for f in db.query(Farm).filter(Farm.grower_id == current_grower.id).all()]
    sys_ids = [s.id for s in db.query(HydroponicSystem).filter(HydroponicSystem.farm_id.in_(farm_ids)).all()] if farm_ids else []
    plant_query = db.query(Plant).filter(Plant.system_id.in_(sys_ids)) if sys_ids else db.query(Plant).filter(False)

    total_farms = len(farm_ids)
    total_systems = len(sys_ids)
    total_plants = plant_query.count()

    healthy_count = plant_query.filter(Plant.status == "Healthy").count() if total_plants > 0 else 0
    needs_att_count = plant_query.filter(Plant.status.in_(["Needs Attention", "Good"])).count() if total_plants > 0 else 0
    critical_count = plant_query.filter(Plant.status == "Critical").count() if total_plants > 0 else 0

    plant_ids = [p.id for p in plant_query.all()] if total_plants > 0 else []
    active_alerts = db.query(Alert).filter(Alert.plant_id.in_(plant_ids), Alert.resolved == False).count() if plant_ids else 0

    avg_temp = plant_query.with_entities(func.avg(Plant.temperature)).scalar() if total_plants > 0 else None
    avg_ph = plant_query.with_entities(func.avg(Plant.ph)).scalar() if total_plants > 0 else None
    avg_humidity = plant_query.with_entities(func.avg(Plant.humidity)).scalar() if total_plants > 0 else None
    avg_water = plant_query.with_entities(func.avg(Plant.water_level)).scalar() if total_plants > 0 else None

    return DashboardStats(
        totalFarms=total_farms,
        totalSystems=total_systems,
        totalPlants=total_plants,
        healthyCount=healthy_count,
        needsAttentionCount=needs_att_count,
        criticalCount=critical_count,
        activeAlertsCount=active_alerts,
        avgTemperature=round(float(avg_temp), 1) if avg_temp is not None else None,
        avgPh=round(float(avg_ph), 1) if avg_ph is not None else None,
        avgHumidity=round(float(avg_humidity), 1) if avg_humidity is not None else None,
        avgWaterLevel=round(float(avg_water), 1) if avg_water is not None else None,
    )
