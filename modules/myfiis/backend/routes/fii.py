"""
Rotas da API para o módulo MyFIIs.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
from datetime import timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from ..models.fii import FII
from ..schemas.fii import FIICreate, FIIUpdate, FIIResponse
from ..services.fii_service import FIIService
from ...ai.services.fii_analyzer import FIIAnalyzer

router = APIRouter()
fii_analyzer = FIIAnalyzer()

@router.get("/myfiis", response_model=List[FIIResponse])
async def list_fiis(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    segmento: Optional[str] = None
):
    """Lista todos os FIIs disponíveis."""
    service = FIIService(db)
    fiis = await service.list_fiis(
        skip=skip,
        limit=limit,
        segmento=segmento
    )
    return fiis

@router.post("/myfiis", response_model=FIIResponse)
async def create_fii(
    fii: FIICreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria um novo FII."""
    service = FIIService(db)
    return await service.create_fii(fii)

@router.get("/myfiis/{fii_id}", response_model=FIIResponse)
async def get_fii(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém detalhes de um FII específico."""
    service = FIIService(db)
    fii = await service.get_fii(fii_id=fii_id, user_id=current_user.id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return fii

@router.put("/myfiis/{fii_id}", response_model=FIIResponse)
async def update_fii(
    fii_id: int,
    fii_update: FIIUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza um FII existente."""
    service = FIIService(db)
    fii = await service.update_fii(fii_id, fii_update)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return fii

@router.delete("/myfiis/{fii_id}")
async def delete_fii(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove um FII."""
    service = FIIService(db)
    if not await service.delete_fii(fii_id):
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return {"message": "FII removido com sucesso"}

@router.post("/myfiis/{fii_id}/favorito")
async def toggle_favorito(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Alterna o status de favorito de um FII."""
    service = FIIService(db)
    fii = await service.toggle_favorito(fii_id=fii_id, user_id=current_user.id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
    return {"favorito": fii.favorito}

@router.get("/myfiis/{fii_id}/analise")
async def get_analise(
    fii_id: int,
    periodo: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$"),
    incluir_historico: bool = Query(False, description="Incluir dados históricos na resposta"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém análise completa de um FII específico.
    
    Parâmetros:
    - periodo: Período para análise (1m, 3m, 6m, 1y, 2y, 5y)
    - incluir_historico: Se deve incluir dados históricos na resposta
    """
    service = FIIService(db)
    
    # Busca FII
    fii = await service.get_fii(fii_id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
        
    # Busca dados históricos
    historical_data = await service.get_historical_data(
        fii_id=fii_id,
        period=periodo
    )
    
    # Prepara dados do FII
    fii_data = {
        "codigo": fii.codigo,
        "nome": fii.nome,
        "segmento": fii.segmento,
        "preco_atual": fii.preco_atual,
        "dividend_yield": fii.dividend_yield,
        "patrimonio_liquido": fii.patrimonio_liquido,
        "valor_patrimonial": fii.valor_patrimonial,
        "vacancia_media": fii.vacancia_media
    }
    
    # Obtém análise completa
    analise = fii_analyzer.analyze_fii(fii_data, historical_data)
    
    # Adiciona dados históricos se solicitado
    if incluir_historico:
        analise['dados_historicos'] = historical_data
        
    return analise

@router.get("/myfiis/{fii_id}/analise-tecnica")
async def get_analise_tecnica(
    fii_id: int,
    periodo: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém apenas análise técnica de um FII.
    """
    service = FIIService(db)
    
    # Busca FII
    fii = await service.get_fii(fii_id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
        
    # Busca dados históricos
    historical_data = await service.get_historical_data(
        fii_id=fii_id,
        period=periodo
    )
    
    if not historical_data:
        raise HTTPException(
            status_code=400,
            detail="Dados históricos insuficientes para análise técnica"
        )
        
    # Converte para DataFrame
    df = pd.DataFrame(historical_data)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    
    # Obtém análise técnica
    technical = fii_analyzer._analyze_technical_indicators(df)
    
    return technical

@router.get("/myfiis/{fii_id}/previsao")
async def get_previsao(
    fii_id: int,
    periodo_historico: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém previsão de preços para um FII.
    """
    service = FIIService(db)
    
    # Busca FII
    fii = await service.get_fii(fii_id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
        
    # Busca dados históricos
    historical_data = await service.get_historical_data(
        fii_id=fii_id,
        period=periodo_historico
    )
    
    if not historical_data:
        raise HTTPException(
            status_code=400,
            detail="Dados históricos insuficientes para previsão"
        )
        
    # Converte para DataFrame
    df = pd.DataFrame(historical_data)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    
    # Obtém previsão
    prediction = fii_analyzer._predict_prices(df)
    
    # Adiciona datas para as previsões
    last_date = df['data'].iloc[-1]
    prediction['datas_previsao'] = [
        (last_date + timedelta(days=i+1)).strftime("%Y-%m-%d")
        for i in range(30)
    ]
    
    return prediction

@router.get("/myfiis/{fii_id}/tendencia")
async def get_tendencia(
    fii_id: int,
    periodo: str = Query("1y", regex="^(1m|3m|6m|1y|2y|5y)$"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Obtém análise de tendência de um FII.
    """
    service = FIIService(db)
    
    # Busca FII
    fii = await service.get_fii(fii_id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
        
    # Busca dados históricos
    historical_data = await service.get_historical_data(
        fii_id=fii_id,
        period=periodo
    )
    
    if not historical_data:
        raise HTTPException(
            status_code=400,
            detail="Dados históricos insuficientes para análise de tendência"
        )
        
    # Converte para DataFrame
    df = pd.DataFrame(historical_data)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    
    # Obtém análise de tendência
    trend = fii_analyzer._analyze_trend(df)
    
    return trend

@router.get("/myfiis/{fii_id}/similares")
async def get_similares(
    fii_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = 5
):
    """Encontra FIIs similares baseado em análise de IA."""
    service = FIIService(db)
    
    # Obter FII alvo
    fii = await service.get_fii(fii_id=fii_id, user_id=current_user.id)
    if not fii:
        raise HTTPException(status_code=404, detail="FII não encontrado")
        
    # Obter todos os FIIs para comparação
    todos_fiis = await service.list_fiis(user_id=current_user.id)
    
    # Atualizar dados no analisador
    fiis_data = [{
        "codigo": f.codigo,
        "nome": f.nome,
        "segmento": f.segmento,
        "preco_atual": f.preco_atual,
        "dividend_yield": f.dividend_yield,
        "patrimonio_liquido": f.patrimonio_liquido,
        "valor_patrimonial": f.valor_patrimonial,
        "vacancia_media": f.vacancia_media
    } for f in todos_fiis]
    
    fii_analyzer.update_fii_data(fiis_data)
    
    # Encontrar similares
    similares = fii_analyzer.find_similar_fiis(fii.codigo, n=limit)
    
    return similares

@router.get("/myfiis/dashboard/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtém resumo do dashboard de FIIs."""
    service = FIIService(db)
    
    # Obter todos os FIIs do usuário
    fiis = await service.list_fiis(user_id=current_user.id)
    
    # Calcular métricas
    total_investido = sum(fii.preco_atual * fii.quantidade for fii in fiis)
    dy_medio = sum(fii.dividend_yield for fii in fiis) / len(fiis) if fiis else 0
    proventos_total = sum(fii.ultimo_provento * fii.quantidade for fii in fiis)
    
    # Distribuição por segmento
    segmentos = {}
    for fii in fiis:
        valor = fii.preco_atual * fii.quantidade
        if fii.segmento in segmentos:
            segmentos[fii.segmento] += valor
        else:
            segmentos[fii.segmento] = valor
            
    # Converter para percentuais
    for segmento in segmentos:
        segmentos[segmento] = (segmentos[segmento] / total_investido) * 100
        
    return {
        "total_investido": total_investido,
        "dy_medio": dy_medio,
        "proventos_total": proventos_total,
        "distribuicao_segmentos": segmentos,
        "quantidade_fiis": len(fiis)
    }

@router.get("/myfiis/dashboard/evolucao")
async def get_evolucao_carteira(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    periodo: str = "1M"
):
    """Obtém dados de evolução da carteira de FIIs."""
    service = FIIService(db)
    return await service.get_portfolio_evolution(
        user_id=current_user.id,
        periodo=periodo
    ) 