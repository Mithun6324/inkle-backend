from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud, models
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.post("/", response_model=schemas.PostOut)
def create_post(payload: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.create_post(db, owner=current_user, content=payload.content)
    return post

@router.get("/{post_id}", response_model=schemas.PostOut)
def get_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id)
    if not post or post.deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    if crud.is_blocked(db, current_user.id, post.owner_id):
        raise HTTPException(status_code=403, detail="You cannot view this post due to block")
    return post

@router.post("/{post_id}/like", status_code=201)
def like(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id)
    if not post or post.deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    if crud.is_blocked(db, current_user.id, post.owner_id):
        raise HTTPException(status_code=403, detail="Cannot like due to block")
    like = crud.like_post(db, user=current_user, post=post)
    if not like:
        raise HTTPException(status_code=400, detail="Already liked")
    return {"detail": "liked"}

@router.post("/{post_id}/unlike", status_code=200)
def unlike(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    crud.unlike_post(db, user=current_user, post=post)
    return {"detail": "unliked"}

@router.get("/", response_model=list[schemas.PostOut])
def feed(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    posts = crud.get_posts_for_user(db, viewer=current_user, limit=100)
    return posts
