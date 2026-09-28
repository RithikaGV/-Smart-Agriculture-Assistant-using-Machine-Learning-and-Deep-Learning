from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import HydroponicSystem, Farm
from app.schemas.schemas import SystemCreate, SystemUpdate, SystemResponse

router = APIRouter(prefix="/systems", tags=["systems"])

@router.get("", response_model=List[SystemResponse])
def get_systems(farm_id: Optional[str] = None, db: Session = Depends(get_db)):
    if farm_id:
        return db.query(HydroponicSystem).filter(HydroponicSystem.farm_id == farm_id).all()
    return db.query(HydroponicSystem).all()

@router.post("", response_model=SystemResponse, status_code=status.HTTP_201_CREATED)
def create_system(sys_in: SystemCreate, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == sys_in.farm_id).first()
    if not farm:
        # Fallback to first farm or create default farm if database is fresh
        farm = db.query(Farm).first()
        if not farm:
            raise HTTPException(status_code=404, detail="Parent Farm not found. Create a farm first.")
        sys_in.farm_id = farm.id

    sys_obj = HydroponicSystem(
        farm_id=sys_in.farm_id,
        name=sys_in.name,
        system_type=sys_in.system_type,
        capacity=sys_in.capacity
    )
    db.add(sys_obj)
    db.commit()
    db.refresh(sys_obj)
    return sys_obj

@router.get("/{system_id}", response_model=SystemResponse)
def get_system(system_id: str, db: Session = Depends(get_db)):
    sys_obj = db.query(HydroponicSystem).filter(HydroponicSystem.id == system_id).first()
    if not sys_obj:
        raise HTTPException(status_code=404, detail="Hydroponic system not found")
    return sys_obj

@router.put("/{system_id}", response_model=SystemResponse)
def update_system(system_id: str, sys_in: SystemUpdate, db: Session = Depends(get_db)):
    sys_obj = db.query(HydroponicSystem).filter(HydroponicSystem.id == system_id).first()
    if not sys_obj:
        raise HTTPException(status_code=404, detail="Hydroponic system not found")
    if sys_in.name is not None:
        sys_obj.name = sys_in.name
    if sys_in.system_type is not None:
        sys_obj.system_type = sys_in.system_type
    if sys_in.capacity is not None:
        sys_obj.capacity = sys_in.capacity
    db.commit()
    db.refresh(sys_obj)
    return sys_obj

@router.delete("/{system_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system(system_id: str, db: Session = Depends(get_db)):
    sys_obj = db.query(HydroponicSystem).filter(HydroponicSystem.id == system_id).first()
    if not sys_obj:
        raise HTTPException(status_code=404, detail="Hydroponic system not found")
    db.delete(sys_obj)
    db.commit()
    return None
