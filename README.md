# Todos List API

A RESTful API for managing a personal to-do list, with user registration, login, and JWT-based authentication. Each user only sees and manages their own tasks.

## Overview

Built with FastAPI and SQLAlchemy, using SQLite for storage. Passwords are hashed with bcrypt, and routes are protected using OAuth2 password flow with JWT bearer tokens.

## Tech Stack

- Python
- FastAPI
- SQLAlchemy (SQLite)
- Passlib (bcrypt password hashing)
- python-jose (JWT tokens)

## Project Structure

```
todos_list_api/
├── main.py            # API routes, auth logic, app entry point
├── database.py        # SQLAlchemy models and DB session setup
├── requirements.txt
└── .gitignore
```

## Endpoints

| Method | Endpoint       | Auth required | Description                     |
|--------|----------------|----------------|----------------------------------|
| POST   | /registration  | No             | Create a new user account        |
| POST   | /login         | No             | Log in, returns a JWT access token |
| GET    | /todos         | Yes            | List your todos (supports `skip`, `limit`, `completed` filters) |
| POST   | /todos         | Yes            | Create a new todo                |
| PUT    | /todos/{id}    | Yes            | Update a todo you own            |
| DELETE | /todos/{id}    | Yes            | Delete a todo you own            |

Authenticated routes expect an `Authorization: Bearer <token>` header, using the token returned from `/login`.

## How to Run Locally

```bash
# clone the repo
git clone https://github.com/cezium55/todos_list_api.git
cd todos_list_api

# create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# set the JWT signing key (required — the app will not start without it)
export SECRET_KEY="your-own-secret-key"   # Windows: set SECRET_KEY=your-own-secret-key

# run the app
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## Author

Garvit Gaur
New Delhi, India
GitHub: https://github.com/cezium55
LinkedIn: https://linkedin.com/in/garvit-gaur-81507525b
