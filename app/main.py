from fastapi import FastAPI
from app.database import init_db
from app.routers import users, posts, admin, activities

app = FastAPI(title="Inkle - Social Activity Feed")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(admin.router)
app.include_router(activities.router)

@app.get("/")
def root():
    return {"msg": "inkle backend running. See /docs for interactive API."}
