import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router
from backend.schemas import HealthResponse
from backend.services.document_service import gemini_service
from document_utils.text_utils import parse_cors_origins


load_dotenv()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="LegalEase API",
    description=(
        "AI-powered legal document drafting API "
        "using Google Gemini."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

cors_origins = parse_cors_origins(
    os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:8501,"
            "http://127.0.0.1:8501"
        ),
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "OPTIONS",
    ],
    allow_headers=["*"],
)


# ============================================================
# ROUTES
# ============================================================

app.include_router(router)


# ============================================================
# ROOT
# ============================================================

@app.get(
    "/",
    tags=["System"],
)
def root():

    return {
        "service": "LegalEase API",
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health():

    return HealthResponse(
        status="ok",
        gemini_configured=gemini_service.configured,
        model=gemini_service.model_name,
    )