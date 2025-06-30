from typing import List, Optional
from pydantic import BaseModel, constr, field_validator, ConfigDict
from geopy.point import Point
from geoalchemy2.shape import to_shape

class PhoneBase(BaseModel):
    number: constr(pattern=r'^(\d{1}-\d{3}-\d{3}|\d{3}-\d{3}-\d{3}|\d{1}-\d{3}-\d{3}-\d{2}-\d{2})$')
    
    @classmethod
    def validate_phone_format(cls, number: str) -> bool:
        """Проверяет, соответствует ли номер одному из форматов:
        - X-XXX-XXX (например, 2-222-222)
        - XXX-XXX-XXX (например, 3-333-333)
        - X-XXX-XXX-XX-XX (например, 8-923-666-13-13)
        """
        import re
        patterns = [
            r'^\d{1}-\d{3}-\d{3}$',  # 2-222-222
            r'^\d{3}-\d{3}-\d{3}$',  # 333-333-333
            r'^\d{1}-\d{3}-\d{3}-\d{2}-\d{2}$'  # 8-923-666-13-13
        ]
        return any(re.match(pattern, number) for pattern in patterns)

class PhoneCreate(PhoneBase):
    pass

class Phone(PhoneBase):
    id: int
    organization_id: int

    model_config = ConfigDict(from_attributes=True)

class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        """Проверяет, что широта находится в диапазоне -90 до 90 градусов."""
        if not -90 <= v <= 90:
            raise ValueError('Широта должна быть в диапазоне от -90 до 90 градусов')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        """Проверяет, что долгота находится в диапазоне -180 до 180 градусов."""
        if not -180 <= v <= 180:
            raise ValueError('Долгота должна быть в диапазоне от -180 до 180 градусов')
        return v

class BuildingCreate(BuildingBase):
    pass

class Building(BuildingBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict):
            return super().model_validate(obj, *args, **kwargs)
        
        # Создаем словарь для данных
        data = {}
        data['id'] = obj.id
        data['address'] = obj.address
        
        if hasattr(obj, 'location') and obj.location is not None:
            # Получаем координаты из WKB формата
            point = to_shape(obj.location)
            data['longitude'] = point.x
            data['latitude'] = point.y
        else:
            data['longitude'] = 0.0
            data['latitude'] = 0.0
            
        return super().model_validate(data, *args, **kwargs)

class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    level: Optional[int] = 1

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []

    model_config = ConfigDict(from_attributes=True)

class OrganizationBase(BaseModel):
    name: str
    building_id: int

class OrganizationCreate(OrganizationBase):
    phones: List[str]
    activities: List[int]
    
    @field_validator('phones')
    @classmethod
    def validate_phones(cls, phones: List[str]) -> List[str]:
        """Проверяет, что все номера телефонов соответствуют допустимому формату."""
        valid_patterns = [
            r'^\d{1}-\d{3}-\d{3}$',  # 2-222-222
            r'^\d{3}-\d{3}-\d{3}$',  # 333-333-333
            r'^\d{1}-\d{3}-\d{3}-\d{2}-\d{2}$'  # 8-923-666-13-13
        ]
        import re
        for phone in phones:
            if not any(re.match(pattern, phone) for pattern in valid_patterns):
                raise ValueError(
                    f'Неверный формат номера телефона: {phone}. '
                    'Допустимые форматы: X-XXX-XXX, XXX-XXX-XXX, X-XXX-XXX-XX-XX'
                )
        return phones

class Organization(OrganizationBase):
    id: int
    phones: List[Phone]
    activities: List[Activity]
    building: Building

    model_config = ConfigDict(from_attributes=True)

# Обновляем forward references
Activity.model_rebuild()

class LocationQuery(BaseModel):
    latitude: float
    longitude: float
    radius: Optional[float] = None  # в метрах
    bbox_min_lat: Optional[float] = None
    bbox_min_lon: Optional[float] = None
    bbox_max_lat: Optional[float] = None
    bbox_max_lon: Optional[float] = None
