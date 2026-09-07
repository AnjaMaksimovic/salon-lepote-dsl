"""FastAPI application serving the generated API and frontend."""
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from generated.database import get_db
from generated.entities import Worker, Service
import business_rules
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from generated.database import init_db
from generated.routes import router


@asynccontextmanager
async def lifespan(app):
    init_db()
    yield


app = FastAPI(title="Beauty Salon API", lifespan=lifespan)
app.include_router(router)
FRONTEND_DIR = Path(__file__).resolve().parent / "generated" / "frontend"
app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.middleware("http")
async def disable_frontend_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/app/"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


@app.get("/", include_in_schema=False)
def home():
    return RedirectResponse("/app/index.html")


@app.get("/reports/revenue")
def revenue(date_from: datetime, date_to: datetime, db: Session = Depends(get_db)):
    if date_from.tzinfo or date_to.tzinfo or date_from > date_to:
        raise HTTPException(status_code=422, detail="Use ordered local datetimes without timezone offsets")
    return business_rules.revenue_report(db, date_from, date_to)


@app.get("/appointments/suggestions")
def suggest_appointment(worker_id: int, service_ids: str, date_time: datetime,
                        duration_minutes: int = Query(..., gt=0), db: Session = Depends(get_db)):
    try:
        ids = list(dict.fromkeys(int(value.strip()) for value in service_ids.split(",")))
    except ValueError as error:
        raise HTTPException(status_code=422, detail="Provide comma-separated service IDs") from error
    if date_time.tzinfo:
        raise HTTPException(status_code=422, detail="Use a local datetime without timezone offset")
    if db.get(Worker, worker_id) is None or any(db.get(Service, i) is None for i in ids):
        raise HTTPException(status_code=404, detail="Worker or service not found")
    return business_rules.suggest_alternative(db, worker_id, ids, date_time, duration_minutes)
