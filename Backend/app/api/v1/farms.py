from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Farm, Grower
from app.schemas.schemas import FarmCreate, FarmUpdate, FarmResponse
from app.api.deps import get_current_grower

router = APIRouter(prefix="/farms", tags=["farms"])

@router.get("", response_model=List[FarmResponse])
def get_farms(
    db: Session = Depends(get_db),
    current_grower: Grower = Depends(get_current_grower)
):
    if current_grower:
        return db.query(Farm).filter(Farm.grower_id == current_grower.id).all()
    return db.query(Farm).all()

@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_in: FarmCreate,
    db: Session = Depends(get_db),
    current_grower: Grower = Depends(get_current_grower)
):
    grower_id = current_grower.id if current_grower else db.query(Grower).first().id
    farm = Farm(
        grower_id=grower_id,
        name=farm_in.name,
        location=farm_in.location,
        description=farm_in.description
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm

@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(farm_id: str, farm_in: FarmUpdate, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if farm_in.name is not None:
        farm.name = farm_in.name
    if farm_in.location is not None:
        farm.location = farm_in.location
    if farm_in.description is not None:
        farm.description = farm_in.description
    db.commit()
    db.refresh(farm)
    return farm

@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(farm_id: str, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    db.delete(farm)
    db.commit()
    return None
