from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_DWithin, ST_MakeEnvelope, ST_MakePoint, ST_Transform
from sqlalchemy import func, and_

from app.database.session import get_db
from app.models import models
from app.schemas import schemas
from app.core.config import settings
from app.api.deps import verify_api_key

router = APIRouter()

@router.get("/buildings/", response_model=List[schemas.Building], tags=["buildings"])
def get_buildings(
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Получить список всех зданий."""
    return db.query(models.Building).all()

@router.post("/organizations/", response_model=schemas.Organization, status_code=201, tags=["organizations"])
def create_organization(
    organization: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Создать новую организацию."""
    db_org = models.Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    for phone_number in organization.phones:
        phone = models.Phone(number=phone_number)
        db_org.phones.append(phone)
    
    activities = db.query(models.Activity).filter(
        models.Activity.id.in_(organization.activities)
    ).all()
    db_org.activities = activities
    
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org
