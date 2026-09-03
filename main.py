import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from database import SessionLocal, TodoDB, UserDB 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt 
from datetime import datetime, timedelta 
from typing import Optional

# 1. Configuration Constants
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2. Initialize App and Tools First
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 3. Pydantic Models
class UserCreate(BaseModel):
    username: str  
    password: str

class TodoItem(BaseModel):
    title: str
    completed: bool = False

# 4. Helper Functions & Dependencies
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

# 5. Authentication Routes
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()

    # Combined the checks for cleaner logic
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/registration")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(UserDB.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="username already taken")
    
    hashed_pw = pwd_context.hash(user.password)
    new_user = UserDB(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "user created successfully", "username": new_user.username}


# 6. Todo Routes (All safely locked down)
@app.post("/todos")
def create_todo(item: TodoItem, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    new_task = TodoDB(
        title=item.title, 
        completed=item.completed, 
        owner_id=current_user.id 
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task added!", "task": new_task}

@app.get("/todos")
def get_all_todos(
    skip: int = 0, 
    limit: int = 10, 
    completed: Optional[bool] = None, 
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    query = db.query(TodoDB).filter(TodoDB.owner_id == current_user.id)
    
    if completed is not None:
        query = query.filter(TodoDB.completed == completed)
        
    tasks = query.offset(skip).limit(limit).all()
    return {"tasks": tasks}

@app.put("/todos/{todo_id}")
def update_todo(
    todo_id: int, 
    item: TodoItem, 
    db: Session = Depends(get_db), 
    current_user: UserDB = Depends(get_current_user)
):
    db_task = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.owner_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    
    db_task.title = item.title
    db_task.completed = item.completed
    db.commit()
    db.refresh(db_task)
    return {"message": "Task updated!", "task": db_task}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_task = db.query(TodoDB).filter(TodoDB.id == todo_id, TodoDB.owner_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}
