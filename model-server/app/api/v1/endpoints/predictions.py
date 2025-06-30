from typing import Any
from fastapi import APIRouter
import pandas as pd

from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.prediction import PredictionService

router = APIRouter()
prediction_service = PredictionService()

@router.post("/", response_model=PredictionOutput)
async def predict(
    *,
    input_data: PredictionInput
) -> Any:
    """
    Make predictions for future financial transactions.
    """
    # Make predictions
    predictions = await prediction_service.predict(
        user_id=input_data.user_id,
        start_date=input_data.start_date,
        end_date=input_data.end_date,
        categories=input_data.categories
    )
    
    return predictions 