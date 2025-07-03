from datetime import date
from typing import List, Dict, Any
from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    user_id: int
    start_date: date
    end_date: date
    categories: List[str] = None

class PredictionOutput(BaseModel):
    predictions: Dict[str, float]
    confidence: Dict[str, float]
    feature_importance: Dict[str, float]
    model_version: str

class TrainingInput(BaseModel):
    data: List[Dict[str, Any]]
    model_params: Dict[str, Any] = None

class TrainingOutput(BaseModel):
    model_version: str
    metrics: Dict[str, float]
    training_time: float
    feature_importance: Dict[str, float] 