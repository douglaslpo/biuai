from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.fii import FII, FIICreate, FIIUpdate, FIIAnalytics
from app.services.ai_insights_service import get_fii_insights

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/", response_model=List[FII])
async def list_fiis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista todos os FIIs do usuário"""
    return db.query(FII).filter(FII.user_id == current_user.id).all()

@router.post("/", response_model=FII)
async def create_fii(
    fii: FIICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cria um novo FII"""
    db_fii = FII(**fii.dict(), user_id=current_user.id)
    db.add(db_fii)
    db.commit()
    db.refresh(db_fii)
    return db_fii

@router.get("/{fii_id}", response_model=FII)
async def get_fii(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém um FII específico"""
    fii = db.query(FII).filter(
        FII.id == fii_id,
        FII.user_id == current_user.id
    ).first()
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return fii

@router.put("/{fii_id}", response_model=FII)
async def update_fii(
    fii_id: int,
    fii_update: FIIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza um FII"""
    db_fii = db.query(FII).filter(
        FII.id == fii_id,
        FII.user_id == current_user.id
    ).first()
    if not db_fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    
    for key, value in fii_update.dict().items():
        setattr(db_fii, key, value)
    
    db.commit()
    db.refresh(db_fii)
    return db_fii

@router.delete("/{fii_id}")
async def delete_fii(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove um FII"""
    db_fii = db.query(FII).filter(
        FII.id == fii_id,
        FII.user_id == current_user.id
    ).first()
    if not db_fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    
    db.delete(db_fii)
    db.commit()
    return {"message": "FII removido com sucesso"}

@router.get("/analytics/summary", response_model=FIIAnalytics)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém análises dos FIIs do usuário"""
    fiis = db.query(FII).filter(FII.user_id == current_user.id).all()
    
    total_investido = sum(fii.preco_atual for fii in fiis)
    rendimento_mensal = sum(
        (fii.preco_atual * fii.dividend_yield / 100) 
        for fii in fiis 
        if fii.dividend_yield
    )
    dy_medio = (
        sum(fii.dividend_yield for fii in fiis if fii.dividend_yield) / 
        len([fii for fii in fiis if fii.dividend_yield])
    ) if fiis else 0
    
    return FIIAnalytics(
        total_investido=total_investido,
        rendimento_mensal=rendimento_mensal,
        dy_medio=dy_medio,
        total_fiis=len(fiis)
    )

@router.get("/{fii_id}/insights")
async def get_insights(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém insights de IA para um FII específico"""
    fii = db.query(FII).filter(
        FII.id == fii_id,
        FII.user_id == current_user.id
    ).first()
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    
    return await get_fii_insights(fii) 