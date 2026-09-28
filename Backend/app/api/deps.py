from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.domain import Grower

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_current_grower(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[Grower]:
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        grower_id: str = payload.get("sub")
        if not grower_id:
            return None
        grower = db.query(Grower).filter(Grower.id == grower_id).first()
        return grower
    except JWTError:
        return None

def require_current_grower(
    grower: Optional[Grower] = Depends(get_current_grower)
) -> Grower:
    if not grower:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to access grower data"
        )
    return grower
