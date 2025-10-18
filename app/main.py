"""Main FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import init_redis, close_redis
from app.api.api_v1.api import api_router
from app.utils.logging import configure_logging


# Configure structured logging
configure_logging()
logger = structlog.get_logger()


# Initialize Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=str(settings.SENTRY_DSN),
        integrations=[FastApiIntegration(auto_enable=False)],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting application", app_name=settings.APP_NAME)

    try:
        # Initialize database with timeout
        try:
            await init_db()
            logger.info("Database initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}", exc_info=True)
            logger.info("App will continue without database (some features may not work)")

        # Initialize Redis with timeout
        try:
            await init_redis()
            logger.info("Redis initialized")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}", exc_info=True)
            logger.info("App will continue without Redis (caching disabled)")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down application")
        try:
            await close_db()
        except Exception as e:
            logger.warning(f"Database close failed: {e}")
        
        try:
            await close_redis()
        except Exception as e:
            logger.warning(f"Redis close failed: {e}")
        
        logger.info("Application shutdown complete")


# Request ID middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# Timing middleware
class TimingMiddleware(BaseHTTPMiddleware):
    """Add request timing."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A production-ready, secure, scalable quiz application backend",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from app.core.database import engine
    from app.core.redis import get_redis

    health = {"status": "healthy", "checks": {}}

    try:
        # Check database
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    try:
        # Check Redis
        redis_client = await get_redis()
        await redis_client.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {str(e)}"
        health["status"] = "unhealthy"

    return health


# Metrics endpoint for Prometheus
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    if not settings.PROMETHEUS_METRICS_ENABLED:
        return JSONResponse(status_code=404, content={"error": "Metrics not enabled"})

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Serve frontend static files (if they exist)
static_dir = Path(__file__).parent / "static"
if static_dir.exists() and static_dir.is_dir():
    # Mount static assets (JS, CSS, images, etc.)
    app.mount(
        "/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets"
    )

    # Serve index.html for all frontend routes (SPA routing)
    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_frontend(full_path: str):
        """Serve React frontend for all non-API routes."""
        # If path starts with /api, /docs, /openapi, /health, /metrics - skip
        if full_path.startswith(("api/", "docs", "openapi", "health", "metrics")):
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Serve index.html for all other routes (React Router handles the rest)
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({"error": "Frontend not built"}, status_code=404)

else:
    # Fallback if frontend not built
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs_url": "/docs",
            "openapi_url": "/openapi.json",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
