from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings

from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.core.init_db import seed_database
import app.models.db_models # Ensure models are loaded

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    # Seed initial concepts and questions
    seed_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API service for Predictara AI Academic Intelligence Platform with full Database persistence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
# Supports local development, production Vercel & Render domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "https://predictara.vercel.app",
        "https://predictara-frontend-only-poc.onrender.com",
        "*"
    ],
    allow_origin_regex=r"https://.*(\.vercel\.app|\.onrender\.com)",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)
app.include_router(router, prefix="/api")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Predictara AI Backend",
        "database": settings.DATABASE_URL.split("://")[0],
        "version": "1.0.0",
        "docs": "/docs"
    }
