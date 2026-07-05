from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.core.database import get_db
from backend.app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from backend.app.models.database_models import User
from backend.app.schemas.schemas import UserSignup, UserLogin, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional), db: Session = Depends(get_db)) -> Optional[User]:
    """Returns the current user if authenticated, or None for anonymous requests."""
    if credentials is None:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return None
    email: str = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    return user

@router.post("/signup", response_model=UserOut)
def signup(user_in: UserSignup, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role,
        location_address=user_in.location_address,
        location_lat=user_in.location_lat,
        location_lng=user_in.location_lng,
        preferred_language=user_in.preferred_language,
        family_members=user_in.family_members,
        medical_conditions=user_in.medical_conditions,
        emergency_contacts=user_in.emergency_contacts
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
