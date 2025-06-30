from typing import Any
from fastapi import APIRouter, HTTPException
import pandas as pd

from app.schemas.prediction import TrainingInput, TrainingOutput
from app.services.prediction import PredictionService

router = APIRouter()
prediction_service = PredictionService()

@router.post("/", response_model=TrainingOutput)
async def train_model(
    *,
    input_data: TrainingInput
) -> Any:
    """
    Train a new model using historical data.
    """
    try:
        # Convert input data to DataFrame
        df = pd.DataFrame(input_data.data)
        
        # Validate required columns
        required_columns = ['data', 'valor', 'categoria', 'tipo']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Train model
        training_result = await prediction_service.train_model(
            df=df,
            model_params=input_data.model_params
        )
        
        return training_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 