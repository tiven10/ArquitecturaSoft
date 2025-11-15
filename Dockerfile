# 1. Usar una imagen base de Python
FROM python:3.9-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el archivo de requisitos e instalar dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el resto del código de la aplicación
COPY . .

# 5. Exponer el puerto en el que corre la aplicación
EXPOSE 8000

# 6. Comando para ejecutar la aplicación
# Uvicorn se ejecuta en 0.0.0.0 para ser accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
