from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, auth, models
from app.deps import get_db, get_current_user
from app.utils import verify_password, hash_password

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already taken")
    user = crud.create_user(db, username=user_in.username, email=user_in.email, password=user_in.password)
    return user

@router.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # simple JSON-based login: username OR email in 'username' field + password
    user = crud.get_user_by_username(db, form_data.username) or crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    token = auth.create_access_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.post("/{username}/follow", status_code=201)
def follow(username: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    other = crud.get_user_by_username(db, username)
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    if other.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow self")
    if crud.is_blocked(db, current_user.id, other.id):
        raise HTTPException(status_code=403, detail="Cannot follow due to block")
    follow = crud.follow_user(db, follower=current_user, followed=other)
    if not follow:
        raise HTTPException(status_code=400, detail="Already following")
    return {"detail": "followed"}

@router.post("/{username}/unfollow", status_code=200)
def unfollow(username: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    other = crud.get_user_by_username(db, username)
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    crud.unfollow_user(db, follower=current_user, followed=other)
    return {"detail": "unfollowed"}

@router.post("/{username}/block", status_code=201)
def block(username: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    other = crud.get_user_by_username(db, username)
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    if other.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot block self")
    b = crud.block_user(db, blocker=current_user, blocked=other)
    if not b:
        raise HTTPException(status_code=400, detail="Already blocked")
    return {"detail": "blocked"}

@router.post("/{username}/unblock", status_code=200)
def unblock(username: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    other = crud.get_user_by_username(db, username)
    if not other:
        raise HTTPException(status_code=404, detail="User not found")
    crud.unblock_user(db, blocker=current_user, blocked=other)
    return {"detail": "unblocked"}
