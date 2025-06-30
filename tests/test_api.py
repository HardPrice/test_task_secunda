import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.core.config import settings

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@db/organization_directory"
)

# Создаем подключение к базе данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def setup_module():
    """Подготавливаем тесты - проверяем подключение к БД."""
    # Проверяем подключение к базе данных
    with engine.connect() as conn:
        pass  # Просто проверяем, что подключение работает

def teardown_module():
    """Очищаем после тестов."""
    # Можно добавить очистку тестовых данных, если нужно
    pass

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_building():
    """Тест создания здания с валидными данными."""
    response = client.post(
        f"{settings.API_V1_STR}/buildings/",
        headers={"api_key": settings.API_KEY},
        json={
            "address": "г. Москва, ул. Тестовая 1",
            "latitude": 55.7558,
            "longitude": 37.6173
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["address"] == "г. Москва, ул. Тестовая 1"
    assert data["latitude"] == 55.7558
    assert data["longitude"] == 37.6173

def test_create_building_invalid_coordinates():
    """Тест создания здания с невалидными координатами."""
    response = client.post(
        f"{settings.API_V1_STR}/buildings/",
        headers={"api_key": settings.API_KEY},
        json={
            "address": "г. Москва, ул. Тестовая 1",
            "latitude": 100,  # Невалидная широта
            "longitude": 37.6173
        }
    )
    assert response.status_code == 422

def test_create_organization():
    """Тест создания организации."""
    # Сначала создаем здание
    building_response = client.post(
        f"{settings.API_V1_STR}/buildings/",
        headers={"api_key": settings.API_KEY},
        json={
            "address": "г. Москва, ул. Тестовая 1",
            "latitude": 55.7558,
            "longitude": 37.6173
        }
    )
    building_id = building_response.json()["id"]
    
    # Создаем организацию
    response = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers={"api_key": settings.API_KEY},
        json={
            "name": "ООО Тест",
            "building_id": building_id,
            "phones": ["2-222-222"],
            "activities": []
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ООО Тест"
    assert data["building_id"] == building_id
    assert len(data["phones"]) == 1
    assert data["phones"][0]["number"] == "2-222-222"

def test_create_organization_invalid_phone():
    """Тест создания организации с невалидным номером телефона."""
    response = client.post(
        f"{settings.API_V1_STR}/organizations/",
        headers={"api_key": settings.API_KEY},
        json={
            "name": "ООО Тест",
            "building_id": 1,
            "phones": ["invalid-phone"],
            "activities": []
        }
    )
    assert response.status_code == 422
    error_detail = response.json()["detail"][0]
    assert "Неверный формат номера телефона" in error_detail["msg"]

def test_create_activity_max_level():
    """Тест создания вида деятельности с превышением максимального уровня вложенности."""
    import time
    timestamp = str(int(time.time()))
    
    # Создаем корневую категорию
    root = client.post(
        f"{settings.API_V1_STR}/activities/",
        headers={"api_key": settings.API_KEY},
        json={"name": f"Тест Уровень 1 {timestamp}"}
    )
    assert root.status_code == 201
    root_id = root.json()["id"]
    
    # Создаем категорию второго уровня
    level2 = client.post(
        "/api/v1/activities/",
        headers={"api_key": settings.API_KEY},
        json={"name": f"Тест Уровень 2 {timestamp}", "parent_id": root_id}
    )
    assert level2.status_code == 201
    level2_id = level2.json()["id"]
    
    # Создаем категорию третьего уровня
    level3 = client.post(
        "/api/v1/activities/",
        headers={"api_key": settings.API_KEY},
        json={"name": f"Тест Уровень 3 {timestamp}", "parent_id": level2_id}
    )
    assert level3.status_code == 201
    level3_id = level3.json()["id"]
    
    # Пытаемся создать категорию четвертого уровня
    response = client.post(
        "/api/v1/activities/",
        headers={"api_key": settings.API_KEY},
        json={"name": f"Тест Уровень 4 {timestamp}", "parent_id": level3_id}
    )
    assert response.status_code == 400
