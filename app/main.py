from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import players, combat

# Metadata para la documentación de la API
description = """
Una API simple para un juego de rol por turnos. 🚀

### Autores:
*   **Maury Alexander Maturana Lozano**
*   **Brian Steven Albornoz**
*   **Steven Munoz Vargas**
"""

app = FastAPI(
    title="FastAPI RPG API",
    description=description,
    version="1.0.0"
)

# Montar el directorio 'static' para servir archivos HTML, CSS, JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir los routers de la API
app.include_router(players.router, prefix="/api/v1", tags=["Players"])
app.include_router(combat.router, prefix="/api/v1", tags=["Combat"])

@app.get("/", response_class=FileResponse)
async def read_index():
    """Sirve la página principal del juego."""
    return "static/index.html"
