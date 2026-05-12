from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import logging
import os

from app.database.session import engine, Base
from app.models import user, book, borrow_record
from app.routers import auth, books, borrow
from app.core.dependencies import get_current_user, get_current_admin
from app.core.logger import setup_logger
from app.core.middleware import log_requests
from app.monitoring.metrics import get_stats
from contextlib import asynccontextmanager


setup_logger()
logger = logging.getLogger("library.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="library management system",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(borrow.router)


@app.get("/")
def home():
    return {"message": "library api is running"}


@app.get("/protected")
def protected_route(current_user=Depends(get_current_user)):
    return {
        "message": "authenticated",
        "user": current_user.username,
        "role": current_user.role
    }


@app.get("/admin-only")
def admin_only_route(current_user=Depends(get_current_admin)):
    return {
        "message": "admin access granted",
        "user": current_user.username
    }


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        return {"status": "healthy"}
    except Exception:
        return {"status": "unhealthy"}


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/stats/recent-errors")
def recent_errors():
    try:
        with open("logs/errors.log") as f:
            lines = f.readlines()
        return lines[-10:]
    except FileNotFoundError:
        return []


@app.get("/info")
def app_info():
    return {
        "app": "library management system",
        "version": "1.0.0",
        "features": [
            "jwt authentication",
            "role based authorization",
            "book management",
            "borrow system",
            "redis caching",
            "logging and monitoring"
        ]
    }