from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import schemas, crud
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/activities", tags=["activities"])

@router.get("/global", response_model=list[schemas.ActivityOut])
def global_activity(limit: int = 50, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    acts = crud.get_global_activity(db, limit=limit)
    return acts
