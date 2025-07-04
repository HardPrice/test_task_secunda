FROM python:3.12-slim

WORKDIR /app

# Устанавливаем зависимости Python
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir shapely

# Копируем код приложения
COPY . .

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
