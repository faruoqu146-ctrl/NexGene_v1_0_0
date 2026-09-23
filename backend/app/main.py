from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import hashlib
import secrets
import time
import threading
from collections import defaultdict

from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import create_engine, String, Float, DateTime, ForeignKey, Text, Boolean, select, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, sessionmaker

APP_VERSION = "1.0.0"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexgene.db")
# Render and some hosts provide postgres://; SQLAlchemy expects postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
SESSION_DAYS = 7
RATE_WINDOW = 60
MAX_LOGIN_ATTEMPTS = 40
MAX_REGISTER_ATTEMPTS = 40
MAX_RESET_ATTEMPTS = 5
MAX_VERIFY_ATTEMPTS = 10
MAX_CHECKIN_KEYS = 16
MAX_VALUE_LENGTH = 256
MAX_REQUEST_BYTES = 16 * 1024

# Production must never start with development secrets or insecure cookies.
if not DEV_MODE:
    if not SECRET_KEY or len(SECRET_KEY) < 32 or SECRET_KEY == "nexgene-dev-secret-change-me":
        raise RuntimeError("SECRET_KEY must be a strong random value of at least 32 characters when DEV_MODE=false")
    if not COOKIE_SECURE:
        raise RuntimeError("COOKIE_SECURE=true is required when DEV_MODE=false")
elif not SECRET_KEY:
    # Local-only fallback. It is deliberately not acceptable in production.
    SECRET_KEY = "nexgene-local-development-secret-only"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine)
pwd = CryptContext(
    schemes=["pbkdf2_sha256"],
    pbkdf2_sha256__default_rounds=600000,
    deprecated="auto",
)

# Used only to make login timing similar when an email does not exist.
DUMMY_PASSWORD_HASH = "$pbkdf2-sha256$600000$Z2ztPad0bs0Z41zrfW/N2Q$1WxGtpukLZ9IZ2mnl9Hc4Yr3dIyChQ1doJzIJ5hbVe8"

app = FastAPI(
    title="NexGene API",
    version=APP_VERSION,
    docs_url="/docs" if DEV_MODE else None,
    redoc_url="/redoc" if DEV_MODE else None,
    openapi_url="/openapi.json" if DEV_MODE else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    length = request.headers.get("content-length")
    if length:
        try:
            if int(length) > MAX_REQUEST_BYTES:
                return Response("Request body too large", status_code=413)
        except ValueError:
            return Response("Invalid Content-Length", status_code=400)
    return await call_next(request)


class Base(DeclarativeBase):
    pass
