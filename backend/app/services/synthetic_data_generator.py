"""
Gerador de Dados Sintéticos Realistas
Usa AI e análise estatística para gerar dados que parecem reais
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import logging
from faker import Faker
from decimal import Decimal

from app.models.financeiro import TipoLancamento

logger = logging.getLogger(__name__)

class SyntheticDataGenerator:
    """Gerador de dados sintéticos avançado"""
    
    def __init__(self):
        self.fake = Faker('pt_BR')
        random.seed(42)  # Para reprodutibilidade
        
        # Padrões brasileiros realistas
        self.categorias_despesa = [
            "Alimentação", "Transporte", "Moradia", "Saúde", "Educação",
            "Lazer", "Vestuário", "Utilidades", "Seguros", "Impostos",
            "Farmácia", "Combustível", "Internet", "Celular", "Academia"
        ]
        
        self.categorias_receita = [
            "Salário", "Freelance", "Investimentos", "Vendas", "Aluguel",
            "Pensão", "Aposentadoria", "Bonificação", "13º Salário"
        ]
        
        self.bancos_brasileiros = [
            "Banco do Brasil", "Bradesco", "Itaú Unibanco", "Santander",
            "Caixa Econômica Federal", "Nubank", "Inter", "BTG Pactual",
            "Banco Original", "C6 Bank"
        ]
    
    async def generate_realistic_data(
        self, 
        existing_data: Dict[str, Any], 
        config: Dict[str, Any],
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Gera dados sintéticos baseados nos dados existentes"""
        
        count = config.get('count', 100)
        data_type = config.get('type', 'financeiro')
        use_ai_patterns = config.get('use_ai_patterns', True)
        
        logger.info(f"Gerando {count} registros sintéticos do tipo {data_type}")
        
        if data_type == 'financeiro':
            return await self._generate_financial_data(existing_data, count, use_ai_patterns, user_id)
        elif data_type == 'siog':
            return await self._generate_siog_data(existing_data, count, user_id)
        else:
            return await self._generate_generic_data(count, user_id)
    
    async def _generate_financial_data(
        self, 
        existing_data: Dict[str, Any], 
        count: int, 
        use_ai_patterns: bool,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Gera dados financeiros sintéticos realistas"""
        
        synthetic_data = []
        
        # Analisar padrões dos dados existentes se disponível
        patterns = self._analyze_existing_patterns(existing_data) if use_ai_patterns else {}
        
        for i in range(count):
            # Definir tipo baseado em padrões ou distribuição padrão
            tipo_ratio = patterns.get('tipo_ratio', {'despesa': 0.75, 'receita': 0.25})
            is_despesa = random.random() < tipo_ratio['despesa']
            tipo = TipoLancamento.DESPESA if is_despesa else TipoLancamento.RECEITA
            
            # Gerar valor realista
            valor = self._generate_realistic_value(tipo, patterns)
            
            # Selecionar categoria
            categoria = self._select_realistic_category(tipo, patterns)
            
            # Gerar data realista (distribuição temporal)
            data_lancamento = self._generate_realistic_date(patterns)
            
            # Gerar descrição contextual
            descricao = self._generate_realistic_description(categoria, valor, tipo)
            
            # Selecionar conta/banco
            conta_info = self._generate_realistic_account(patterns)
            
            record = {
                'valor': valor,
                'tipo': tipo.value,
                'descricao': descricao,
                'categoria': categoria,
                'data_lancamento': data_lancamento.isoformat(),
                'conta': conta_info['conta'],
                'banco': conta_info['banco'],
                'user_id': user_id,
                'synthetic': True,
                'generated_at': datetime.now().isoformat()
            }
            
            synthetic_data.append(record)
        
        logger.info(f"Gerados {len(synthetic_data)} registros financeiros sintéticos")
        return synthetic_data
    
    async def _generate_siog_data(
        self, 
        existing_data: Dict[str, Any], 
        count: int,
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Gera dados no formato SIOG"""
        
        synthetic_data = []
        
        # Naturezas de despesa SIOG típicas
        naturezas_siog = [
            "DESPESAS FIXAS", "DESPESAS VARIÁVEIS", "GASTOS COM PESSOAL",
            "MANUTENÇÃO CASA", "INVESTIMENTOS", "EQUIPAMENTOS", "SERVIÇOS"
        ]
        
        sub_naturezas = {
            "DESPESAS FIXAS": ["AGUA", "ENERGIA", "CONDOMÍNIO", "INTERNET", "TELEFONE"],
            "GASTOS COM PESSOAL": ["SALÁRIOS", "FGTS", "BENEFÍCIOS", "TERCEIRIZADOS"],
            "MANUTENÇÃO CASA": ["REFORMA", "JARDIM", "LIMPEZA", "SEGURANÇA"],
            "DESPESAS VARIÁVEIS": ["ALIMENTAÇÃO", "COMBUSTÍVEL", "MEDICAMENTOS"]
        }
        
        filiais = ["MATRIZ", "SALÁRIOS", "ADMINISTRATIVO", "OPERACIONAL"]
        
        for i in range(count):
            natureza = random.choice(naturezas_siog)
            sub_natureza = random.choice(sub_naturezas.get(natureza, ["GERAL"]))
            
            # Valor baseado no tipo de natureza
            if natureza == "GASTOS COM PESSOAL":
                valor = round(random.uniform(1000.0, 8000.0), 2)
            elif natureza == "DESPESAS FIXAS":
                valor = round(random.uniform(200.0, 1500.0), 2)
            else:
                valor = round(random.uniform(50.0, 2000.0), 2)
            
            data_base = datetime.now() - timedelta(days=random.randint(0, 365))
            
            record = {
                'id_lan': str(i + 1),
                'filial': random.choice(filiais),
                'conta': random.choice(self.bancos_brasileiros).upper(),
                'banco': random.choice(self.bancos_brasileiros).upper(),
                'cliente_fornecedor': self.fake.company().upper(),
                'tipo_lancamento': 'Saída',
                'vl_original': str(valor).replace('.', ','),
                'vl_baixado': str(valor).replace('.', ','),
                'complemento': self._generate_siog_description(natureza, sub_natureza),
                'dt_vencimento': data_base.strftime('%Y-%m-%d'),
                'dt_baixa': data_base.strftime('%Y-%m-%d'),
                'dt_emissao': data_base.strftime('%Y-%m-%d'),
                'nm_natureza': natureza,
                'sub_natureza': sub_natureza,
                'status_lan': 'Baixado',
                'user_id': user_id,
                'synthetic': True
            }
            
            synthetic_data.append(record)
        
        return synthetic_data
    
    async def _generate_generic_data(self, count: int, user_id: int) -> List[Dict[str, Any]]:
        """Gera dados genéricos"""
        return [
            {
                'id': i + 1,
                'nome': self.fake.name(),
                'email': self.fake.email(),
                'telefone': self.fake.phone_number(),
                'endereco': self.fake.address(),
                'data': self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                'valor': round(random.uniform(10.0, 1000.0), 2),
                'user_id': user_id,
                'synthetic': True
            }
            for i in range(count)
        ]
    
    def _analyze_existing_patterns(self, existing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa padrões dos dados existentes para gerar dados similares"""
        patterns = {}
        
        if not existing_data or not existing_data.get('lancamentos'):
            return self._get_default_patterns()
        
        lancamentos = existing_data['lancamentos']
        df = pd.DataFrame(lancamentos)
        
        if len(df) > 0:
            # Análise de tipos
            if 'tipo' in df.columns:
                tipo_counts = df['tipo'].value_counts()
                total = len(df)
                patterns['tipo_ratio'] = {
                    'despesa': tipo_counts.get('DESPESA', 0) / total,
                    'receita': tipo_counts.get('RECEITA', 0) / total
                }
            
            # Análise de valores
            if 'valor' in df.columns:
                numeric_values = pd.to_numeric(df['valor'], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    patterns['valor_stats'] = {
                        'mean': float(numeric_values.mean()),
                        'std': float(numeric_values.std()),
                        'min': float(numeric_values.min()),
                        'max': float(numeric_values.max()),
                        'percentiles': {
                            '25': float(numeric_values.quantile(0.25)),
                            '50': float(numeric_values.quantile(0.50)),
                            '75': float(numeric_values.quantile(0.75))
                        }
                    }
            
            # Análise de categorias
            if 'categoria' in df.columns:
                patterns['categorias_frequentes'] = df['categoria'].value_counts().head(10).to_dict()
        
        return patterns
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Retorna padrões padrão quando não há dados existentes"""
        return {
            'tipo_ratio': {'despesa': 0.75, 'receita': 0.25},
            'valor_stats': {
                'mean': 350.0,
                'std': 200.0,
                'min': 10.0,
                'max': 2000.0,
                'percentiles': {'25': 100.0, '50': 250.0, '75': 500.0}
            }
        }
    
    def _generate_realistic_value(self, tipo: TipoLancamento, patterns: Dict[str, Any]) -> float:
        """Gera valor realista baseado em padrões"""
        valor_stats = patterns.get('valor_stats', self._get_default_patterns()['valor_stats'])
        
        if tipo == TipoLancamento.DESPESA:
            # Despesas: distribuição log-normal (muitas pequenas, poucas grandes)
            if random.random() < 0.8:  # 80% valores pequenos/médios
                valor = max(10.0, np.random.normal(200.0, 150.0))
            else:  # 20% valores altos
                valor = max(500.0, np.random.normal(1200.0, 400.0))
        else:
            # Receitas: valores maiores e mais estáveis
            valor = max(100.0, np.random.normal(2000.0, 800.0))
        
        return round(min(valor, 10000.0), 2)  # Limitar valor máximo
    
    def _select_realistic_category(self, tipo: TipoLancamento, patterns: Dict[str, Any]) -> str:
        """Seleciona categoria realista"""
        categorias_freq = patterns.get('categorias_frequentes', {})
        
        if categorias_freq and random.random() < 0.6:  # 60% usar categorias existentes
            return random.choice(list(categorias_freq.keys()))
        else:
            # Usar categorias padrão
            if tipo == TipoLancamento.DESPESA:
                return random.choice(self.categorias_despesa)
            else:
                return random.choice(self.categorias_receita)
    
    def _generate_realistic_date(self, patterns: Dict[str, Any]) -> datetime:
        """Gera data realista com sazonalidade"""
        # Distribuição temporal: mais transações no final do mês e meio do mês
        dias_atras = random.randint(0, 365)
        base_date = datetime.now() - timedelta(days=dias_atras)
        
        # Ajustar para padrões de pagamento (dias 5, 15, 30)
        if random.random() < 0.3:  # 30% chance de ser dia de pagamento típico
            payment_days = [5, 15, 30]
            day = random.choice(payment_days)
            base_date = base_date.replace(day=min(day, 28))  # Evitar dias inválidos
        
        return base_date
    
    def _generate_realistic_description(self, categoria: str, valor: float, tipo: TipoLancamento) -> str:
        """Gera descrição contextual realista"""
        descriptions = {
            "Alimentação": [
                f"Supermercado {self.fake.company()}", 
                f"Restaurante {self.fake.first_name()}",
                "iFood - Delivery", 
                "Padaria do Bairro", 
                "Feira Livre"
            ],
            "Transporte": [
                "Posto de Combustível", 
                "Uber", 
                "99Taxi", 
                "Passagem Ônibus",
                "Estacionamento Shopping"
            ],
            "Moradia": [
                "Aluguel Residencial", 
                "Taxa Condomínio", 
                "Conta de Luz - CPFL", 
                "Conta de Água - SABESP", 
                "Internet - Vivo Fibra"
            ],
            "Salário": [
                f"Salário {self.fake.company()}", 
                "Pagamento Freelance", 
                "Bonificação Mensal",
                "13º Salário"
            ]
        }
        
        base_descriptions = descriptions.get(categoria, [f"Transação {categoria}"])
        base_desc = random.choice(base_descriptions)
        
        # Contextualizar baseado no valor
        if valor > 1000:
            return f"{base_desc} - Alto Valor"
        elif valor < 50:
            return f"{base_desc} - Pequena Compra"
        else:
            return base_desc
    
    def _generate_realistic_account(self, patterns: Dict[str, Any]) -> Dict[str, str]:
        """Gera informações de conta realistas"""
        banco = random.choice(self.bancos_brasileiros)
        
        # Tipos de conta baseados no banco
        if banco in ["Nubank", "Inter", "C6 Bank"]:
            conta_tipo = "Conta Digital"
        else:
            conta_tipo = random.choice(["Conta Corrente", "Conta Poupança", "Conta Salário"])
        
        return {
            "conta": f"{conta_tipo} - {banco}",
            "banco": banco
        }
    
    def _generate_siog_description(self, natureza: str, sub_natureza: str) -> str:
        """Gera descrição no formato SIOG"""
        base_descriptions = {
            "AGUA": "Conta de água",
            "ENERGIA": "Conta de energia elétrica", 
            "SALÁRIOS": "Pagamento salários",
            "FGTS": "Depósito FGTS",
            "REFORMA": "Serviços de reforma",
            "JARDIM": "Manutenção jardim"
        }
        
        base = base_descriptions.get(sub_natureza, f"{sub_natureza.lower()}")
        mes_ref = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%m/%Y")
        
        return f"{base.upper()} REF {mes_ref}"

# Instância global
synthetic_generator = SyntheticDataGenerator() 