from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, crud
from app.deps import get_db, require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])

def admin_required(user: models.User = Depends(require_role(models.RoleEnum.admin))):
    return user

@router.delete("/posts/{post_id}")
def admin_delete_post(post_id: int, db: Session = Depends(get_db), admin_user: models.User = Depends(admin_required)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    crud.delete_post(db, post, actor_id=admin_user.id)
    return {"detail": "post marked deleted"}

@router.delete("/users/{username}")
def admin_delete_user(username: str, db: Session = Depends(get_db), admin_user: models.User = Depends(admin_required)):
    target = crud.get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role == models.RoleEnum.owner and admin_user.role != models.RoleEnum.owner:
        raise HTTPException(status_code=403, detail="Cannot delete owner")
    crud.delete_user(db, target)
    activity = models.Activity(actor_id=admin_user.id, verb=models.ActivityType.delete_user, target_user_id=target.id)
    db.add(activity); db.commit()
    return {"detail": "user deleted"}

@router.post("/owners/create-admin/{username}")
def owner_create_admin(username: str, db: Session = Depends(get_db), owner: models.User = Depends(require_role(models.RoleEnum.owner))):
    target = crud.get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.role = models.RoleEnum.admin
    db.add(target)
    db.commit()
    return {"detail": f"{username} promoted to admin"}

@router.delete("/owners/remove-admin/{username}")
def owner_remove_admin(username: str, db: Session = Depends(get_db), owner: models.User = Depends(require_role(models.RoleEnum.owner))):
    target = crud.get_user_by_username(db, username)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role != models.RoleEnum.admin:
        raise HTTPException(status_code=400, detail="User is not an admin")
    target.role = models.RoleEnum.user
    db.add(target)
    db.commit()
    return {"detail": f"{username} demoted from admin"}
