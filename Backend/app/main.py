from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.models.domain import Base
from app.db.seed import seed_db

from app.api.v1.auth import router as auth_router
from app.api.v1.farms import router as farms_router
from app.api.v1.systems import router as systems_router
from app.api.v1.plants import router as plants_router
from app.api.v1.sensors import router as sensors_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.ml import router as ml_router

# Create DB tables & seed initial data
Base.metadata.create_all(bind=engine)
try:
    seed_db()
except Exception as e:
    print(f"Seeding notice: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(farms_router, prefix=settings.API_V1_STR)
app.include_router(systems_router, prefix=settings.API_V1_STR)
app.include_router(plants_router, prefix=settings.API_V1_STR)
app.include_router(sensors_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(alerts_router, prefix=settings.API_V1_STR)
app.include_router(ml_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "Welcome to Machine Learning Hydroponic Assistant FastAPI Backend",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
