from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes import router
from .models import HealthResponse
from .stream_processor import AsyncStreamProcessor

# Global stream processor instance
stream_processor = AsyncStreamProcessor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Event Management System Backend...")
    yield
    # Shutdown
    print("👋 Shutting down Event Management System Backend...")


# Create FastAPI app
app = FastAPI(
    title="Event Management System API",
    description="A full-stack event management system with natural language parsing and conflict detection",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["api"])

# Stream processing endpoints
@app.post("/api/stream/start")
async def start_stream():
    """Start the async stream processor"""
    stream_processor.start()
    return {"status": "started", "message": "Stream processing started"}

@app.post("/api/stream/stop")
async def stop_stream():
    """Stop the async stream processor"""
    stream_processor.stop()
    return {"status": "stopped", "message": "Stream processing stopped"}

@app.get("/api/stream/status")
async def get_stream_status():
    """Get the current status of the stream processor"""
    return stream_processor.status()


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="Event Management System API is running",
        version="1.0.0"
    )


@app.get("/docs", include_in_schema=False)
async def custom_docs():
    """Redirect to API documentation"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 