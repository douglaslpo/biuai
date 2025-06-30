from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_user
from app.models.financeiro import Lancamento, Categoria
from app.schemas.financeiro import LancamentoCreate, LancamentoResponse, CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.models.user import User
from sqlalchemy import func, and_, select
from decimal import Decimal

router = APIRouter()

# ===========================================
# ROTAS DE CATEGORIAS (DEVEM VIR PRIMEIRO)
# ===========================================

@router.get("/categorias", response_model=List[CategoriaResponse])
async def listar_categorias(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todas as categorias do usuário com filtros opcionais
    """
    try:
        query = select(Categoria).where(Categoria.user_id == current_user.id)
        
        if tipo:
            query = query.where(Categoria.tipo == tipo)
        
        query = query.order_by(Categoria.nome).offset(skip).limit(limit)
        result = await db.execute(query)
        categorias = result.scalars().all()
        
        return categorias
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar categorias: {str(e)}")

@router.post("/categorias", response_model=CategoriaResponse)
async def criar_categoria(
    categoria: CategoriaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma nova categoria financeira
    """
    try:
        # Verificar se já existe categoria com esse nome para o usuário
        query = select(Categoria).where(
            and_(
                Categoria.user_id == current_user.id,
                Categoria.nome == categoria.nome
            )
        )
        result = await db.execute(query)
        categoria_existente = result.scalar_one_or_none()
        
        if categoria_existente:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma categoria com este nome"
            )
        
        nova_categoria = Categoria(
            **categoria.dict(),
            user_id=current_user.id
        )
        db.add(nova_categoria)
        await db.commit()
        await db.refresh(nova_categoria)
        return nova_categoria
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar categoria: {str(e)}")

@router.get("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def obter_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém uma categoria específica por ID
    """
    try:
        query = select(Categoria).where(
            and_(
                Categoria.id == categoria_id,
                Categoria.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        categoria = result.scalar_one_or_none()
        
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        return categoria
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter categoria: {str(e)}")

@router.put("/categorias/{categoria_id}", response_model=CategoriaResponse)
async def atualizar_categoria(
    categoria_id: int,
    categoria_update: CategoriaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza uma categoria existente
    """
    try:
        # Buscar categoria
        query = select(Categoria).where(
            and_(
                Categoria.id == categoria_id,
                Categoria.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        categoria = result.scalar_one_or_none()
        
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        # Verificar se novo nome já existe (se estiver sendo alterado)
        if categoria_update.nome and categoria_update.nome != categoria.nome:
            query_nome = select(Categoria).where(
                and_(
                    Categoria.user_id == current_user.id,
                    Categoria.nome == categoria_update.nome,
                    Categoria.id != categoria_id
                )
            )
            result_nome = await db.execute(query_nome)
            categoria_nome_existente = result_nome.scalar_one_or_none()
            
            if categoria_nome_existente:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe uma categoria com este nome"
                )
        
        # Atualizar campos
        update_data = categoria_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(categoria, field, value)
        
        await db.commit()
        await db.refresh(categoria)
        return categoria
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar categoria: {str(e)}")

@router.delete("/categorias/{categoria_id}")
async def deletar_categoria(
    categoria_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deleta uma categoria e desvincula lançamentos associados
    """
    try:
        # Buscar categoria
        query = select(Categoria).where(
            and_(
                Categoria.id == categoria_id,
                Categoria.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        categoria = result.scalar_one_or_none()
        
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        
        # Desvincular lançamentos desta categoria (definir categoria_id como NULL)
        query_lancamentos = select(Lancamento).where(Lancamento.categoria_id == categoria_id)
        result_lancamentos = await db.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        for lancamento in lancamentos:
            lancamento.categoria_id = None
        
        # Deletar categoria
        await db.delete(categoria)
        await db.commit()
        
        return {
            "message": "Categoria deletada com sucesso",
            "lancamentos_desvinculados": len(lancamentos)
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar categoria: {str(e)}")

@router.get("/categorias/stats/usage")
async def estatisticas_uso_categorias(
    periodo_dias: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas de uso das categorias
    """
    try:
        data_limite = datetime.now() - timedelta(days=periodo_dias)
        
        # Buscar todas as categorias do usuário
        query_categorias = select(Categoria).where(Categoria.user_id == current_user.id)
        result_categorias = await db.execute(query_categorias)
        categorias = result_categorias.scalars().all()
        
        # Buscar lançamentos do período
        query_lancamentos = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= data_limite
            )
        )
        result_lancamentos = await db.execute(query_lancamentos)
        lancamentos = result_lancamentos.scalars().all()
        
        # Calcular estatísticas por categoria
        stats_por_categoria = {}
        lancamentos_sem_categoria = 0
        
        for lancamento in lancamentos:
            if lancamento.categoria_id:
                if lancamento.categoria_id not in stats_por_categoria:
                    stats_por_categoria[lancamento.categoria_id] = {
                        "quantidade": 0,
                        "total_valor": 0
                    }
                stats_por_categoria[lancamento.categoria_id]["quantidade"] += 1
                stats_por_categoria[lancamento.categoria_id]["total_valor"] += abs(lancamento.valor)
            else:
                lancamentos_sem_categoria += 1
        
        # Preparar resposta
        categorias_com_stats = []
        for categoria in categorias:
            stats = stats_por_categoria.get(categoria.id, {"quantidade": 0, "total_valor": 0})
            categorias_com_stats.append({
                "id": categoria.id,
                "nome": categoria.nome,
                "tipo": categoria.tipo,
                "quantidade_uso": stats["quantidade"],
                "total_valor": stats["total_valor"]
            })
        
        return {
            "periodo_dias": periodo_dias,
            "categorias": categorias_com_stats,
            "lancamentos_sem_categoria": lancamentos_sem_categoria,
            "total_categorias": len(categorias)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

# ===========================================
# ROTAS DE LANÇAMENTOS
# ===========================================

@router.get("/summary/stats")
async def get_summary(
    periodo_dias: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas resumidas para o dashboard
    """
    try:
        # Calcular período
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        # Buscar lançamentos do período
        query = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= data_inicio,
                Lancamento.data_lancamento <= data_fim
            )
        )
        result = await db.execute(query)
        lancamentos = result.scalars().all()
        
        # Calcular totais
        total_receitas = sum(l.valor for l in lancamentos if l.tipo == "RECEITA")
        total_despesas = sum(abs(l.valor) for l in lancamentos if l.tipo == "DESPESA")
        saldo = total_receitas - total_despesas
        
        return {
            "total_receitas": float(total_receitas),
            "total_despesas": float(total_despesas),
            "saldo": float(saldo),
            "total_lancamentos": len(lancamentos),
            "periodo_dias": periodo_dias
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/analytics")
async def get_dashboard_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna dados analíticos para gráficos do dashboard
    """
    try:
        # Evolução mensal dos últimos 12 meses
        doze_meses = datetime.now() - timedelta(days=365)
        
        # Buscar todos os lançamentos do usuário nos últimos 12 meses
        query = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= doze_meses
            )
        ).order_by(Lancamento.data_lancamento)
        
        result = await db.execute(query)
        lancamentos = result.scalars().all()
        
        # Processar evolução mensal
        evolucao_mensal = {}
        for l in lancamentos:
            mes_key = l.data_lancamento.strftime("%Y-%m")
            if mes_key not in evolucao_mensal:
                evolucao_mensal[mes_key] = {"receitas": 0, "despesas": 0}
            
            if l.tipo == "RECEITA":
                evolucao_mensal[mes_key]["receitas"] += l.valor
            else:
                evolucao_mensal[mes_key]["despesas"] += abs(l.valor)
        
        # Converter para lista
        evolucao_lista = []
        for mes, dados in sorted(evolucao_mensal.items()):
            evolucao_lista.append({
                "mes": mes,
                "receitas": dados["receitas"],
                "despesas": dados["despesas"],
                "saldo": dados["receitas"] - dados["despesas"]
            })
        
        # Distribuição por categoria (últimos 30 dias)
        trinta_dias = datetime.now() - timedelta(days=30)
        
        query_recentes = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= trinta_dias
            )
        )
        result = await db.execute(query_recentes)
        lancamentos_recentes = result.scalars().all()
        
        # Processar distribuição por tipo
        distribuicao = {"RECEITA": {"quantidade": 0, "total": 0}, "DESPESA": {"quantidade": 0, "total": 0}}
        for l in lancamentos_recentes:
            distribuicao[l.tipo]["quantidade"] += 1
            distribuicao[l.tipo]["total"] += abs(l.valor)
        
        distribuicao_lista = [
            {
                "tipo": tipo,
                "quantidade": dados["quantidade"],
                "total": dados["total"]
            }
            for tipo, dados in distribuicao.items()
        ]
        
        # Lançamentos recentes para display
        lancamentos_recentes_display = []
        for l in sorted(lancamentos_recentes, key=lambda x: x.data_lancamento, reverse=True)[:10]:
            lancamentos_recentes_display.append({
                "id": l.id,
                "descricao": l.descricao,
                "valor": float(l.valor),
                "tipo": l.tipo,
                "data_lancamento": l.data_lancamento.isoformat()
            })
        
        return {
            "evolucao_mensal": evolucao_lista,
            "distribuicao_categoria": distribuicao_lista,
            "lancamentos_recentes": lancamentos_recentes_display
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=LancamentoResponse)
async def criar_lancamento(
    lancamento: LancamentoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo lançamento financeiro
    """
    try:
        novo_lancamento = Lancamento(
            **lancamento.dict(),
            user_id=current_user.id
        )
        db.add(novo_lancamento)
        await db.commit()
        await db.refresh(novo_lancamento)
        return novo_lancamento
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[LancamentoResponse])
async def listar_lancamentos(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista lançamentos financeiros com filtros opcionais
    """
    try:
        query = select(Lancamento).where(Lancamento.user_id == current_user.id)

        if tipo:
            query = query.where(Lancamento.tipo == tipo)
        
        if data_inicio:
            query = query.where(Lancamento.data_lancamento >= data_inicio)
        
        if data_fim:
            query = query.where(Lancamento.data_lancamento <= data_fim)

        query = query.order_by(Lancamento.data_lancamento.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lancamento_id}", response_model=LancamentoResponse)
async def obter_lancamento(
    lancamento_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém um lançamento específico por ID
    """
    query = select(Lancamento).where(
        and_(
            Lancamento.id == lancamento_id,
            Lancamento.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    lancamento = result.scalar_one_or_none()
    
    if not lancamento:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    return lancamento

@router.delete("/{lancamento_id}")
async def deletar_lancamento(
    lancamento_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove um lançamento financeiro
    """
    try:
        query = select(Lancamento).where(
            and_(
                Lancamento.id == lancamento_id,
                Lancamento.user_id == current_user.id
            )
        )
        result = await db.execute(query)
        lancamento = result.scalar_one_or_none()
        
        if not lancamento:
            raise HTTPException(status_code=404, detail="Lançamento não encontrado")
        
        await db.delete(lancamento)
        await db.commit()
        return {"message": "Lançamento removido com sucesso"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
@router.get("/import/siog")
async def import_siog_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importa dados do dataset SIOG para demonstração
    """
    try:
        # Dados de exemplo baseados no dataset SIOG
        dados_exemplo = [
            {
                "descricao": "Saneamento de Goiás S.A - Água",
                "valor": -510.42,
                "tipo": "DESPESA",
                "data_lancamento": datetime(2025, 1, 25)
            },
            {
                "descricao": "Associação Jardins Paris - Condomínio",
                "valor": -2085.71,
                "tipo": "DESPESA", 
                "data_lancamento": datetime(2025, 1, 5)
            },
            {
                "descricao": "Estrutural Madeiras - Reforma",
                "valor": -2030.80,
                "tipo": "DESPESA",
                "data_lancamento": datetime(2025, 1, 5)
            },
            {
                "descricao": "Receita de Vendas - Janeiro",
                "valor": 15000.00,
                "tipo": "RECEITA",
                "data_lancamento": datetime(2025, 1, 1)
            },
            {
                "descricao": "Prestação de Serviços",
                "valor": 8500.00,
                "tipo": "RECEITA",
                "data_lancamento": datetime(2025, 1, 15)
            }
        ]
        
        count = 0
        for dados in dados_exemplo:
            # Verificar se já existe
            query = select(Lancamento).where(
                and_(
                    Lancamento.user_id == current_user.id,
                    Lancamento.descricao == dados["descricao"]
                )
            )
            result = await db.execute(query)
            existe = result.scalar_one_or_none()
            
            if not existe:
                lancamento = Lancamento(**dados, user_id=current_user.id)
                db.add(lancamento)
                count += 1
        
        await db.commit()
        return {"message": f"{count} lançamentos importados com sucesso do dataset SIOG"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/evolution")
async def get_evolution_data(
    meses: int = 6,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna dados de evolução temporal para gráficos
    """
    try:
        # Calcular período
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=meses * 30)
        
        # Buscar lançamentos do período
        query = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= data_inicio,
                Lancamento.data_lancamento <= data_fim
            )
        ).order_by(Lancamento.data_lancamento)
        
        result = await db.execute(query)
        lancamentos = result.scalars().all()
        
        # Agrupar por mês
        evolucao_mensal = {}
        for l in lancamentos:
            mes_key = l.data_lancamento.strftime("%m/%y")
            if mes_key not in evolucao_mensal:
                evolucao_mensal[mes_key] = {"receitas": 0, "despesas": 0}
            
            if l.tipo == "RECEITA":
                evolucao_mensal[mes_key]["receitas"] += float(l.valor)
            else:
                evolucao_mensal[mes_key]["despesas"] += float(abs(l.valor))
        
        # Gerar labels e dados para os últimos meses
        labels = []
        receitas = []
        despesas = []
        
        now = datetime.now()
        for i in range(meses):
            mes_data = now - timedelta(days=(meses - 1 - i) * 30)
            mes_key = mes_data.strftime("%m/%y")
            labels.append(mes_key)
            
            if mes_key in evolucao_mensal:
                receitas.append(evolucao_mensal[mes_key]["receitas"])
                despesas.append(evolucao_mensal[mes_key]["despesas"])
            else:
                receitas.append(0)
                despesas.append(0)
        
        return {
            "labels": labels,
            "receitas": receitas,
            "despesas": despesas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/categories")
async def get_category_data(
    periodo_dias: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna dados de distribuição por categoria para gráficos
    """
    try:
        # Calcular período
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=periodo_dias)
        
        # Buscar lançamentos do período
        query = select(Lancamento).where(
            and_(
                Lancamento.user_id == current_user.id,
                Lancamento.data_lancamento >= data_inicio,
                Lancamento.data_lancamento <= data_fim
            )
        )
        
        result = await db.execute(query)
        lancamentos = result.scalars().all()
        
        # Calcular totais por tipo
        total_receitas = sum(float(l.valor) for l in lancamentos if l.tipo == "RECEITA")
        total_despesas = sum(float(abs(l.valor)) for l in lancamentos if l.tipo == "DESPESA")
        
        return {
            "labels": ["Receitas", "Despesas"],
            "values": [total_receitas, total_despesas]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 