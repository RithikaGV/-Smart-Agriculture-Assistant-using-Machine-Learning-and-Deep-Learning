from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Grower, Farm, HydroponicSystem, Plant
from app.schemas.schemas import GrowerSignup, LoginRequest, Token, GrowerResponse, GrowerUpdate
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_grower

router = APIRouter(prefix="/auth", tags=["auth"])

def create_default_grower_environment(grower: Grower, db: Session):
    # Check if grower already has farms
    existing_farm = db.query(Farm).filter(Farm.grower_id == grower.id).first()
    if not existing_farm:
        farm = Farm(
            grower_id=grower.id,
            name=f"{grower.name}'s Farm",
            location="Smart Greenhouse Bay 1",
            description="Automated Hydroponics & IoT Greenhouse"
        )
        db.add(farm)
        db.flush()

        sys_obj = HydroponicSystem(
            farm_id=farm.id,
            grower_id=grower.id,
            name="NFT System 1",
            system_type="Nutrient Film Technique",
            capacity=50
        )
        db.add(sys_obj)
        db.flush()

        # Seed initial starter plant for new grower
        plant = Plant(
            grower_id=grower.id,
            system_id=sys_obj.id,
            name=f"{grower.name.split()[0]}'s Hydroponic Crop",
            species="Tomato (Solanum lycopersicum)",
            location="Bay 1 - Tower A",
            status="Healthy",
            temperature=24.0,
            ph=6.2,
            humidity=65.0,
            water_level=90.0,
            notes="Initial crop initialized for new grower profile."
        )
        db.add(plant)
        db.commit()

@router.post("/signup", response_model=Token)
def signup(grower_in: GrowerSignup, db: Session = Depends(get_db)):
    existing = db.query(Grower).filter(Grower.email == grower_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
    
    grower = Grower(
        name=grower_in.name,
        email=grower_in.email,
        hashed_password=get_password_hash(grower_in.password),
        address=grower_in.address,
        state=grower_in.state,
        country=grower_in.country,
        pincode=grower_in.pincode,
        farm_type=grower_in.farmType
    )
    db.add(grower)
    db.commit()
    db.refresh(grower)

    create_default_grower_environment(grower, db)

    access_token = create_access_token(subject=grower.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": grower.id,
            "name": grower.name,
            "email": grower.email,
            "address": grower.address,
            "state": grower.state,
            "country": grower.country,
            "pincode": grower.pincode,
            "farmType": grower.farm_type,
            "memberSince": grower.member_since
        }
    }

@router.post("/login", response_model=Token)
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    grower = db.query(Grower).filter(Grower.email == login_in.email).first()
    
    if not grower:
        # Create a separate new account for this new email address
        name_parts = login_in.email.split("@")[0].replace(".", " ").title()
        grower = Grower(
            name=f"Grower {name_parts}",
            email=login_in.email,
            hashed_password=get_password_hash(login_in.password),
            address="Agritech Innovation Hub",
            state="State Center",
            country="India",
            pincode="560100"
        )
        db.add(grower)
        db.commit()
        db.refresh(grower)
        create_default_grower_environment(grower, db)
    elif not verify_password(login_in.password, grower.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password for this email"
        )

    access_token = create_access_token(subject=grower.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": grower.id,
            "name": grower.name,
            "email": grower.email,
            "address": grower.address,
            "state": grower.state,
            "country": grower.country,
            "pincode": grower.pincode,
            "farmType": grower.farm_type,
            "memberSince": grower.member_since
        }
    }

@router.get("/me", response_model=GrowerResponse)
def get_me(current_grower: Grower = Depends(get_current_grower)):
    if not current_grower:
        raise HTTPException(status_code=404, detail="Grower profile not found")
    return GrowerResponse(
        id=current_grower.id,
        name=current_grower.name,
        email=current_grower.email,
        address=current_grower.address,
        state=current_grower.state,
        country=current_grower.country,
        pincode=current_grower.pincode,
        memberSince=current_grower.member_since,
        farmType=current_grower.farm_type
    )

@router.put("/me", response_model=GrowerResponse)
def update_me(
    profile_in: GrowerUpdate,
    db: Session = Depends(get_db),
    current_grower: Grower = Depends(get_current_grower)
):
    if not current_grower:
        raise HTTPException(status_code=404, detail="Grower profile not found")

    if profile_in.name is not None:
        current_grower.name = profile_in.name
    if profile_in.email is not None:
        current_grower.email = profile_in.email
    if profile_in.address is not None:
        current_grower.address = profile_in.address
    if profile_in.state is not None:
        current_grower.state = profile_in.state
    if profile_in.country is not None:
        current_grower.country = profile_in.country
    if profile_in.pincode is not None:
        current_grower.pincode = profile_in.pincode
    if profile_in.farmType is not None:
        current_grower.farm_type = profile_in.farmType

    db.commit()
    db.refresh(current_grower)

    return GrowerResponse(
        id=current_grower.id,
        name=current_grower.name,
        email=current_grower.email,
        address=current_grower.address,
        state=current_grower.state,
        country=current_grower.country,
        pincode=current_grower.pincode,
        memberSince=current_grower.member_since,
        farmType=current_grower.farm_type
    )
