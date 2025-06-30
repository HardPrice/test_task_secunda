from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_DWithin, ST_MakeEnvelope, ST_MakePoint, ST_Transform
from geoalchemy2 import WKTElement
from sqlalchemy import func, and_, or_

from app.database.session import get_db
from app.models import models
from app.schemas import schemas
from app.core.config import settings
from app.api.deps import verify_api_key

router = APIRouter()

# === BUILDINGS ENDPOINTS ===

@router.get("/buildings/", response_model=List[schemas.Building], tags=["buildings"])
def get_buildings(
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Получить список всех зданий."""
    return db.query(models.Building).all()

@router.post("/buildings/", response_model=schemas.Building, status_code=201, tags=["buildings"])
def create_building(
    building: schemas.BuildingCreate,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Создать новое здание."""
    # Создаем WKT точку для координат
    point = WKTElement(f'POINT({building.longitude} {building.latitude})', srid=4326)
    
    db_building = models.Building(
        address=building.address,
        location=point
    )
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

# === ACTIVITIES ENDPOINTS ===

@router.get("/activities/", response_model=List[schemas.Activity], tags=["activities"])
def get_activities(
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Получить список всех видов деятельности."""
    return db.query(models.Activity).all()

@router.post("/activities/", response_model=schemas.Activity, status_code=201, tags=["activities"])
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Создать новый вид деятельности."""
    # Проверяем ограничение на уровень вложенности (максимум 3)
    if activity.parent_id:
        parent = db.query(models.Activity).filter(models.Activity.id == activity.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Родительская категория не найдена")
        if parent.level >= 3:
            raise HTTPException(
                status_code=400, 
                detail="Превышен максимальный уровень вложенности (3 уровня)"
            )
        level = parent.level + 1
    else:
        level = 1
    
    db_activity = models.Activity(
        name=activity.name,
        parent_id=activity.parent_id,
        level=level
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

# === ORGANIZATIONS ENDPOINTS ===

@router.get("/organizations/", response_model=List[schemas.Organization], tags=["organizations"])
def get_organizations(
    building_id: Optional[int] = Query(None, description="ID здания для фильтрации"),
    activity_id: Optional[int] = Query(None, description="ID вида деятельности для фильтрации"),
    name: Optional[str] = Query(None, description="Поиск по названию организации"),
    latitude: Optional[float] = Query(None, description="Широта для географического поиска"),
    longitude: Optional[float] = Query(None, description="Долгота для географического поиска"),
    radius: Optional[float] = Query(None, description="Радиус поиска в метрах"),
    bbox_min_lat: Optional[float] = Query(None, description="Минимальная широта прямоугольной области"),
    bbox_min_lon: Optional[float] = Query(None, description="Минимальная долгота прямоугольной области"),
    bbox_max_lat: Optional[float] = Query(None, description="Максимальная широта прямоугольной области"),
    bbox_max_lon: Optional[float] = Query(None, description="Максимальная долгота прямоугольной области"),
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """
    Получить список организаций с возможностью фильтрации по:
    - зданию
    - виду деятельности (включая дочерние категории)
    - названию
    - географическому расположению (радиус или прямоугольная область)
    """
    query = db.query(models.Organization)
    
    # Фильтр по зданию
    if building_id:
        query = query.filter(models.Organization.building_id == building_id)
    
    # Фильтр по виду деятельности (включая дочерние)
    if activity_id:
        # Получаем ID всех дочерних категорий
        def get_child_activity_ids(parent_id):
            children = db.query(models.Activity.id).filter(models.Activity.parent_id == parent_id).all()
            child_ids = [child[0] for child in children]
            all_ids = [parent_id]
            for child_id in child_ids:
                all_ids.extend(get_child_activity_ids(child_id))
            return all_ids
        
        activity_ids = get_child_activity_ids(activity_id)
        query = query.join(models.organization_activity).filter(
            models.organization_activity.c.activity_id.in_(activity_ids)
        )
    
    # Фильтр по названию
    if name:
        query = query.filter(models.Organization.name.ilike(f"%{name}%"))
    
    # Географический фильтр
    if latitude is not None and longitude is not None:
        if radius:
            # Поиск в радиусе
            point = ST_MakePoint(longitude, latitude)
            query = query.join(models.Building).filter(
                ST_DWithin(models.Building.location, point, radius)
            )
        elif all([bbox_min_lat, bbox_min_lon, bbox_max_lat, bbox_max_lon]):
            # Поиск в прямоугольной области
            envelope = ST_MakeEnvelope(bbox_min_lon, bbox_min_lat, bbox_max_lon, bbox_max_lat, 4326)
            query = query.join(models.Building).filter(
                func.ST_Within(models.Building.location, envelope)
            )
    
    return query.all()

@router.get("/organizations/{organization_id}", response_model=schemas.Organization, tags=["organizations"])
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Получить информацию об организации по её идентификатору."""
    organization = db.query(models.Organization).filter(
        models.Organization.id == organization_id
    ).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return organization

@router.post("/organizations/", response_model=schemas.Organization, status_code=201, tags=["organizations"])
def create_organization(
    organization: schemas.OrganizationCreate,
    db: Session = Depends(get_db),
    api_key: str = Security(verify_api_key)
):
    """Создать новую организацию."""
    # Проверяем, что здание существует
    building = db.query(models.Building).filter(models.Building.id == organization.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    
    db_org = models.Organization(
        name=organization.name,
        building_id=organization.building_id
    )
    
    # Добавляем телефоны
    for phone_number in organization.phones:
        phone = models.Phone(number=phone_number)
        db_org.phones.append(phone)
    
    # Добавляем виды деятельности
    if organization.activities:
        activities = db.query(models.Activity).filter(
            models.Activity.id.in_(organization.activities)
        ).all()
        if len(activities) != len(organization.activities):
            raise HTTPException(status_code=404, detail="Один или несколько видов деятельности не найдены")
        db_org.activities = activities
    
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org
