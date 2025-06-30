from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.financeiro import Lancamento, Categoria, TipoLancamento
from app.schemas.lancamento import (
    LancamentoCreate, 
    LancamentoUpdate, 
    LancamentoResponse,
    LancamentoSummary
)
from app.services.cache import cache

router = APIRouter()

@router.get("/", response_model=List[LancamentoResponse])
async def list_lancamentos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[TipoLancamento] = None,
    categoria_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
) -> Any:
    """
    Retrieve lancamentos with filters
    """
    # Build cache key
    cache_key = f"lancamentos:{current_user.id}:{skip}:{limit}:{tipo}:{categoria_id}:{data_inicio}:{data_fim}"
    
    # Try to get from cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Build query
    query = select(Lancamento).where(Lancamento.user_id == current_user.id)
    
    if tipo:
        query = query.where(Lancamento.tipo == tipo)
    if categoria_id:
        query = query.where(Lancamento.categoria_id == categoria_id)
    if data_inicio:
        query = query.where(Lancamento.data_lancamento >= data_inicio)
    if data_fim:
        query = query.where(Lancamento.data_lancamento <= data_fim)
    
    query = query.offset(skip).limit(limit).order_by(Lancamento.data_lancamento.desc())
    
    result = await db.execute(query)
    lancamentos = result.scalars().all()
    
    # Convert to response format
    response_data = [LancamentoResponse.from_orm(l) for l in lancamentos]
    
    # Cache for 5 minutes
    cache.set(cache_key, response_data, ttl=timedelta(minutes=5))
    
    return response_data

@router.post("/", response_model=LancamentoResponse)
async def create_lancamento(
    *,
    db: AsyncSession = Depends(get_db),
    lancamento_in: LancamentoCreate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new lancamento
    """
    lancamento = Lancamento(
        **lancamento_in.dict(),
        user_id=current_user.id
    )
    
    db.add(lancamento)
    await db.commit()
    await db.refresh(lancamento)
    
    # Clear user's cache
    cache.delete(f"lancamentos:{current_user.id}:*")
    cache.delete(f"summary:{current_user.id}")
    
    return LancamentoResponse.from_orm(lancamento)

@router.get("/{lancamento_id}", response_model=LancamentoResponse)
async def get_lancamento(
    lancamento_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get lancamento by ID
    """
    result = await db.execute(
        select(Lancamento).where(
            and_(
                Lancamento.id == lancamento_id,
                Lancamento.user_id == current_user.id
            )
        )
    )
    lancamento = result.scalar_one_or_none()
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento not found")
    
    return LancamentoResponse.from_orm(lancamento)

@router.put("/{lancamento_id}", response_model=LancamentoResponse)
async def update_lancamento(
    *,
    db: AsyncSession = Depends(get_db),
    lancamento_id: int,
    lancamento_in: LancamentoUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update lancamento
    """
    result = await db.execute(
        select(Lancamento).where(
            and_(
                Lancamento.id == lancamento_id,
                Lancamento.user_id == current_user.id
            )
        )
    )
    lancamento = result.scalar_one_or_none()
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento not found")
    
    update_data = lancamento_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lancamento, field, value)
    
    await db.commit()
    await db.refresh(lancamento)
    
    # Clear cache
    cache.delete(f"lancamentos:{current_user.id}:*")
    cache.delete(f"summary:{current_user.id}")
    
    return LancamentoResponse.from_orm(lancamento)

@router.delete("/{lancamento_id}")
async def delete_lancamento(
    lancamento_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete lancamento
    """
    result = await db.execute(
        select(Lancamento).where(
            and_(
                Lancamento.id == lancamento_id,
                Lancamento.user_id == current_user.id
            )
        )
    )
    lancamento = result.scalar_one_or_none()
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lancamento not found")
    
    await db.delete(lancamento)
    await db.commit()
    
    # Clear cache
    cache.delete(f"lancamentos:{current_user.id}:*")
    cache.delete(f"summary:{current_user.id}")
    
    return {"message": "Lancamento deleted successfully"}

@router.get("/summary/stats", response_model=LancamentoSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    periodo_dias: int = Query(30, ge=1, le=365)
) -> Any:
    """
    Get financial summary for the user
    """
    cache_key = f"summary:{current_user.id}:{periodo_dias}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Calculate date range
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=periodo_dias)
    
    # Query data
    query = select(Lancamento).where(
        and_(
            Lancamento.user_id == current_user.id,
            Lancamento.data_lancamento >= data_inicio,
            Lancamento.data_lancamento <= data_fim
        )
    )
    
    result = await db.execute(query)
    lancamentos = result.scalars().all()
    
    # Calculate summary
    total_receitas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.RECEITA)
    total_despesas = sum(l.valor for l in lancamentos if l.tipo == TipoLancamento.DESPESA)
    saldo = total_receitas - total_despesas
    
    summary = LancamentoSummary(
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        saldo=saldo,
        total_lancamentos=len(lancamentos),
        periodo_dias=periodo_dias
    )
    
    # Cache for 10 minutes
    cache.set(cache_key, summary.dict(), ttl=timedelta(minutes=10))
    
    return summary 