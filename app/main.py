from fastapi import FastAPI
from app.routers import players, combat

app = FastAPI(
    title="Juego API",
    description="Una API simple para un juego de rol.",
    version="0.1.0"
)

# Incluir los routers
app.include_router(players.router, prefix="/api/v1", tags=["Players"])
app.include_router(combat.router, prefix="/api/v1", tags=["Combat"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API del Juego"}
