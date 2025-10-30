# backend_v2/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.api.v1 import auth, recruiter, candidate

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the application.
    Connects to MongoDB on startup and disconnects on shutdown.
    """
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="backend_v2 Assessment API",
    description="API for the technical assessment platform. \n\n"
                "Handles user auth (Candidate, Recruiter), test creation, "
                "and assessment session management.",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Middleware ---
if settings.FRONTEND_URL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    print("Warning: FRONTEND_URL not set. CORS is not configured.")

# --- API Routers ---
api_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(recruiter.router, prefix=api_prefix)
app.include_router(candidate.router, prefix=api_prefix)

@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"message": "Welcome to the backend_v2 API!", "status": "ok"}

if __name__ == "__main__":
    # This is for local debugging, not for production
    uvicorn.run(app, host="0.0.0.0", port=8000)

