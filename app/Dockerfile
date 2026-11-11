
# Imagen base con Python
FROM python:3.12-slim

# Instalar FFmpeg dentro del contenedor
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar las dependencias
COPY requirements.txt .

# Instalar Flask y Gunicorn
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app.py .

# Puerto interno de la aplicación
EXPOSE 5000

# Ejecutar Flask mediante Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "330", "app:app"]
