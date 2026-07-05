from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "citizen"
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    preferred_language: str = "English"
    family_members: List[Dict[str, Any]] = []
    medical_conditions: Optional[str] = None
    emergency_contacts: List[Dict[str, Any]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    location_address: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    preferred_language: str
    family_members: List[Dict[str, Any]]
    medical_conditions: Optional[str]
    emergency_contacts: List[Dict[str, Any]]
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- INCIDENT SCHEMAS ---
class IncidentReport(BaseModel):
    title: str
    description: Optional[str] = None
    location_lat: float
    location_lng: float
    address: Optional[str] = None
    disaster_type: str  # Flood, Fire, Collapse, Landslide, Blockage, Other
    severity: str = "Medium"  # Low, Medium, High, Critical
    image_url: Optional[str] = None
    assessment_details: Optional[Dict[str, Any]] = None

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: Optional[int]
    title: str
    description: Optional[str]
    location_lat: float
    location_lng: float
    address: Optional[str]
    disaster_type: str
    severity: str
    status: str
    image_url: Optional[str]
    assessment_details: Optional[Dict[str, Any]]
    created_at: datetime

# --- RESOURCE & SHELTER SCHEMAS ---
class ShelterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    location_lat: float
    location_lng: float
    contact_number: Optional[str]
    total_beds: int
    available_beds: int
    has_food: bool
    has_water: bool
    has_medical: bool
    has_power: bool
    distance_km: Optional[float] = None

class HospitalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    location_lat: float
    location_lng: float
    contact_number: Optional[str]
    total_beds: int
    available_beds: int
    emergency_services: bool
    distance_km: Optional[float] = None

class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    quantity: float
    unit: str
    location_lat: float
    location_lng: float
    address: Optional[str]
    contact_number: Optional[str]
    status: str
    distance_km: Optional[float] = None

# --- VOLUNTEER SCHEMAS ---
class VolunteerRegister(BaseModel):
    name: str
    skill_set: str  # first-aid, rescue, cooking, etc.
    phone: str
    email: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    address: Optional[str] = None

class VolunteerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    skill_set: Optional[str]
    phone: str
    email: Optional[str]
    status: str
    location_lat: Optional[float]
    location_lng: Optional[float]
    address: Optional[str]
    distance_km: Optional[float] = None

# --- CHAT & MULTI-AGENT EXECUTION SCHEMAS ---
class ChatRequest(BaseModel):
    user_query: str
    user_location: str = "Mumbai"
    user_lat: float = 19.0760
    user_lng: float = 72.8777
    user_language: str = "English"
    image_data_b64: Optional[str] = None  # Base64 string of uploaded image
    image_name: Optional[str] = None

class ChatResponse(BaseModel):
    final_response: str
    agent_logs: List[Dict[str, Any]]
    vision_assessment: Optional[Dict[str, Any]]
    weather_info: Optional[Dict[str, Any]]
    search_alerts: List[Dict[str, Any]]
    navigation_info: Optional[Dict[str, Any]]
    shelter_info: List[Dict[str, Any]]
    hospital_info: List[Dict[str, Any]]
    medical_advice: Optional[str] = None
    resource_info: List[Dict[str, Any]]
    communication_info: Optional[Dict[str, Any]]
    government_info: List[Dict[str, Any]]
    recovery_info: Optional[str]
    volunteer_info: Optional[Dict[str, Any]]
