from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.history import router as history_router
from app.routers.products import router as products_router
from app.routers.shopping_items import router as shopping_items_router
from app.routers.voice import router as voice_router


app = FastAPI(
    title="Voice Shopping Assistant API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

ALLOWED_ORIGINS = [
    "https://voice-shopping-assistant-o0uxy51c3.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Security headers
# ---------------------------------------------------------


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

    return response


# ---------------------------------------------------------
# Generic 500 error
# ---------------------------------------------------------




# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(auth_router)
app.include_router(shopping_items_router)
app.include_router(products_router)
app.include_router(categories_router)
app.include_router(history_router)
app.include_router(voice_router)


# ---------------------------------------------------------
# Protected health endpoint
# ---------------------------------------------------------


@app.get("/health")
def health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.execute(text("SELECT 1")).scalar()

    return {
        "status": "ok",
        "database": result == 1,
    }


# ---------------------------------------------------------
# Public ping endpoint (no auth) — used by UptimeRobot
# to keep the free Render instance alive.
# ---------------------------------------------------------


@app.api_route("/ping", methods=["GET", "HEAD"])
def ping():
    return {"status": "pong"}
