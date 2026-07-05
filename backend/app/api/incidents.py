from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.database_models import Incident
from backend.app.schemas.schemas import IncidentReport, IncidentOut
from backend.app.api.auth import get_optional_user
from backend.app.models.database_models import User
from typing import List, Optional

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.post("/report", response_model=IncidentOut)
def report_incident(incident_in: IncidentReport, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    incident = Incident(
        reporter_id=current_user.id if current_user else None,
        title=incident_in.title,
        description=incident_in.description,
        location_lat=incident_in.location_lat,
        location_lng=incident_in.location_lng,
        address=incident_in.address,
        disaster_type=incident_in.disaster_type,
        severity=incident_in.severity,
        status="Reported",
        image_url=incident_in.image_url,
        assessment_details=incident_in.assessment_details
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/list", response_model=List[IncidentOut])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(Incident).order_by(Incident.created_at.desc()).all()
