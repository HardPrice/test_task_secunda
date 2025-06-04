# Organization Directory API

REST API приложение для справочника Организаций, Зданий и Деятельности.

## Функциональность

- Управление организациями (создание, поиск, просмотр)
- Управление зданиями (создание, просмотр)
- Управление видами деятельности (создание с ограничением уровня вложенности до 3)
- Поиск организаций:
  - по конкретному зданию
  - по виду деятельности (включая все дочерние категории)
  - по географическому расположению (радиус/прямоугольная область)
  - по названию

## Требования

- Docker
- Docker Compose

## Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd test_task_secunda
   ```

2. Создайте и запустите контейнеры:
   ```bash
   docker-compose up -d
   ```

3. Примените миграции:
   ```bash
   docker-compose exec web alembic upgrade head
   ```

## API Документация

После запуска приложения, документация API доступна по следующим URL:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Форматы данных

### Телефонные номера
Поддерживаются следующие форматы:
- X-XXX-XXX (например, 2-222-222)
- XXX-XXX-XXX (например, 3-333-333)
- X-XXX-XXX-XX-XX (например, 8-923-666-13-13)

### Географические координаты
Координаты указываются в формате WGS84 (EPSG:4326)

## Аутентификация

Все API endpoints защищены API ключом. Для доступа к API необходимо передавать заголовок:

```
api_key: your-super-secret-api-key
```

## Примеры запросов

1. Получение списка всех организаций:
```bash
curl -X GET "http://localhost:8000/api/v1/organizations/" -H "api_key: your-super-secret-api-key"
```

2. Поиск организаций в радиусе 1км от точки:
```bash
curl -X GET "http://localhost:8000/api/v1/organizations/?location.latitude=55.7558&location.longitude=37.6173&location.radius=1000" -H "api_key: your-super-secret-api-key"
```

3. Создание новой организации:
```bash
curl -X POST "http://localhost:8000/api/v1/organizations/" \
     -H "api_key: your-super-secret-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "New Company",
       "building_id": 1,
       "phones": ["1-111-111"],
       "activities": [1, 2]
     }'
```
