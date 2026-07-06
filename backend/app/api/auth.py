from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.database_models import User, Session as SessionModel
from backend.app.core.security import get_password_hash, verify_password
import uuid
from datetime import datetime

router = APIRouter()

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    location_address: str | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    preferred_language: str | None = None
    family_members: list | None = None
    medical_conditions: str | None = None
    emergency_contacts: list | None = None

    model_config = {
        "from_attributes": True
    }

class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    location_address: str | None = None
    location_lat: float | None = None
    location_lng: float | None = None
    medical_conditions: str | None = None
    family_members: list | None = None
    emergency_contacts: list | None = None

@router.post("/auth/signup", response_model=UserOut)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        full_name=payload.full_name,
        role="citizen"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = str(uuid.uuid4())
    session = SessionModel(user_id=user.id, token=token, created_at=datetime.utcnow())
    db.add(session)
    db.commit()
    return TokenResponse(access_token=token)

@router.post("/auth/logout")
def logout(authorization: str | None = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.split(" ")[-1]
    session = db.query(SessionModel).filter(SessionModel.token == token).first()
    if session:
        db.delete(session)
        db.commit()
    return {"status": "logged_out"}

# Helper dependency to get current user from token
def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = authorization.split(" ")[-1]
    session = db.query(SessionModel).filter(SessionModel.token == token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/auth/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.put("/auth/profile", response_model=UserOut)
def update_profile(payload: ProfileUpdateRequest, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.full_name is not None:
        current.full_name = payload.full_name
    if payload.location_address is not None:
        current.location_address = payload.location_address
    if payload.location_lat is not None:
        current.location_lat = payload.location_lat
    if payload.location_lng is not None:
        current.location_lng = payload.location_lng
    if payload.medical_conditions is not None:
        current.medical_conditions = payload.medical_conditions
    if payload.family_members is not None:
        current.family_members = payload.family_members
    if payload.emergency_contacts is not None:
        current.emergency_contacts = payload.emergency_contacts
    db.commit()
    db.refresh(current)
    return current

