from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal
from app.routers import games, leagues, teams

app = FastAPI(title="Scoreline API")
app.include_router(leagues.router)
app.include_router(games.router)
app.include_router(teams.router)


@app.get("/health")
def health() -> dict:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}
