# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Evitar archivos pyc y forzar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema necesarias para compilación (si las necesitas)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python desde requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear usuario no root y ajustar permisos
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Puerto expuesto (Render inyecta $PORT en tiempo de ejecución)
EXPOSE 8000

# Comando por defecto: usa la variable PORT si está definida, si no 8000
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]