from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_user
from app.models.financeiro import MetaFinanceira, Categoria, Lancamento
from app.schemas.financeiro import (
    MetaFinanceiraCreate, 
    MetaFinanceiraResponse, 
    MetaFinanceiraUpdate,
    ResumoMetasResponse
)
from app.models.user import User
from sqlalchemy import func, and_, select, or_
from decimal import Decimal

router = APIRouter()

@router.get("/", response_model=List[MetaFinanceiraResponse])
async def listar_metas(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as metas financeiras do usuário
    """
    try:
        query = select(MetaFinanceira).where(MetaFinanceira.user_id == current_user.id)
        
        if status:
            query = query.where(MetaFinanceira.status == status)
        
        query = query.order_by(MetaFinanceira.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        metas = result.scalars().all()
        
        # Calcular campos calculados para cada meta
        metas_response = []
        for meta in metas:
            # Calcular progresso percentual
            progresso_percentual = (meta.valor_atual / meta.valor_meta * 100) if meta.valor_meta > 0 else 0
            progresso_percentual = min(progresso_percentual, 100)  # Máximo 100%
            
            # Calcular dias restantes
            hoje = datetime.now()
            dias_restantes = (meta.data_fim.replace(tzinfo=None) - hoje).days if meta.data_fim else 0
            
            # Carregar categoria se existir
            categoria = None
            if meta.categoria_id:
                query_cat = select(Categoria).where(Categoria.id == meta.categoria_id)
                result_cat = await db.execute(query_cat)
                categoria = result_cat.scalar_one_or_none()
            
            meta_dict = {
                **meta.__dict__,
                "progresso_percentual": round(progresso_percentual, 2),
                "dias_restantes": dias_restantes,
                "categoria": categoria
            }
            metas_response.append(meta_dict)
        
        return metas_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar metas: {str(e)}")

@router.post("/", response_model=MetaFinanceiraResponse)
async def criar_meta(
    meta: MetaFinanceiraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova meta financeira
    """
    try:
        # Validar se categoria existe (se informada)
        if meta.categoria_id:
            query_cat = select(Categoria).where(
                and_(
                    Categoria.id == meta.categoria_id,
                    Categoria.user_id == current_user.id
                )
            )
            result_cat = await db.execute(query_cat)
            categoria = result_cat.scalar_one_or_none()
            
            if not categoria:
                raise HTTPException(
                    status_code=400,
                    detail="Categoria não encontrada"
                )
        
        # Validar datas
        if meta.data_fim <= meta.data_inicio:
            raise HTTPException(
                status_code=400,
                detail="Data fim deve ser posterior à data início"
            )
        
        nova_meta = MetaFinanceira(
            **meta.dict(),
            user_id=current_user.id
        )
        db.add(nova_meta)
        await db.commit()
        await db.refresh(nova_meta)
        
        # Retornar com campos calculados
        progresso_percentual = (nova_meta.valor_atual / nova_meta.valor_meta * 100) if nova_meta.valor_meta > 0 else 0
        dias_restantes = (nova_meta.data_fim.replace(tzinfo=None) - datetime.now()).days
        
        meta_response = {
            **nova_meta.__dict__,
            "progresso_percentual": round(progresso_percentual, 2),
            "dias_restantes": dias_restantes,
            "categoria": None
        }
        
        return meta_response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar meta: {str(e)}")

@router.get("/{meta_id}", response_model=MetaFinanceiraResponse)
async def obter_meta(
    meta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma meta específica por ID
    """
    try:
        query = select(MetaFinanceira).where(
            and_(
                MetaFinanceira.id == meta_id,
                MetaFinanceira.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        meta = result.scalar_one_or_none()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        # Calcular campos calculados
        progresso_percentual = (meta.valor_atual / meta.valor_meta * 100) if meta.valor_meta > 0 else 0
        progresso_percentual = min(progresso_percentual, 100)
        dias_restantes = (meta.data_fim.replace(tzinfo=None) - datetime.now()).days if meta.data_fim else 0
        
        # Carregar categoria
        categoria = None
        if meta.categoria_id:
            query_cat = select(Categoria).where(Categoria.id == meta.categoria_id)
            result_cat = await db.execute(query_cat)
            categoria = result_cat.scalar_one_or_none()
        
        meta_response = {
            **meta.__dict__,
            "progresso_percentual": round(progresso_percentual, 2),
            "dias_restantes": dias_restantes,
            "categoria": categoria
        }
        
        return meta_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter meta: {str(e)}")

@router.put("/{meta_id}", response_model=MetaFinanceiraResponse)
async def atualizar_meta(
    meta_id: int,
    meta_update: MetaFinanceiraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma meta existente
    """
    try:
        # Buscar meta
        query = select(MetaFinanceira).where(
            and_(
                MetaFinanceira.id == meta_id,
                MetaFinanceira.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        meta = result.scalar_one_or_none()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        # Validar categoria se informada
        if meta_update.categoria_id:
            query_cat = select(Categoria).where(
                and_(
                    Categoria.id == meta_update.categoria_id,
                    Categoria.user_id == current_user.id
                )
            )
            result_cat = await db.execute(query_cat)
            categoria = result_cat.scalar_one_or_none()
            
            if not categoria:
                raise HTTPException(
                    status_code=400,
                    detail="Categoria não encontrada"
                )
        
        # Atualizar campos
        update_data = meta_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meta, field, value)
        
        await db.commit()
        await db.refresh(meta)
        
        # Retornar com campos calculados
        progresso_percentual = (meta.valor_atual / meta.valor_meta * 100) if meta.valor_meta > 0 else 0
        progresso_percentual = min(progresso_percentual, 100)
        dias_restantes = (meta.data_fim.replace(tzinfo=None) - datetime.now()).days if meta.data_fim else 0
        
        # Carregar categoria
        categoria = None
        if meta.categoria_id:
            query_cat = select(Categoria).where(Categoria.id == meta.categoria_id)
            result_cat = await db.execute(query_cat)
            categoria = result_cat.scalar_one_or_none()
        
        meta_response = {
            **meta.__dict__,
            "progresso_percentual": round(progresso_percentual, 2),
            "dias_restantes": dias_restantes,
            "categoria": categoria
        }
        
        return meta_response
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar meta: {str(e)}")

@router.delete("/{meta_id}")
async def deletar_meta(
    meta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma meta financeira
    """
    try:
        query = select(MetaFinanceira).where(
            and_(
                MetaFinanceira.id == meta_id,
                MetaFinanceira.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        meta = result.scalar_one_or_none()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        await db.delete(meta)
        await db.commit()
        
        return {"message": "Meta deletada com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar meta: {str(e)}")

@router.get("/resumo/estatisticas", response_model=ResumoMetasResponse)
async def obter_resumo_metas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém resumo estatístico das metas do usuário
    """
    try:
        # Query base
        query = select(MetaFinanceira).where(MetaFinanceira.user_id == current_user.id)
        result = await db.execute(query)
        todas_metas = result.scalars().all()
        
        total_metas = len(todas_metas)
        metas_ativas = len([m for m in todas_metas if m.status == "ATIVA"])
        metas_concluidas = len([m for m in todas_metas if m.status == "CONCLUIDA"])
        
        valor_total_metas = sum([m.valor_meta for m in todas_metas])
        valor_atual_total = sum([m.valor_atual for m in todas_metas])
        
        progresso_geral = (valor_atual_total / valor_total_metas * 100) if valor_total_metas > 0 else 0
        progresso_geral = min(progresso_geral, 100)
        
        return ResumoMetasResponse(
            total_metas=total_metas,
            metas_ativas=metas_ativas,
            metas_concluidas=metas_concluidas,
            valor_total_metas=valor_total_metas,
            valor_atual_total=valor_atual_total,
            progresso_geral=round(progresso_geral, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo: {str(e)}")

@router.post("/{meta_id}/atualizar-valor")
async def atualizar_valor_meta(
    meta_id: int,
    novo_valor: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza o valor atual de uma meta (para adicionar progresso)
    """
    try:
        query = select(MetaFinanceira).where(
            and_(
                MetaFinanceira.id == meta_id,
                MetaFinanceira.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        meta = result.scalar_one_or_none()
        
        if not meta:
            raise HTTPException(status_code=404, detail="Meta não encontrada")
        
        # Atualizar valor atual
        meta.valor_atual = novo_valor
        
        # Verificar se meta foi concluída
        if novo_valor >= meta.valor_meta and meta.status == "ATIVA":
            meta.status = "CONCLUIDA"
        
        await db.commit()
        await db.refresh(meta)
        
        return {"message": "Valor da meta atualizado com sucesso", "novo_valor": novo_valor}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar valor: {str(e)}") 