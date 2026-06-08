# Usamos una imagen ligera de Python oficial
FROM python:3.10-slim

# Evita que Python escriba archivos .pyc en el disco y fuerza la salida en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de requerimientos para optimizar la caché de Docker
COPY requirements.txt /app/

# Instala las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del repositorio dentro del contenedor
COPY . /app/

# Expone el puerto estándar que usa Google Cloud Run de forma interna
EXPOSE 8080

# Comando para ejecutar la aplicación usando Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]
