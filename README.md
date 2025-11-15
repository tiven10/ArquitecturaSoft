# FastAPI RPG Battle Simulator

Un simple juego de rol por turnos construido con FastAPI para el backend y HTML/JavaScript/CSS puro para el frontend.

## Características

*   Crea jugadores con diferentes profesiones (Guerrero, Mago, Paladín, etc.).
*   Sistema de combate por turnos con ataques únicos por profesión.
*   Variabilidad en el daño, críticos y fallos.
*   Coste de maná para habilidades especiales.
*   Sistema de experiencia y subida de nivel.
*   Interfaz web interactiva para jugar.
*   Totalmente contenedorizado con Docker.

## Autores

*   **Maury Alexander Maturana Lozano**
*   **Brian Steven Albornoz**
*   **Steven Munoz Vargas**

## Cómo Ejecutar

1.  Asegúrate de tener Docker instalado y en ejecución.
2.  Construye la imagen de Docker:
    ```bash
    docker build -t fastapi-rpg-app .
    ```
3.  Ejecuta el contenedor:
    ```bash
    docker run --rm -d -p 8000:8000 --name rpg-api-container fastapi-rpg-app
    ```
4.  Abre tu navegador y ve a `http://localhost:8000`.
