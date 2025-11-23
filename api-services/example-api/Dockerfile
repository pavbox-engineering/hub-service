FROM python:3.11-slim

WORKDIR /app

# Пример для FastAPI приложения
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Временный пример с базовым HTTP сервером
RUN pip install --no-cache-dir fastapi uvicorn

COPY . .

# Для FastAPI приложения:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Временная заглушка для демонстрации
CMD ["python", "-m", "http.server", "8000"]


