from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import crud, auth, models

# Simple Bearer Token (NOT OAuth2)
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    # Extract token
    token = credentials.credentials

    # Decode JWT
    payload = auth.decode_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = crud.get_user(db, payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

def require_role(role: models.RoleEnum):
    def _require_role(current_user: models.User = Depends(get_current_user)):
        if current_user.role != role and current_user.role != models.RoleEnum.owner:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _require_role
