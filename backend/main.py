from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings

import logging
from pythonjsonlogger import json
from prometheus_fastapi_instrumentator import Instrumentator

# Configure JSON logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = json.JsonFormatter('%(timestamp)s %(levelname)s %(message)s %(module)s %(funcName)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="OrderGuard AI - COD order verification and risk management API"
)

# Instrument the app for Prometheus metrics
Instrumentator().instrument(app).expose(app)


# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

# We will include routers here once we build the api endpoints
from app.api import orders, auth
app.include_router(auth.router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])
app.include_router(orders.router, prefix=settings.API_V1_STR + "/orders", tags=["orders"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
