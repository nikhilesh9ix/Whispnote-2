#!/usr/bin/env python3
"""
Mock Swecha Corpus API Server
============================

This is a development server that implements the missing Swecha corpus API endpoints
for local testing and development of WhispNote integration.

Run with: uv run python mock_swecha_api.py
API will be available at: http://localhost:8080

This simulates the endpoints that will eventually be available at:
https://api.corpus.swecha.org
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Mock Swecha Telugu Corpus API",
    description="Development server simulating Swecha corpus collection endpoints",
    version="0.1.0-mock",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for development
corpus_data: Dict[str, Any] = {
    "texts": [],
    "audio_transcriptions": [],
    "stats": {
        "total_texts": 0,
        "total_audio_files": 0,
        "total_transcriptions": 0,
        "languages": {"te": 0, "hi": 0, "en": 0},
        "last_updated": datetime.now().isoformat(),
    },
}


# Pydantic models
class TextContribution(BaseModel):
    text: str
    language_code: str = "te"
    metadata: Optional[Dict] = None


class ContributionResponse(BaseModel):
    success: bool
    message: str
    contribution_id: Optional[str] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class StatsResponse(BaseModel):
    total_contributions: int
    total_texts: int
    total_audio_files: int
    languages: Dict[str, int]
    last_updated: str


# Root endpoint
@app.get("/")
async def root():
    """Welcome message and API information"""
    return {
        "message": "Welcome to Telugu Corpus Collections API (Mock Server)",
        "version": "0.1.0-mock",
        "docs": "/docs",
        "status": "development",
        "note": "This is a mock server for WhispNote development",
    }


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """API health status"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="0.1.0-mock",
    )


# Statistics endpoint
@app.get("/stats", response_model=StatsResponse)
async def get_corpus_stats():
    """Get corpus statistics"""
    return StatsResponse(
        total_contributions=len(corpus_data["texts"])
        + len(corpus_data["audio_transcriptions"]),
        total_texts=len(corpus_data["texts"]),
        total_audio_files=len(corpus_data["audio_transcriptions"]),
        languages=corpus_data["stats"]["languages"],
        last_updated=corpus_data["stats"]["last_updated"],
    )


# Text contribution endpoint
@app.post("/contribute", response_model=ContributionResponse)
async def contribute_text(contribution: TextContribution):
    """Contribute text data to the corpus"""
    try:
        # Generate contribution ID
        contribution_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Store contribution
        contribution_data = {
            "id": contribution_id,
            "text": contribution.text,
            "language_code": contribution.language_code,
            "metadata": contribution.metadata or {},
            "timestamp": timestamp,
            "type": "text",
        }

        corpus_data["texts"].append(contribution_data)
        corpus_data["stats"]["languages"][contribution.language_code] = (
            corpus_data["stats"]["languages"].get(contribution.language_code, 0) + 1
        )
        corpus_data["stats"]["total_texts"] = len(corpus_data["texts"])
        corpus_data["stats"]["last_updated"] = timestamp

        logger.info(f"Text contribution received: {contribution_id}")

        return ContributionResponse(
            success=True,
            message="Text contribution received successfully",
            contribution_id=contribution_id,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"Error processing text contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process contribution: {str(e)}",
        )


# Audio transcription contribution endpoint
@app.post("/contribute/audio", response_model=ContributionResponse)
async def contribute_audio_transcription(
    audio: UploadFile = File(...),
    transcription: str = Form(...),
    language_code: str = Form("te"),
    metadata: Optional[str] = Form(None),
):
    """Contribute audio file with transcription"""
    try:
        # Generate contribution ID
        contribution_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Parse metadata if provided
        metadata_dict = {}
        if metadata:
            with contextlib.suppress(json.JSONDecodeError):
                metadata_dict = json.loads(metadata)

        # Store contribution (in real implementation, would save audio file)
        contribution_data = {
            "id": contribution_id,
            "audio_filename": audio.filename,
            "audio_size": audio.size,
            "transcription": transcription,
            "language_code": language_code,
            "metadata": metadata_dict,
            "timestamp": timestamp,
            "type": "audio_transcription",
        }

        corpus_data["audio_transcriptions"].append(contribution_data)
        corpus_data["stats"]["languages"][language_code] = (
            corpus_data["stats"]["languages"].get(language_code, 0) + 1
        )
        corpus_data["stats"]["total_audio_files"] = len(
            corpus_data["audio_transcriptions"]
        )
        corpus_data["stats"]["last_updated"] = timestamp

        logger.info(f"Audio transcription contribution received: {contribution_id}")

        return ContributionResponse(
            success=True,
            message="Audio transcription contribution received successfully",
            contribution_id=contribution_id,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"Error processing audio contribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process audio contribution: {str(e)}",
        )


# Corpus data access endpoints
@app.get("/corpus")
async def get_corpus_data():
    """Get corpus data overview"""
    return {
        "total_contributions": len(corpus_data["texts"])
        + len(corpus_data["audio_transcriptions"]),
        "text_contributions": len(corpus_data["texts"]),
        "audio_contributions": len(corpus_data["audio_transcriptions"]),
        "languages": corpus_data["stats"]["languages"],
        "last_updated": corpus_data["stats"]["last_updated"],
    }


@app.get("/texts")
async def get_texts(limit: int = 10, offset: int = 0, language: Optional[str] = None):
    """Get text contributions"""
    texts = corpus_data["texts"]

    # Filter by language if specified
    if language:
        texts = [t for t in texts if t["language_code"] == language]

    # Apply pagination
    total = len(texts)
    texts = texts[offset : offset + limit]

    return {
        "texts": texts,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/audio")
async def get_audio_transcriptions(
    limit: int = 10, offset: int = 0, language: Optional[str] = None
):
    """Get audio transcription contributions"""
    audio_data = corpus_data["audio_transcriptions"]

    # Filter by language if specified
    if language:
        audio_data = [a for a in audio_data if a["language_code"] == language]

    # Apply pagination
    total = len(audio_data)
    audio_data = audio_data[offset : offset + limit]

    return {
        "audio_transcriptions": audio_data,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


# Search endpoint
@app.get("/search")
async def search_corpus(
    query: str,
    language: Optional[str] = None,
    limit: int = 10,
):
    """Search corpus data"""
    results = []

    # Search in texts
    for text_data in corpus_data["texts"]:
        if language and text_data["language_code"] != language:
            continue
        if query.lower() in text_data["text"].lower():
            results.append({"type": "text", "data": text_data})

    # Search in transcriptions
    for audio_data in corpus_data["audio_transcriptions"]:
        if language and audio_data["language_code"] != language:
            continue
        if query.lower() in audio_data["transcription"].lower():
            results.append({"type": "audio_transcription", "data": audio_data})

    return {
        "query": query,
        "language": language,
        "results": results[:limit],
        "total_found": len(results),
    }


# Authentication simulation endpoints
@app.get("/auth")
async def auth_info():
    """Authentication information"""
    return {
        "message": "Mock authentication - no token required for development",
        "token_required": False,
        "development_mode": True,
    }


@app.get("/user")
async def get_user_info():
    """Get current user information (mock)"""
    return {
        "user_id": "mock_user_123",
        "username": "developer",
        "email": "dev@example.com",
        "contributions": len(corpus_data["texts"])
        + len(corpus_data["audio_transcriptions"]),
        "role": "contributor",
    }


# Admin endpoints for development
@app.get("/admin/reset")
async def reset_corpus():
    """Reset all corpus data (development only)"""
    global corpus_data
    corpus_data = {
        "texts": [],
        "audio_transcriptions": [],
        "stats": {
            "total_texts": 0,
            "total_audio_files": 0,
            "total_transcriptions": 0,
            "languages": {"te": 0, "hi": 0, "en": 0},
            "last_updated": datetime.now().isoformat(),
        },
    }
    return {
        "message": "Corpus data reset successfully",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/admin/export")
async def export_corpus():
    """Export all corpus data (development only)"""
    return corpus_data


if __name__ == "__main__":
    print("🚀 Starting Mock Swecha Corpus API Server")
    print("📡 Server will be available at: http://localhost:8080")
    print("📚 API Documentation: http://localhost:8080/docs")
    print("🔧 This is a development server simulating Swecha API endpoints")
    print("⚠️  Data is stored in memory and will be lost when server stops")
    print()

    uvicorn.run(
        "mock_swecha_api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
