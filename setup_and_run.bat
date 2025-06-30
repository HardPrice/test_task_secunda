@echo off
setlocal enabledelayedexpansion

echo === Настройка проекта Organization Directory API ===

REM Проверяем наличие Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не установлен. Пожалуйста, установите Docker.
    pause
    exit /b 1
)

REM Проверяем наличие Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose.
    pause
    exit /b 1
)

echo ✅ Docker и Docker Compose найдены

REM Останавливаем существующие контейнеры
echo 🔄 Останавливаем существующие контейнеры...
docker-compose down

REM Собираем и запускаем контейнеры
echo 🚀 Собираем и запускаем контейнеры...
docker-compose up -d

REM Ждем запуска базы данных
echo ⏳ Ждем запуска базы данных...
timeout /t 15 /nobreak >nul

REM Применяем миграции
echo 📊 Применяем миграции и создаем тестовые данные...
docker-compose exec web alembic upgrade head

echo.
echo 🎉 Проект успешно запущен!
echo.
echo 📖 Документация API доступна по адресам:
echo    - Swagger UI: http://localhost:8000/docs
echo    - ReDoc: http://localhost:8000/redoc
echo.
echo 🔑 API ключ для авторизации: your-super-secret-api-key
echo    Используйте заголовок: api_key: your-super-secret-api-key
echo.
echo 📋 Примеры запросов:
echo    # Получить все здания
echo    curl -H "api_key: your-super-secret-api-key" http://localhost:8000/api/v1/buildings/
echo.
echo    # Получить все организации
echo    curl -H "api_key: your-super-secret-api-key" http://localhost:8000/api/v1/organizations/
echo.
echo    # Поиск организаций в радиусе 1км от точки
echo    curl -H "api_key: your-super-secret-api-key" "http://localhost:8000/api/v1/organizations/?latitude=55.7558&longitude=37.6173&radius=1000"
echo.
echo 🛑 Для остановки проекта выполните: docker-compose down

pause
