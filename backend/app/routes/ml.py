from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.jwt import get_current_user
from ..models.usuario import Usuario
import httpx

router = APIRouter()

@router.post("/predict")
async def predict_financeiro(
    data: dict,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Faz predições usando o serviço ML
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://ml_service:5000/predict",
                json=data
            )
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao fazer predição: {str(e)}"
        ) 