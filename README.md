# Inkle Social Activity Feed Backend

This repository contains the backend implementation for the Inkle Social Activity Feed assignment.  
The project is built with FastAPI and PostgreSQL and includes user authentication, posting, following, blocking, activity feeds, and admin controls.

## Features

1. User authentication with JWT
2. User signup and login
3. Follow and unfollow users
4. Block and unblock users
5. Create and manage posts
6. Like and unlike posts
7. Global activity feed
8. Admin functionalities
9. Owner-level controls for promoting and removing admins

## Technology Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn
- Passlib (bcrypt)
- Python-Jose (JWT)

## Project Structure

inkle-backend/
app/
main.py
database.py
models.py
schemas.py
crud.py
auth.py
utils.py
deps.py
routers/
users.py
posts.py
admin.py
activities.py
requirements.txt
postman_collection.json
.env (to be created by user)

## Environment Variables

Create a .env file in the root folder:

DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/inkle_db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=1440

## Database Setup

Create the PostgreSQL database:

CREATE DATABASE inkle_db;

## Running the Server

Install dependencies:

pip install -r requirements.txt

Start the FastAPI server:

uvicorn app.main:app --reload

Access the API documentation:

http://127.0.0.1:8000/docs

## Authentication

This project uses JWT based authentication.

Login returns:

{
  "access_token": "token",
  "token_type": "bearer"
}

Send this token in all protected routes:

Authorization: Bearer your_token

## API Endpoints

### User Endpoints
POST /api/users/signup  
POST /api/users/login  
GET /api/users/me  
POST /api/users/{username}/follow  
POST /api/users/{username}/unfollow  
POST /api/users/{username}/block  
POST /api/users/{username}/unblock  

### Post Endpoints
GET /api/posts/  
POST /api/posts/  
GET /api/posts/{post_id}  
POST /api/posts/{post_id}/like  
POST /api/posts/{post_id}/unlike  

### Admin Endpoints
DELETE /api/admin/posts/{post_id}  
DELETE /api/admin/users/{username}  
POST /api/admin/owners/create-admin/{username}  
DELETE /api/admin/owners/remove-admin/{username}  

### Activity Feed
GET /api/activities/global  

## Postman Collection

A ready-to-use Postman collection is included in the file:

postman_collection.json

Import the file into Postman to test all endpoints.

## Deployment

1. Push the repository to GitHub.
2. Deploy to Railway.
3. Add PostgreSQL as a Railway service.
4. Add the following environment variables inside Railway:
   - DATABASE_URL
   - SECRET_KEY
   - ACCESS_TOKEN_EXPIRE_MINUTES
5. Start command for Railway:
   uvicorn app.main:app --host 0.0.0.0 --port 8000

## Author

Mithun SP  
GitHub: https://github.com/Mithun6324
