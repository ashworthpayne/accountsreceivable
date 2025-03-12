from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from auth import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"  # ✅ Default to "user"

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True  # ✅ Ensure Pydantic correctly maps this schema

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: str
    email: str
    password: str
    role: str

# ✅ Create a new user
@router.post("/register/")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    if user.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    return {"message": f"User '{user.username}' created successfully with role '{user.role}'"}

# ✅ Login and get JWT token
@router.post("/login/")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"🔹 Received login request: {user.username}")  # ✅ Debugging log

    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        print(f"❌ User not found: {user.username}")  # ✅ Debugging log
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(user.password, db_user.hashed_password):
        print(f"❌ Incorrect password for: {user.username}")  # ✅ Debugging log
        raise HTTPException(status_code=401, detail="Invalid username or password")

    print(f"✅ User authenticated: {user.username}")  # ✅ Debugging log
    access_token = create_access_token({"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Get the currently logged-in user
def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid authentication")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user  # ✅ Return the full user object, including role

# ✅ Get All Users (Admin Only)
@router.get("/users/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    return db.query(User).all()

# ✅ Add a New User (Admin Only)
@router.post("/users/")
def create_user(user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password, role=user.role)
    
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# ✅ Edit a User (Admin Only)
@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.email = user.email
    db_user.hashed_password = hash_password(user.password)
    db_user.role = user.role

    db.commit()
    return {"message": "User updated successfully"}

# ✅ Delete a User (Admin Only)
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}

