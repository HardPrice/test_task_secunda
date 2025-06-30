# Organization Directory API

REST API приложение для справочника Организаций, Зданий и Деятельности.

## 🚀 Быстрый запуск

### Вариант 1: Автоматический запуск (рекомендуется)

**Windows:**
```cmd
setup_and_run.bat
```

**Linux/MacOS:**
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Вариант 2: Ручной запуск

1. **Убедитесь, что установлены Docker и Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Клонируйте репозиторий и перейдите в папку проекта**
   ```bash
   git clone <repository-url>
   cd test_task_secunda
   ```

3. **Запустите приложение**
   ```bash
   # Остановите старые контейнеры (если есть)
   docker-compose down

   # Соберите и запустите контейнеры
   docker-compose up -d

   # Подождите 10-15 секунд для запуска БД, затем примените миграции
   docker-compose exec web alembic upgrade head
   ```

4. **Проверьте, что приложение запустилось**
   - API: http://localhost:8000
   - Документация: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📋 После запуска доступно

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API базовый URL:** http://localhost:8000/api/v1
- **API ключ:** `your-super-secret-api-key`

## 🔧 Функциональность

- **Управление организациями:** создание, поиск, просмотр
- **Управление зданиями:** создание, просмотр с геокоординатами
- **Управление видами деятельности:** создание с ограничением уровня вложенности до 3
- **Поиск организаций:**
  - по конкретному зданию
  - по виду деятельности (включая все дочерние категории)
  - по географическому расположению (радиус/прямоугольная область)
  - по названию (частичное совпадение)

## 🧪 Тестирование

**Запуск тестов:**
```bash
docker-compose exec web python -m pytest tests/test_api.py -v
```

**Все тесты покрывают:**
- Создание зданий с валидацией координат
- Создание организаций с валидацией телефонов
- Создание видов деятельности с ограничением вложенности
- Валидацию входных данных

## 📝 Примеры использования API

### Авторизация
Все запросы требуют заголовок:
```
api_key: your-super-secret-api-key
```

### Создание здания
```bash
curl -H "api_key: your-super-secret-api-key" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"address": "г. Москва, ул. Тестовая 1", "latitude": 55.7558, "longitude": 37.6173}' \
     "http://localhost:8000/api/v1/buildings/"
```

### Создание организации
```bash
curl -H "api_key: your-super-secret-api-key" \
     -H "Content-Type: application/json" \
     -X POST \
     -d '{"name": "ООО Тест", "building_id": 1, "phones": ["2-222-222"], "activities": [1]}' \
     "http://localhost:8000/api/v1/organizations/"
```

### Получение всех организаций
```bash
curl -H "api_key: your-super-secret-api-key" \
     "http://localhost:8000/api/v1/organizations/"
```

### Поиск организаций в конкретном здании
```bash
curl -H "api_key: your-super-secret-api-key" \
     "http://localhost:8000/api/v1/organizations/?building_id=1"
```

### Поиск организаций по виду деятельности (включая дочерние)
```bash
curl -H "api_key: your-super-secret-api-key" \
     "http://localhost:8000/api/v1/organizations/?activity_id=1"
```

### Поиск организаций в радиусе 1км от точки
```bash
curl -H "api_key: your-super-secret-api-key" \
     "http://localhost:8000/api/v1/organizations/?latitude=55.7558&longitude=37.6173&radius=1000"
```

### Поиск организаций по названию
```bash
curl -H "api_key: your-super-secret-api-key" \
     "http://localhost:8000/api/v1/organizations/?name=Рога"
```

## 🗂️ Структура проекта

```
├── app/                    # Основной код приложения
│   ├── __init__.py         # Пакет приложения
│   ├── api/               # API роуты и зависимости
│   │   ├── __init__.py
│   │   ├── deps.py        # Зависимости (авторизация)
│   │   └── endpoints.py   # API endpoints
│   ├── core/              # Основные настройки
│   │   ├── __init__.py
│   │   └── config.py      # Конфигурация приложения
│   ├── database/          # База данных
│   │   ├── __init__.py
│   │   └── session.py     # Сессия SQLAlchemy
│   ├── models/            # Модели данных
│   │   ├── __init__.py
│   │   └── models.py      # SQLAlchemy модели
│   ├── schemas/           # Pydantic схемы
│   │   ├── __init__.py
│   │   └── schemas.py     # Схемы для валидации данных
│   └── main.py            # Точка входа FastAPI
├── alembic/               # Миграции базы данных
│   ├── versions/          # Файлы миграций
│   ├── env.py            # Конфигурация Alembic
│   └── script.py.mako    # Шаблон миграций
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── conftest.py        # Конфигурация тестов
│   └── test_api.py        # API тесты
├── .flake8                # Конфигурация flake8
├── .pre-commit-config.yaml # Конфигурация pre-commit
├── alembic.ini            # Конфигурация Alembic
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile             # Docker образ
├── requirements.txt       # Python зависимости
├── requirements-dev.txt   # Зависимости для разработки
├── setup_and_run.bat      # Скрипт запуска для Windows
└── setup_and_run.sh       # Скрипт запуска для Linux/MacOS
```

## 🛠️ Технологии

### Основные технологии
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных
- **PostGIS** - расширение PostgreSQL для работы с геоданными
- **Docker** - контейнеризация приложения
- **pytest** - тестирование

### Инструменты разработки
- **Black** - автоматическое форматирование кода
- **isort** - сортировка импортов
- **flake8** - линтер для проверки стиля кода
- **mypy** - статическая типизация
- **pre-commit** - автоматические проверки перед коммитом

## 📋 Тестовые данные

В базе данных автоматически создаются следующие тестовые данные:

### Здания:
- г. Москва, ул. Ленина 1 (координаты: 55.7558, 37.6173)
- г. Москва, ул. Тверская 2 (координаты: 55.7648, 37.6067)

### Виды деятельности (древовидная структура):
```
Еда
├── Мясная продукция
└── Молочная продукция

Автомобили
├── Грузовые
└── Легковые
    ├── Запчасти
    └── Аксессуары
```

### Организации:
- ООО "Рога и Копыта" (здание 1, телефоны: 2-222-222, 3-333-333, 8-923-666-13-13)
  - Виды деятельности: Мясная продукция, Молочная продукция
- ЗАО "АвтоМир" (здание 2, телефоны: 4-444-444, 5-555-555)
  - Виды деятельности: Легковые, Запчасти, Аксессуары

## 🔗 API Endpoints

### Здания
- `GET /api/v1/buildings/` - Получить все здания
- `POST /api/v1/buildings/` - Создать новое здание

### Виды деятельности
- `GET /api/v1/activities/` - Получить все виды деятельности
- `POST /api/v1/activities/` - Создать новый вид деятельности

### Организации
- `GET /api/v1/organizations/` - Получить организации с фильтрацией
- `GET /api/v1/organizations/{id}` - Получить организацию по ID
- `POST /api/v1/organizations/` - Создать новую организацию

### Параметры фильтрации для GET /api/v1/organizations/:
- `building_id` - фильтр по зданию
- `activity_id` - фильтр по виду деятельности (включая дочерние)
- `name` - поиск по названию (частичное совпадение)
- `latitude`, `longitude`, `radius` - географический поиск в радиусе (метры)
- `bbox_min_lat`, `bbox_min_lon`, `bbox_max_lat`, `bbox_max_lon` - поиск в прямоугольной области

## 📋 Форматы данных

### Телефонные номера
Поддерживаются следующие форматы:
- X-XXX-XXX (например, 2-222-222)
- XXX-XXX-XXX (например, 3-333-333)
- X-XXX-XXX-XX-XX (например, 8-923-666-13-13)

### Географические координаты
Координаты указываются в формате WGS84 (EPSG:4326)

## 🚫 Ограничения

- Максимальный уровень вложенности видов деятельности: 3
- Обязательна авторизация по API ключу для всех запросов
- Координаты должны быть в диапазоне: широта (-90, 90), долгота (-180, 180)

## 🛑 Остановка приложения

```bash
docker-compose down
```

## 💻 Разработка

### Настройка среды разработки

1. **Клонируйте репозиторий**
   ```bash
   git clone <repository-url>
   cd test_task_secunda
   ```

2. **Создайте виртуальное окружение**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/MacOS
   python -m venv venv
   source venv/bin/activate
   ```

3. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Настройте pre-commit хуки**
   ```bash
   pre-commit install
   ```

5. **Запустите проверки качества кода**
   ```bash
   pre-commit run --all-files
   ```

### Инструменты качества кода

Проект использует следующие инструменты:
- **Black** - автоматическое форматирование кода
- **isort** - сортировка импортов
- **flake8** - проверка стиля кода и потенциальных ошибок
- **mypy** - статическая типизация
- **pre-commit** - автоматическая проверка перед коммитом

### Готовность к разработке

✅ **Проект полностью настроен для разработки:**
- Все инструменты качества кода настроены и работают
- Pre-commit хуки установлены и проверены
- Соблюдены стандарты PEP 8 и современные практики Python
- Статическая типизация настроена через mypy
- Автоматическое форматирование через Black
- Все тесты проходят успешно

### Структура зависимостей

- `requirements.txt` - основные зависимости для production
- `requirements-dev.txt` - дополнительные инструменты для разработки
