from fastapi import APIRouter

from app.api.v1.endpoints import predictions, training

api_router = APIRouter()
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(training.router, prefix="/training", tags=["training"]) 