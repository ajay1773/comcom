from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat
from app.services.db.seeder import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and run seeding on startup."""
    from app.services.db.db import db_service
    await db_service.init_db()
    await seed_database()
    yield

app = FastAPI(title="ComCom API", description="A simple chat API", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ComCom API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }
