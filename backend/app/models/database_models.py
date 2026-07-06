from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="citizen")  # citizen, responder, admin, volunteer
    location_address = Column(String, nullable=True)
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    preferred_language = Column(String, default="English")
    family_members = Column(JSON, default=list)  # list of dicts: name, relationship, age
    medical_conditions = Column(Text, nullable=True)  # comma separated list
    emergency_contacts = Column(JSON, default=list)  # list of dicts: name, relationship, phone
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    incidents = relationship("Incident", back_populates="reporter")
    emergency_requests = relationship("EmergencyRequest", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    disaster_type = Column(String, nullable=False)  # Flood, Fire, Collapse, Landslide, Blockage, Other
    severity = Column(String, default="Medium")  # Low, Medium, High, Critical
    status = Column(String, default="Reported")  # Reported, Verifying, Responding, Resolved
    image_url = Column(String, nullable=True)
    assessment_details = Column(JSON, nullable=True)  # vision analysis output
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reporter = relationship("User", back_populates="incidents")

class Shelter(Base):
    __tablename__ = "shelters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    contact_number = Column(String, nullable=True)
    total_beds = Column(Integer, default=50)
    available_beds = Column(Integer, default=50)
    has_food = Column(Boolean, default=True)
    has_water = Column(Boolean, default=True)
    has_medical = Column(Boolean, default=True)
    has_power = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    contact_number = Column(String, nullable=True)
    total_beds = Column(Integer, default=100)
    available_beds = Column(Integer, default=50)
    emergency_services = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # Food, Water, Medicine, Fuel, Power
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # kg, liters, packets, cans
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    status = Column(String, default="Available")  # Available, Low, Depleted
    created_at = Column(DateTime, default=datetime.utcnow)

class Volunteer(Base):
    __tablename__ = "volunteers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    skill_set = Column(Text, nullable=True)  # first-aid, rescue, cooking, driving
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    status = Column(String, default="Available")  # Available, Active, Offline
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    current_assignment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reporter_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    location_lat = Column(Float, nullable=False)
    location_lng = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    status = Column(String, default="Open")  # Open, Dispatched, Resolved
    priority = Column(String, default="High")  # Low, Medium, High, Critical
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="emergency_requests")

class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # Compensation, Relief Fund, Medical Aid, Housing
    eligibility_criteria = Column(Text, nullable=True)
    benefit_amount = Column(String, nullable=True)
    contact_helpline = Column(String, nullable=True)
    documents_required = Column(JSON, default=list)  # list of strings: Aadhar, Income Certificate, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class WeatherAlert(Base):
    __tablename__ = "weather_alerts"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    alert_type = Column(String, nullable=False)  # Rain, Flood, cyclone, heatwave, storm
    severity = Column(String, default="Moderate")  # Moderate, Severe, Extreme
    description = Column(Text, nullable=True)
    forecast_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
