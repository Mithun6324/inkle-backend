from sqlalchemy.orm import Session
from . import models, utils
from typing import Optional

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, username: str, email: str, password: str, role: models.RoleEnum = models.RoleEnum.user) -> models.User:
    hashed = utils.hash_password(password)
    user = models.User(username=username, email=email, hashed_password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()

def create_post(db: Session, owner: models.User, content: str) -> models.Post:
    post = models.Post(content=content, owner=owner)
    db.add(post)
    db.commit()
    db.refresh(post)
    activity = models.Activity(actor_id=owner.id, verb=models.ActivityType.post, target_post_id=post.id)
    db.add(activity); db.commit()
    return post

def get_post(db: Session, post_id: int) -> Optional[models.Post]:
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def delete_post(db: Session, post: models.Post, actor_id: Optional[int] = None):
    post.deleted = True
    db.add(post)
    activity = models.Activity(actor_id=actor_id, verb=models.ActivityType.delete_post, target_post_id=post.id)
    db.add(activity)
    db.commit()

def like_post(db: Session, user: models.User, post: models.Post):
    from sqlalchemy.exc import IntegrityError
    like = models.Like(user=user, post=post)
    db.add(like)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(like)
    activity = models.Activity(actor_id=user.id, verb=models.ActivityType.like, target_post_id=post.id)
    db.add(activity); db.commit()
    return like

def unlike_post(db: Session, user: models.User, post: models.Post):
    like = db.query(models.Like).filter(models.Like.user_id==user.id, models.Like.post_id==post.id).first()
    if like:
        db.delete(like)
        db.commit()

def follow_user(db: Session, follower: models.User, followed: models.User):
    from sqlalchemy.exc import IntegrityError
    follow = models.Follow(follower=follower, followed=followed)
    db.add(follow)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(follow)
    activity = models.Activity(actor_id=follower.id, verb=models.ActivityType.follow, target_user_id=followed.id)
    db.add(activity); db.commit()
    return follow

def unfollow_user(db: Session, follower: models.User, followed: models.User):
    f = db.query(models.Follow).filter(models.Follow.follower_id==follower.id, models.Follow.followed_id==followed.id).first()
    if f:
        db.delete(f)
        db.commit()

def block_user(db: Session, blocker: models.User, blocked: models.User):
    from sqlalchemy.exc import IntegrityError
    b = models.Block(blocker=blocker, blocked=blocked)
    db.add(b)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(b)
    activity = models.Activity(actor_id=blocker.id, verb=models.ActivityType.block, target_user_id=blocked.id)
    db.add(activity); db.commit()
    return b

def unblock_user(db: Session, blocker: models.User, blocked: models.User):
    b = db.query(models.Block).filter(models.Block.blocker_id==blocker.id, models.Block.blocked_id==blocked.id).first()
    if b:
        db.delete(b)
        db.commit()

def get_global_activity(db: Session, limit: int = 50):
    return db.query(models.Activity).order_by(models.Activity.created_at.desc()).limit(limit).all()

def is_blocked(db: Session, viewer_id: int, owner_id: int) -> bool:
    blocked = db.query(models.Block).filter(
        (models.Block.blocker_id == viewer_id) & (models.Block.blocked_id == owner_id)
    ).first()
    blocked2 = db.query(models.Block).filter(
        (models.Block.blocker_id == owner_id) & (models.Block.blocked_id == viewer_id)
    ).first()
    return bool(blocked or blocked2)

def get_posts_for_user(db: Session, viewer: Optional[models.User], limit: int = 50):
    q = db.query(models.Post).filter(models.Post.deleted == False).order_by(models.Post.created_at.desc()).limit(limit)
    posts = []
    for post in q:
        if viewer:
            if is_blocked(db, viewer.id, post.owner_id):
                continue
        posts.append(post)
    return posts
