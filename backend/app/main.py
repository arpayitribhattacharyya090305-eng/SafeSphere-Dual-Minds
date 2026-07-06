from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import incidents, shelters, weather, resources, volunteers, chat
from backend.app.api import government, medical, auth
from backend.app.services.rag_service import RAGService
from backend.app.core.config import settings
from backend.app.core.database import Base, engine
from backend.app.seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    print("SafeSphere Startup Initializations...")
    try:
        Base.metadata.create_all(bind=engine)
        seed_database()
    except Exception as e:
        print(f"Database initialization failed on startup: {e}")

    try:
        RAGService.initialize()
    except Exception as e:
        print(f"Failed to initialize RAG collection on startup: {e}")

    yield  # Application runs here

    print("SafeSphere shutdown.")

app = FastAPI(
    title="SafeSphere REST API Backend",
    description="Production-grade AI Disaster Management Engine powered by LangGraph, Gemini, and FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend requests (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production to match deployment domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind Routers
app.include_router(incidents.router, prefix="/api")
app.include_router(shelters.router, prefix="/api")  # Includes shelters & hospitals
app.include_router(weather.router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(volunteers.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(government.router, prefix="/api")
app.include_router(medical.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "Online",
        "service": "SafeSphere Disaster Response Platform",
        "version": "1.0.0",
        "api_documentation": f"{settings.BACKEND_URL}/docs"
    }
