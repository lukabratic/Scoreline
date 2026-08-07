from fastapi import FastAPI
from sqlalchemy import text

from app.db import SessionLocal

app = FastAPI(title="Scoreline API")


@app.get("/health")
def health() -> dict:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}
