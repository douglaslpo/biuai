import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from app.models.financeiro import Lancamento, Categoria, MetaFinanceira
from app.models.user import User
import statistics
import numpy as np
from dataclasses import dataclass
from enum import Enum
from app.models.fii import FII

logger = logging.getLogger(__name__)

class InsightType(Enum):
    PATTERN_DETECTION = "pattern_detection"
    SPENDING_ANOMALY = "spending_anomaly"
    GROWTH_OPPORTUNITY = "growth_opportunity"
    RISK_WARNING = "risk_warning"
    GOAL_ACHIEVEMENT = "goal_achievement"
    BUDGET_OPTIMIZATION = "budget_optimization"
    TREND_ANALYSIS = "trend_analysis"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AIInsight:
    id: str
    title: str
    description: str
    insight_type: InsightType
    confidence_score: float  # 0-100
    impact_score: float     # 0-100
    actionable: bool
    action_suggestions: List[str]
    data_supporting: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None

@dataclass
class SmartAlert:
    id: str
    title: str
    message: str
    severity: AlertSeverity
    category: str
    triggered_by: Dict[str, Any]
    threshold_exceeded: Optional[float] = None
    recommendation: str = ""
    dismissible: bool = True
    persistent: bool = False
    created_at: Optional[datetime] = None

class AIInsightsService:
    def __init__(self):
        self.insight_processors = [
            self._analyze_spending_patterns,
            self._detect_anomalies,
            self._identify_growth_opportunities,
            self._assess_financial_health,
            self._analyze_goal_progress,
            self._optimize_budget_allocation,
            self._predict_trends
        ]
        
        self.alert_processors = [
            self._check_budget_limits,
            self._detect_unusual_spending,
            self._monitor_goal_deadlines,
            self._assess_cash_flow_risks,
            self._identify_recurring_payment_issues
        ]

    async def generate_insights(self, user_id: int, db: AsyncSession) -> List[AIInsight]:
        """Gera insights inteligentes baseados nos dados financeiros do usuário"""
        try:
            # Carregar dados do usuário
            financial_data = await self._load_user_financial_data(user_id, db)
            
            if not financial_data["lancamentos"]:
                return self._generate_empty_state_insights()
            
            insights = []
            
            # Executar análises em paralelo para performance
            analysis_tasks = [
                processor(financial_data, db) for processor in self.insight_processors
            ]
            
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            for result in analysis_results:
                if isinstance(result, Exception):
                    logger.error(f"Erro na análise: {result}")
                    continue
                if isinstance(result, list):
                    insights.extend(result)
                elif result:
                    insights.append(result)
            
            # Ordenar por relevância (confidence + impact)
            insights.sort(key=lambda x: (x.confidence_score + x.impact_score) / 2, reverse=True)
            
            return insights[:10]  # Top 10 insights mais relevantes
            
        except Exception as e:
            logger.error(f"Erro ao gerar insights: {e}")
            return self._generate_fallback_insights()

    async def generate_smart_alerts(self, user_id: int, db: AsyncSession) -> List[SmartAlert]:
        """Gera alertas inteligentes baseados em análise de padrões e riscos"""
        try:
            financial_data = await self._load_user_financial_data(user_id, db)
            
            if not financial_data["lancamentos"]:
                return []
            
            alerts = []
            
            # Executar verificações de alerta
            alert_tasks = [
                processor(financial_data, db) for processor in self.alert_processors
            ]
            
            alert_results = await asyncio.gather(*alert_tasks, return_exceptions=True)
            
            for result in alert_results:
                if isinstance(result, Exception):
                    logger.error(f"Erro na verificação de alerta: {result}")
                    continue
                if isinstance(result, list):
                    alerts.extend(result)
                elif result:
                    alerts.append(result)
            
            # Ordenar por severidade
            severity_order = {AlertSeverity.CRITICAL: 4, AlertSeverity.HIGH: 3, 
                            AlertSeverity.MEDIUM: 2, AlertSeverity.LOW: 1}
            alerts.sort(key=lambda x: severity_order[x.severity], reverse=True)
            
            return alerts[:5]  # Top 5 alertas mais críticos
            
        except Exception as e:
            logger.error(f"Erro ao gerar alertas: {e}")
            return []

    async def _load_user_financial_data(self, user_id: int, db: AsyncSession) -> Dict[str, Any]:
        """Carrega todos os dados financeiros necessários para análise"""
        # Período de análise: últimos 12 meses
        data_limite = datetime.now() - timedelta(days=365)
        
        # Carregar lançamentos
        query_lancamentos = select(Lancamento).where(
            and_(
                Lancamento.user_id == user_id,
                Lancamento.data_lancamento >= data_limite
            )
        ).order_by(Lancamento.data_lancamento.desc())
        
        result = await db.execute(query_lancamentos)
        lancamentos = result.scalars().all()
        
        # Carregar categorias
        query_categorias = select(Categoria).where(Categoria.user_id == user_id)
        result = await db.execute(query_categorias)
        categorias = result.scalars().all()
        
        # Carregar metas
        query_metas = select(MetaFinanceira).where(MetaFinanceira.user_id == user_id)
        result = await db.execute(query_metas)
        metas = result.scalars().all()
        
        return {
            "lancamentos": lancamentos,
            "categorias": categorias,
            "metas": metas,
            "periodo_analise": 365
        }

    async def _analyze_spending_patterns(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Analisa padrões de gastos e identifica tendências"""
        insights = []
        lancamentos = data["lancamentos"]
        
        if len(lancamentos) < 10:
            return insights
        
        try:
            # Analisar gastos por dia da semana
            gastos_por_dia = {}
            for l in lancamentos:
                if l.tipo == "DESPESA":
                    dia_semana = l.data_lancamento.weekday()
                    if dia_semana not in gastos_por_dia:
                        gastos_por_dia[dia_semana] = []
                    gastos_por_dia[dia_semana].append(abs(l.valor))
            
            if gastos_por_dia:
                medias_por_dia = {dia: statistics.mean(valores) for dia, valores in gastos_por_dia.items()}
                dia_maior_gasto = max(medias_por_dia.items(), key=lambda x: x[1])[0]
                valor_maior_gasto = medias_por_dia[dia_maior_gasto]
                
                dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
                
                insights.append(AIInsight(
                    id=f"pattern_weekly_{datetime.now().timestamp()}",
                    title=f"Padrão de Gastos: {dias_semana[dia_maior_gasto]}",
                    description=f"Você gasta em média R$ {valor_maior_gasto:.2f} nas {dias_semana[dia_maior_gasto]}s, seu dia de maior gasto semanal.",
                    insight_type=InsightType.PATTERN_DETECTION,
                    confidence_score=85.0,
                    impact_score=70.0,
                    actionable=True,
                    action_suggestions=[
                        f"Planeje melhor os gastos de {dias_semana[dia_maior_gasto]}",
                        "Considere definir um limite específico para este dia",
                        "Analise se os gastos são realmente necessários"
                    ],
                    data_supporting={
                        "dia_semana": dia_maior_gasto,
                        "valor_medio": valor_maior_gasto,
                        "total_registros": len(gastos_por_dia[dia_maior_gasto])
                    },
                    created_at=datetime.now()
                ))
            
            # Analisar crescimento/redução de gastos
            gastos_mensais = {}
            for l in lancamentos:
                if l.tipo == "DESPESA":
                    mes_key = l.data_lancamento.strftime("%Y-%m")
                    if mes_key not in gastos_mensais:
                        gastos_mensais[mes_key] = 0
                    gastos_mensais[mes_key] += abs(l.valor)
            
            if len(gastos_mensais) >= 3:
                valores_ordenados = [gastos_mensais[mes] for mes in sorted(gastos_mensais.keys())]
                
                # Calcular tendência (últimos 3 meses vs 3 anteriores)
                if len(valores_ordenados) >= 6:
                    ultimos_3 = statistics.mean(valores_ordenados[-3:])
                    anteriores_3 = statistics.mean(valores_ordenados[-6:-3])
                    variacao = ((ultimos_3 - anteriores_3) / anteriores_3) * 100
                    
                    if abs(variacao) > 15:  # Mudança significativa
                        tendencia = "aumentaram" if variacao > 0 else "diminuíram"
                        insights.append(AIInsight(
                            id=f"trend_monthly_{datetime.now().timestamp()}",
                            title=f"Tendência: Gastos {tendencia.capitalize()}",
                            description=f"Seus gastos {tendencia} {abs(variacao):.1f}% nos últimos 3 meses comparado ao período anterior.",
                            insight_type=InsightType.TREND_ANALYSIS,
                            confidence_score=90.0,
                            impact_score=85.0 if variacao > 0 else 75.0,
                            actionable=True,
                            action_suggestions=[
                                "Analise as categorias que mais contribuíram para esta mudança",
                                "Revise seu orçamento se necessário",
                                "Continue monitorando esta tendência"
                            ] if variacao > 0 else [
                                "Parabéns pela redução de gastos!",
                                "Identifique o que funcionou para manter esta tendência",
                                "Considere investir a economia"
                            ],
                            data_supporting={
                                "variacao_percentual": variacao,
                                "valor_atual": ultimos_3,
                                "valor_anterior": anteriores_3
                            },
                            created_at=datetime.now()
                        ))
            
        except Exception as e:
            logger.error(f"Erro na análise de padrões: {e}")
        
        return insights

    async def _detect_anomalies(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Detecta anomalias e gastos incomuns"""
        insights = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar despesas incomuns (outliers)
            despesas = [abs(l.valor) for l in lancamentos if l.tipo == "DESPESA"]
            
            if len(despesas) >= 20:
                q1 = np.percentile(despesas, 25)
                q3 = np.percentile(despesas, 75)
                iqr = q3 - q1
                limite_superior = q3 + 1.5 * iqr
                
                outliers = [v for v in despesas if v > limite_superior]
                
                if outliers:
                    media_outliers = statistics.mean(outliers)
                    media_normal = statistics.mean([v for v in despesas if v <= limite_superior])
                    
                    insights.append(AIInsight(
                        id=f"anomaly_spending_{datetime.now().timestamp()}",
                        title="Gastos Incomuns Detectados",
                        description=f"Identificamos {len(outliers)} transações com valores muito acima do normal (média de R$ {media_outliers:.2f} vs R$ {media_normal:.2f}).",
                        insight_type=InsightType.SPENDING_ANOMALY,
                        confidence_score=80.0,
                        impact_score=75.0,
                        actionable=True,
                        action_suggestions=[
                            "Revise essas transações para verificar se são justificadas",
                            "Considere criar alertas para gastos acima de um limite",
                            "Analise se esses gastos se repetem mensalmente"
                        ],
                        data_supporting={
                            "numero_outliers": len(outliers),
                            "valor_medio_outliers": media_outliers,
                            "valor_medio_normal": media_normal,
                            "limite_considerado": limite_superior
                        },
                        created_at=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {e}")
        
        return insights

    async def _identify_growth_opportunities(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Identifica oportunidades de crescimento financeiro"""
        insights = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar potencial de economia
            receitas = [l.valor for l in lancamentos if l.tipo == "RECEITA"]
            despesas = [abs(l.valor) for l in lancamentos if l.tipo == "DESPESA"]
            
            if receitas and despesas:
                total_receitas = sum(receitas)
                total_despesas = sum(despesas)
                taxa_poupanca = (total_receitas - total_despesas) / total_receitas * 100
                
                if taxa_poupanca < 20:  # Taxa baixa de poupança
                    economia_sugerida = total_receitas * 0.05  # 5% das receitas
                    
                    insights.append(AIInsight(
                        id=f"opportunity_savings_{datetime.now().timestamp()}",
                        title="Oportunidade de Aumentar Poupança",
                        description=f"Sua taxa de poupança atual é de {taxa_poupanca:.1f}%. Economizando apenas R$ {economia_sugerida:.2f} por mês, você poderia melhorar significativamente sua situação financeira.",
                        insight_type=InsightType.GROWTH_OPPORTUNITY,
                        confidence_score=85.0,
                        impact_score=90.0,
                        actionable=True,
                        action_suggestions=[
                            "Defina uma meta de poupança de pelo menos 20% da renda",
                            "Identifique gastos que podem ser reduzidos",
                            "Considere automatizar a poupança"
                        ],
                        data_supporting={
                            "taxa_poupanca_atual": taxa_poupanca,
                            "economia_sugerida": economia_sugerida,
                            "receitas_totais": total_receitas,
                            "despesas_totais": total_despesas
                        },
                        created_at=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Erro na identificação de oportunidades: {e}")
        
        return insights

    async def _assess_financial_health(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Avalia a saúde financeira geral"""
        insights = []
        lancamentos = data["lancamentos"]
        
        try:
            if not lancamentos:
                return insights
                
            # Calcular índice de saúde financeira
            receitas_mensais = {}
            despesas_mensais = {}
            
            for l in lancamentos:
                mes_key = l.data_lancamento.strftime("%Y-%m")
                if l.tipo == "RECEITA":
                    if mes_key not in receitas_mensais:
                        receitas_mensais[mes_key] = 0
                    receitas_mensais[mes_key] += l.valor
                else:
                    if mes_key not in despesas_mensais:
                        despesas_mensais[mes_key] = 0
                    despesas_mensais[mes_key] += abs(l.valor)
            
            # Calcular consistência financeira
            meses_com_dados = set(receitas_mensais.keys()) & set(despesas_mensais.keys())
            if len(meses_com_dados) >= 3:
                saldos_mensais = []
                for mes in meses_com_dados:
                    receita = receitas_mensais.get(mes, 0)
                    despesa = despesas_mensais.get(mes, 0)
                    saldos_mensais.append(receita - despesa)
                
                meses_positivos = len([s for s in saldos_mensais if s > 0])
                consistencia = (meses_positivos / len(saldos_mensais)) * 100
                
                if consistencia >= 80:
                    nivel_saude = "Excelente"
                    cor = "success"
                elif consistencia >= 60:
                    nivel_saude = "Boa"
                    cor = "info"
                elif consistencia >= 40:
                    nivel_saude = "Regular"
                    cor = "warning"
                else:
                    nivel_saude = "Crítica"
                    cor = "error"
                
                insights.append(AIInsight(
                    id=f"health_assessment_{datetime.now().timestamp()}",
                    title=f"Saúde Financeira: {nivel_saude}",
                    description=f"Sua consistência financeira é de {consistencia:.1f}%. Você teve saldo positivo em {meses_positivos} de {len(saldos_mensais)} meses analisados.",
                    insight_type=InsightType.RISK_WARNING if consistencia < 60 else InsightType.PATTERN_DETECTION,
                    confidence_score=90.0,
                    impact_score=95.0,
                    actionable=consistencia < 80,
                    action_suggestions=[
                        "Mantenha o bom trabalho com sua disciplina financeira!",
                        "Considere aumentar sua reserva de emergência",
                        "Explore opções de investimento"
                    ] if consistencia >= 80 else [
                        "Revise seu orçamento para melhorar a consistência",
                        "Identifique e elimine gastos desnecessários",
                        "Considere aumentar suas fontes de renda"
                    ],
                    data_supporting={
                        "consistencia_percentual": consistencia,
                        "meses_positivos": meses_positivos,
                        "total_meses": len(saldos_mensais),
                        "nivel_saude": nivel_saude
                    },
                    created_at=datetime.now()
                ))
                
        except Exception as e:
            logger.error(f"Erro na avaliação de saúde financeira: {e}")
        
        return insights

    async def _analyze_goal_progress(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Analisa progresso das metas financeiras"""
        insights = []
        metas = data["metas"]
        
        try:
            for meta in metas:
                if meta.status == "ATIVA":
                    progresso = (meta.valor_atual / meta.valor_meta) * 100 if meta.valor_meta > 0 else 0
                    
                    # Calcular dias restantes
                    hoje = datetime.now()
                    dias_restantes = (meta.data_fim.replace(tzinfo=None) - hoje).days if meta.data_fim else 0
                    
                    if dias_restantes > 0:
                        # Calcular progresso necessário por dia
                        valor_restante = meta.valor_meta - meta.valor_atual
                        necessario_por_dia = valor_restante / dias_restantes if dias_restantes > 0 else 0
                        
                        if progresso >= 90:
                            insights.append(AIInsight(
                                id=f"goal_near_completion_{meta.id}",
                                title=f"Meta Quase Concluída: {meta.nome}",
                                description=f"Parabéns! Você está a {100 - progresso:.1f}% de completar sua meta '{meta.nome}'. Faltam apenas R$ {valor_restante:.2f}!",
                                insight_type=InsightType.GOAL_ACHIEVEMENT,
                                confidence_score=95.0,
                                impact_score=85.0,
                                actionable=True,
                                action_suggestions=[
                                    "Continue focado para concluir esta meta",
                                    "Comemore este grande progresso!",
                                    "Prepare-se para definir uma nova meta"
                                ],
                                data_supporting={
                                    "meta_id": meta.id,
                                    "progresso_percentual": progresso,
                                    "valor_restante": valor_restante,
                                    "dias_restantes": dias_restantes
                                },
                                created_at=datetime.now()
                            ))
                        elif progresso < 25 and dias_restantes < 30:
                            insights.append(AIInsight(
                                id=f"goal_at_risk_{meta.id}",
                                title=f"Meta em Risco: {meta.nome}",
                                description=f"Atenção! Sua meta '{meta.nome}' tem apenas {progresso:.1f}% de progresso com {dias_restantes} dias restantes. Você precisaria economizar R$ {necessario_por_dia:.2f} por dia.",
                                insight_type=InsightType.RISK_WARNING,
                                confidence_score=90.0,
                                impact_score=80.0,
                                actionable=True,
                                action_suggestions=[
                                    "Revise o valor da meta se necessário",
                                    "Intensifique os esforços de economia",
                                    "Considere ajustar o prazo da meta"
                                ],
                                data_supporting={
                                    "meta_id": meta.id,
                                    "progresso_percentual": progresso,
                                    "necessario_por_dia": necessario_por_dia,
                                    "dias_restantes": dias_restantes
                                },
                                created_at=datetime.now()
                            ))
                            
        except Exception as e:
            logger.error(f"Erro na análise de metas: {e}")
        
        return insights

    async def _optimize_budget_allocation(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Sugere otimizações na alocação do orçamento"""
        insights = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar gastos por categoria
            gastos_categoria = {}
            for l in lancamentos:
                if l.tipo == "DESPESA" and l.categoria_id:
                    if l.categoria_id not in gastos_categoria:
                        gastos_categoria[l.categoria_id] = 0
                    gastos_categoria[l.categoria_id] += abs(l.valor)
            
            if gastos_categoria:
                total_gastos = sum(gastos_categoria.values())
                
                # Identificar categoria com maior gasto
                categoria_maior_gasto = max(gastos_categoria.items(), key=lambda x: x[1])[0]
                valor_maior_gasto = gastos_categoria[categoria_maior_gasto]
                percentual_maior = (valor_maior_gasto / total_gastos) * 100
                
                if percentual_maior > 40:  # Concentração muito alta
                    insights.append(AIInsight(
                        id=f"budget_concentration_{datetime.now().timestamp()}",
                        title="Alta Concentração de Gastos",
                        description=f"Uma categoria representa {percentual_maior:.1f}% dos seus gastos totais. Considere diversificar ou otimizar esta área.",
                        insight_type=InsightType.BUDGET_OPTIMIZATION,
                        confidence_score=85.0,
                        impact_score=70.0,
                        actionable=True,
                        action_suggestions=[
                            "Analise se estes gastos podem ser reduzidos",
                            "Compare preços e fornecedores nesta categoria",
                            "Defina um limite específico para esta categoria"
                        ],
                        data_supporting={
                            "categoria_id": categoria_maior_gasto,
                            "percentual": percentual_maior,
                            "valor": valor_maior_gasto
                        },
                        created_at=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Erro na otimização de orçamento: {e}")
        
        return insights

    async def _predict_trends(self, data: Dict[str, Any], db: AsyncSession) -> List[AIInsight]:
        """Prediz tendências futuras baseadas nos dados históricos"""
        insights = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar tendência de crescimento de receitas
            receitas_mensais = {}
            for l in lancamentos:
                if l.tipo == "RECEITA":
                    mes_key = l.data_lancamento.strftime("%Y-%m")
                    if mes_key not in receitas_mensais:
                        receitas_mensais[mes_key] = 0
                    receitas_mensais[mes_key] += l.valor
            
            if len(receitas_mensais) >= 6:
                valores = [receitas_mensais[mes] for mes in sorted(receitas_mensais.keys())]
                
                # Calcular tendência simples (últimos 3 vs primeiros 3)
                if len(valores) >= 6:
                    primeiros_3 = statistics.mean(valores[:3])
                    ultimos_3 = statistics.mean(valores[-3:])
                    
                    if ultimos_3 > primeiros_3:
                        crescimento = ((ultimos_3 - primeiros_3) / primeiros_3) * 100
                        
                        # Projeção para próximos 3 meses
                        projecao = ultimos_3 * (1 + (crescimento / 100))
                        
                        insights.append(AIInsight(
                            id=f"trend_revenue_growth_{datetime.now().timestamp()}",
                            title="Tendência Positiva de Receitas",
                            description=f"Suas receitas cresceram {crescimento:.1f}% nos últimos meses. Mantendo este ritmo, você pode ter R$ {projecao:.2f} de receita mensal em breve.",
                            insight_type=InsightType.TREND_ANALYSIS,
                            confidence_score=75.0,
                            impact_score=80.0,
                            actionable=True,
                            action_suggestions=[
                                "Continue focando nas atividades que geram essa receita",
                                "Considere investir parte desta receita extra",
                                "Planeje com base nesta tendência positiva"
                            ],
                            data_supporting={
                                "crescimento_percentual": crescimento,
                                "receita_atual": ultimos_3,
                                "projecao": projecao
                            },
                            created_at=datetime.now()
                        ))
                        
        except Exception as e:
            logger.error(f"Erro na predição de tendências: {e}")
        
        return insights

    # Métodos para alertas
    async def _check_budget_limits(self, data: Dict[str, Any], db: AsyncSession) -> List[SmartAlert]:
        """Verifica limites de orçamento e gera alertas"""
        alerts = []
        lancamentos = data["lancamentos"]
        
        try:
            # Calcular gastos do mês atual
            hoje = datetime.now()
            inicio_mes = datetime(hoje.year, hoje.month, 1)
            
            gastos_mes = [abs(l.valor) for l in lancamentos 
                         if l.tipo == "DESPESA" and l.data_lancamento >= inicio_mes]
            
            if gastos_mes:
                total_gastos_mes = sum(gastos_mes)
                
                # Calcular média de gastos mensais dos últimos 6 meses
                gastos_mensais = {}
                for l in lancamentos:
                    if l.tipo == "DESPESA":
                        mes_key = l.data_lancamento.strftime("%Y-%m")
                        if mes_key not in gastos_mensais:
                            gastos_mensais[mes_key] = 0
                        gastos_mensais[mes_key] += abs(l.valor)
                
                if len(gastos_mensais) >= 3:
                    media_mensal = statistics.mean(list(gastos_mensais.values()))
                    
                    if total_gastos_mes > media_mensal * 1.2:  # 20% acima da média
                        alerts.append(SmartAlert(
                            id=f"budget_exceeded_{datetime.now().timestamp()}",
                            title="Gastos Acima da Média",
                            message=f"Seus gastos este mês (R$ {total_gastos_mes:.2f}) estão 20% acima da sua média mensal.",
                            severity=AlertSeverity.MEDIUM,
                            category="budget",
                            triggered_by={"gastos_mes": total_gastos_mes, "media": media_mensal},
                            threshold_exceeded=20.0,
                            recommendation="Monitore os gastos restantes do mês e evite compras desnecessárias.",
                            created_at=datetime.now()
                        ))
                    elif total_gastos_mes > media_mensal * 1.4:  # 40% acima
                        alerts.append(SmartAlert(
                            id=f"budget_critical_{datetime.now().timestamp()}",
                            title="Gastos Muito Elevados",
                            message=f"ATENÇÃO: Seus gastos este mês estão 40% acima do normal!",
                            severity=AlertSeverity.HIGH,
                            category="budget",
                            triggered_by={"gastos_mes": total_gastos_mes, "media": media_mensal},
                            threshold_exceeded=40.0,
                            recommendation="Revise urgentemente seus gastos e corte despesas não essenciais.",
                            persistent=True,
                            created_at=datetime.now()
                        ))
                        
        except Exception as e:
            logger.error(f"Erro na verificação de orçamento: {e}")
        
        return alerts

    async def _detect_unusual_spending(self, data: Dict[str, Any], db: AsyncSession) -> List[SmartAlert]:
        """Detecta gastos incomuns"""
        alerts = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar gastos dos últimos 7 dias
            hoje = datetime.now()
            semana_passada = hoje - timedelta(days=7)
            
            gastos_recentes = [abs(l.valor) for l in lancamentos 
                             if l.tipo == "DESPESA" and l.data_lancamento >= semana_passada]
            
            if gastos_recentes:
                # Calcular estatísticas dos últimos 3 meses para comparação
                tres_meses = hoje - timedelta(days=90)
                gastos_historicos = [abs(l.valor) for l in lancamentos 
                                   if l.tipo == "DESPESA" and l.data_lancamento >= tres_meses and l.data_lancamento < semana_passada]
                
                if len(gastos_historicos) >= 20:
                    media_historica = statistics.mean(gastos_historicos)
                    desvio_historico = statistics.stdev(gastos_historicos)
                    
                    gastos_incomuns = [g for g in gastos_recentes if g > media_historica + 2 * desvio_historico]
                    
                    if gastos_incomuns:
                        alerts.append(SmartAlert(
                            id=f"unusual_spending_{datetime.now().timestamp()}",
                            title="Gastos Incomuns Detectados",
                            message=f"Identificamos {len(gastos_incomuns)} transações com valores muito acima do seu padrão normal.",
                            severity=AlertSeverity.MEDIUM,
                            category="anomaly",
                            triggered_by={
                                "gastos_incomuns": len(gastos_incomuns),
                                "valor_maximo": max(gastos_incomuns),
                                "media_historica": media_historica
                            },
                            recommendation="Verifique se estas transações estão corretas e se são justificadas.",
                            created_at=datetime.now()
                        ))
                        
        except Exception as e:
            logger.error(f"Erro na detecção de gastos incomuns: {e}")
        
        return alerts

    async def _monitor_goal_deadlines(self, data: Dict[str, Any], db: AsyncSession) -> List[SmartAlert]:
        """Monitora prazos de metas"""
        alerts = []
        metas = data["metas"]
        
        try:
            hoje = datetime.now()
            
            for meta in metas:
                if meta.status == "ATIVA" and meta.data_fim:
                    dias_restantes = (meta.data_fim.replace(tzinfo=None) - hoje).days
                    progresso = (meta.valor_atual / meta.valor_meta) * 100 if meta.valor_meta > 0 else 0
                    
                    if dias_restantes <= 7 and progresso < 90:
                        severity = AlertSeverity.HIGH if progresso < 50 else AlertSeverity.MEDIUM
                        
                        alerts.append(SmartAlert(
                            id=f"goal_deadline_{meta.id}",
                            title=f"Meta com Prazo Próximo: {meta.nome}",
                            message=f"Sua meta '{meta.nome}' vence em {dias_restantes} dias e está {progresso:.1f}% completa.",
                            severity=severity,
                            category="goals",
                            triggered_by={
                                "meta_id": meta.id,
                                "dias_restantes": dias_restantes,
                                "progresso": progresso
                            },
                            recommendation="Intensifique os esforços ou considere ajustar o prazo da meta.",
                            created_at=datetime.now()
                        ))
                        
        except Exception as e:
            logger.error(f"Erro no monitoramento de metas: {e}")
        
        return alerts

    async def _assess_cash_flow_risks(self, data: Dict[str, Any], db: AsyncSession) -> List[SmartAlert]:
        """Avalia riscos de fluxo de caixa"""
        alerts = []
        lancamentos = data["lancamentos"]
        
        try:
            # Analisar padrão de receitas e despesas
            hoje = datetime.now()
            ultimos_30_dias = hoje - timedelta(days=30)
            
            receitas_recentes = [l.valor for l in lancamentos 
                               if l.tipo == "RECEITA" and l.data_lancamento >= ultimos_30_dias]
            despesas_recentes = [abs(l.valor) for l in lancamentos 
                               if l.tipo == "DESPESA" and l.data_lancamento >= ultimos_30_dias]
            
            if receitas_recentes and despesas_recentes:
                total_receitas = sum(receitas_recentes)
                total_despesas = sum(despesas_recentes)
                
                # Verificar se despesas excedem receitas significativamente
                if total_despesas > total_receitas * 1.1:  # 10% a mais em despesas
                    deficit = total_despesas - total_receitas
                    
                    alerts.append(SmartAlert(
                        id=f"cash_flow_risk_{datetime.now().timestamp()}",
                        title="Risco de Fluxo de Caixa",
                        message=f"Suas despesas excederam as receitas em R$ {deficit:.2f} nos últimos 30 dias.",
                        severity=AlertSeverity.HIGH if deficit > total_receitas * 0.2 else AlertSeverity.MEDIUM,
                        category="cash_flow",
                        triggered_by={
                            "deficit": deficit,
                            "total_receitas": total_receitas,
                            "total_despesas": total_despesas
                        },
                        recommendation="Revise seus gastos e considere aumentar suas receitas ou reduzir despesas não essenciais.",
                        persistent=True,
                        created_at=datetime.now()
                    ))
                    
        except Exception as e:
            logger.error(f"Erro na avaliação de fluxo de caixa: {e}")
        
        return alerts

    async def _identify_recurring_payment_issues(self, data: Dict[str, Any], db: AsyncSession) -> List[SmartAlert]:
        """Identifica problemas com pagamentos recorrentes"""
        alerts = []
        lancamentos = data["lancamentos"]
        
        try:
            # Identificar possíveis pagamentos recorrentes (mesmo valor e descrição similar)
            despesas_agrupadas = {}
            
            for l in lancamentos:
                if l.tipo == "DESPESA":
                    # Agrupar por valor similar (variação de até 5%)
                    valor_base = round(abs(l.valor) / 50) * 50  # Arredondar para múltiplos de 50
                    
                    if valor_base not in despesas_agrupadas:
                        despesas_agrupadas[valor_base] = []
                    despesas_agrupadas[valor_base].append(l)
            
            # Verificar se há padrões suspeitos (muitas transações com mesmo valor)
            for valor, transacoes in despesas_agrupadas.items():
                if len(transacoes) >= 3:  # 3 ou mais transações similares
                    # Verificar se estão bem distribuídas no tempo
                    datas = [t.data_lancamento for t in transacoes]
                    datas.sort()
                    
                    # Calcular intervalo médio entre transações
                    intervalos = [(datas[i] - datas[i-1]).days for i in range(1, len(datas))]
                    
                    if intervalos:
                        intervalo_medio = statistics.mean(intervalos)
                        
                        # Se intervalo é próximo de 30 dias (mensal), pode ser recorrente
                        if 25 <= intervalo_medio <= 35:
                            ultima_transacao = max(datas)
                            dias_desde_ultima = (datetime.now() - ultima_transacao).days
                            
                            if dias_desde_ultima > 35:  # Atraso no pagamento recorrente
                                alerts.append(SmartAlert(
                                    id=f"recurring_payment_missing_{valor}",
                                    title="Possível Pagamento Recorrente em Atraso",
                                    message=f"Detectamos um possível pagamento recorrente de ~R$ {valor:.2f} que pode estar em atraso.",
                                    severity=AlertSeverity.LOW,
                                    category="recurring",
                                    triggered_by={
                                        "valor_aproximado": valor,
                                        "dias_atraso": dias_desde_ultima,
                                        "intervalo_medio": intervalo_medio
                                    },
                                    recommendation="Verifique se há algum pagamento mensal que você esqueceu de registrar.",
                                    created_at=datetime.now()
                                ))
                                
        except Exception as e:
            logger.error(f"Erro na identificação de pagamentos recorrentes: {e}")
        
        return alerts

    def _generate_empty_state_insights(self) -> List[AIInsight]:
        """Gera insights para usuários com poucos dados"""
        return [
            AIInsight(
                id="empty_state_welcome",
                title="Bem-vindo ao BIUAI!",
                description="Comece registrando seus lançamentos financeiros para receber insights personalizados e inteligentes.",
                insight_type=InsightType.PATTERN_DETECTION,
                confidence_score=100.0,
                impact_score=90.0,
                actionable=True,
                action_suggestions=[
                    "Registre algumas receitas e despesas",
                    "Configure categorias para organizar seus gastos",
                    "Defina metas financeiras para acompanhar seu progresso"
                ],
                data_supporting={},
                created_at=datetime.now()
            )
        ]

    def _generate_fallback_insights(self) -> List[AIInsight]:
        """Gera insights de fallback em caso de erro"""
        return [
            AIInsight(
                id="fallback_insight",
                title="Mantenha o Controle Financeiro",
                description="Continue registrando suas transações para uma análise mais precisa dos seus padrões financeiros.",
                insight_type=InsightType.PATTERN_DETECTION,
                confidence_score=70.0,
                impact_score=60.0,
                actionable=True,
                action_suggestions=[
                    "Registre todas as transações regularmente",
                    "Categorize seus gastos adequadamente",
                    "Revise periodicamente seu orçamento"
                ],
                data_supporting={},
                created_at=datetime.now()
            )
        ]

async def get_fii_insights(fii: FII) -> List[Dict[str, Any]]:
    """
    Gera insights inteligentes para um FII específico.
    Retorna uma lista de insights com tipo, mensagem e ícone.
    """
    insights = []

    # Análise de Dividend Yield
    if fii.dividend_yield:
        if fii.dividend_yield > 8:
            insights.append({
                "tipo": "success",
                "mensagem": f"Dividend Yield de {fii.dividend_yield:.2f}% está acima da média do mercado",
                "icone": "mdi-trending-up"
            })
        elif fii.dividend_yield < 4:
            insights.append({
                "tipo": "warning",
                "mensagem": f"Dividend Yield de {fii.dividend_yield:.2f}% está abaixo da média do mercado",
                "icone": "mdi-trending-down"
            })

    # Análise de Liquidez
    if fii.liquidez_diaria:
        if fii.liquidez_diaria < 100000:
            insights.append({
                "tipo": "warning",
                "mensagem": "Baixa liquidez diária pode dificultar compra/venda",
                "icone": "mdi-alert"
            })
        elif fii.liquidez_diaria > 1000000:
            insights.append({
                "tipo": "success",
                "mensagem": "Alta liquidez diária facilita negociações",
                "icone": "mdi-check-circle"
            })

    # Análise de Valor Patrimonial
    if fii.valor_patrimonial and fii.preco_atual:
        pvp = fii.preco_atual / fii.valor_patrimonial
        if pvp < 0.9:
            insights.append({
                "tipo": "success",
                "mensagem": f"FII negociando abaixo do valor patrimonial (P/VP = {pvp:.2f})",
                "icone": "mdi-currency-usd"
            })
        elif pvp > 1.3:
            insights.append({
                "tipo": "warning",
                "mensagem": f"FII negociando muito acima do valor patrimonial (P/VP = {pvp:.2f})",
                "icone": "mdi-alert-circle"
            })

    # Análise de Patrimônio Líquido
    if fii.patrimonio_liquido:
        if fii.patrimonio_liquido < 100000000:  # 100 milhões
            insights.append({
                "tipo": "warning",
                "mensagem": "Patrimônio líquido relativamente baixo",
                "icone": "mdi-bank"
            })
        elif fii.patrimonio_liquido > 1000000000:  # 1 bilhão
            insights.append({
                "tipo": "success",
                "mensagem": "FII com grande patrimônio líquido",
                "icone": "mdi-bank-check"
            })

    # Análise de Segmento
    segmentos_risco = {
        "Shoppings": "Exposição ao varejo pode trazer volatilidade",
        "Logística": "Setor resiliente com boas perspectivas",
        "Escritórios": "Atenção à taxa de vacância do mercado",
        "Recebíveis": "Menor risco, mas retornos podem ser menores"
    }

    if fii.segmento in segmentos_risco:
        insights.append({
            "tipo": "info",
            "mensagem": segmentos_risco[fii.segmento],
            "icone": "mdi-information"
        })

    # Se não houver insights, adiciona uma mensagem padrão
    if not insights:
        insights.append({
            "tipo": "info",
            "mensagem": "Não há insights relevantes no momento",
            "icone": "mdi-information"
        })

    return insights 