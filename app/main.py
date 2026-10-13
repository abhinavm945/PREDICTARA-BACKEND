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

# Enable CORS for local Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Predictara AI Backend",
        "database": settings.DATABASE_URL.split("://")[0],
        "version": "1.0.0",
        "docs": "/docs"
    }
