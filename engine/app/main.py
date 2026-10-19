"""API du moteur. Les routes /tickets et /alerts arrivent à l'étape 3."""
from fastapi import FastAPI

app = FastAPI(title="TicketIt engine", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": app.version}
