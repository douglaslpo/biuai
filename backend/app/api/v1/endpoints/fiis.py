from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api import deps
from app.models.fii import FII
from app.schemas.fii import FII as FIISchema, FIICreate, FIIUpdate, FIIAnalytics
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[FIISchema])
async def get_fiis(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Retorna a lista de FIIs do usuário atual.
    """
    query = select(FII).where(FII.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=FIISchema)
async def create_fii(
    fii_in: FIICreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Cria um novo FII para o usuário atual.
    """
    # Verifica se já existe um FII com o mesmo código
    query = select(FII).where(FII.codigo == fii_in.codigo, FII.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="FII já existe na sua carteira"
        )

    fii = FII(**fii_in.dict(), user_id=current_user.id)
    db.add(fii)
    await db.commit()
    await db.refresh(fii)
    return fii

@router.get("/{fii_id}", response_model=FIISchema)
async def get_fii(
    fii_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retorna um FII específico.
    """
    query = select(FII).where(FII.id == fii_id, FII.user_id == current_user.id)
    result = await db.execute(query)
    fii = result.scalar_one_or_none()
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return fii

@router.put("/{fii_id}", response_model=FIISchema)
async def update_fii(
    fii_id: int,
    fii_in: FIIUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Atualiza um FII específico.
    """
    query = select(FII).where(FII.id == fii_id, FII.user_id == current_user.id)
    result = await db.execute(query)
    fii = result.scalar_one_or_none()
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")

    # Verifica se o novo código já existe (se foi alterado)
    if fii_in.codigo != fii.codigo:
        query = select(FII).where(FII.codigo == fii_in.codigo, FII.user_id == current_user.id)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="FII com este código já existe na sua carteira"
            )

    for field, value in fii_in.dict(exclude_unset=True).items():
        setattr(fii, field, value)

    await db.commit()
    await db.refresh(fii)
    return fii

@router.delete("/{fii_id}")
async def delete_fii(
    fii_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Remove um FII específico.
    """
    query = select(FII).where(FII.id == fii_id, FII.user_id == current_user.id)
    result = await db.execute(query)
    fii = result.scalar_one_or_none()
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")

    await db.delete(fii)
    await db.commit()
    return {"message": "FII removido com sucesso"}

@router.get("/analytics", response_model=FIIAnalytics)
async def get_analytics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retorna análises da carteira de FIIs do usuário.
    """
    # Total investido
    query = select(func.sum(FII.preco_atual)).where(FII.user_id == current_user.id)
    result = await db.execute(query)
    total_investido = result.scalar() or 0

    # Total de FIIs
    query = select(func.count(FII.id)).where(FII.user_id == current_user.id)
    result = await db.execute(query)
    total_fiis = result.scalar()

    # DY médio
    query = select(func.avg(FII.dividend_yield)).where(FII.user_id == current_user.id)
    result = await db.execute(query)
    dy_medio = result.scalar() or 0

    # Rendimento mensal
    rendimento_mensal = total_investido * (dy_medio / 100) / 12

    return FIIAnalytics(
        total_investido=total_investido,
        rendimento_mensal=rendimento_mensal,
        dy_medio=dy_medio,
        total_fiis=total_fiis
    )

@router.get("/search", response_model=List[FIISchema])
async def search_fiis(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Busca FIIs por código ou nome.
    """
    query = select(FII).where(
        FII.user_id == current_user.id,
        (FII.codigo.ilike(f"%{q}%") | FII.nome.ilike(f"%{q}%"))
    )
    result = await db.execute(query)
    return result.scalars().all() 