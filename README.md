# Proyecto FastAPI con Docker

Este es un proyecto de ejemplo de una API con FastAPI y Docker.

## Cómo ejecutar localmente

1.  Instalar dependencias:

    ```bash
    python -m pip install fastapi uvicorn
    ```

2.  Ejecutar la aplicación:

    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

## Cómo construir la imagen de Docker

```bash
docker build -t juego-api:latest .
```

## Cómo correr la imagen de Docker

```bash
docker run -p 8000:8000 juego-api:latest
```
