"""
Serviço de Inteligência de Dados - Análise e Geração Sintética
Analisa arquivos automaticamente e mapeia para tabelas do banco
Gera dados sintéticos realistas usando AI baseado nos dados existentes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
import logging
from pathlib import Path
import random
from faker import Faker
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import asyncio
import aiofiles
from decimal import Decimal

from app.models.financeiro import Lancamento, Categoria, Conta, TipoLancamento
from app.models.user import User
from app.services.cache import cache
from app.core.config import settings

fake = Faker('pt_BR')
logger = logging.getLogger(__name__)

class DataIntelligenceService:
    """Serviço principal de inteligência de dados"""
    
    def __init__(self):
        self.mappers = {
            'financeiro': FinancialDataMapper(),
            'siog': SiogDataMapper(),
            'synthetic': SyntheticDataGenerator()
        }
        self.cache_ttl = 3600  # 1 hora
    
    async def analyze_file(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """
        Analisa arquivo e determina automaticamente o tipo e mapeamento
        """
        try:
            # Detectar tipo de arquivo
            file_type = self._detect_file_type(file_path)
            
            # Carregar dados
            if file_type == 'csv':
                df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            elif file_type == 'excel':
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Tipo de arquivo não suportado: {file_type}")
            
            # Análise da estrutura
            structure_analysis = self._analyze_structure(df)
            
            # Detectar tipo de dados (financeiro, etc)
            data_type = self._detect_data_type(df, structure_analysis)
            
            # Mapear campos automaticamente
            field_mapping = self._auto_map_fields(df, data_type)
            
            # Estatísticas dos dados
            statistics = self._generate_statistics(df)
            
            # Sugestões de limpeza
            cleaning_suggestions = self._suggest_cleaning(df)
            
            return {
                "file_info": {
                    "name": Path(file_path).name,
                    "type": file_type,
                    "size": df.shape[0],
                    "columns": df.shape[1]
                },
                "data_type": data_type,
                "structure_analysis": structure_analysis,
                "field_mapping": field_mapping,
                "statistics": statistics,
                "cleaning_suggestions": cleaning_suggestions,
                "preview_data": df.head(10).to_dict('records'),
                "can_import": True,
                "confidence_score": self._calculate_confidence(structure_analysis, field_mapping)
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar arquivo: {e}")
            return {"error": str(e), "can_import": False}
    
    async def import_data(self, file_path: str, user_id: int, mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Importa dados usando o mapeamento configurado
        """
        try:
            # Carregar dados
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path)
            
            # Aplicar limpeza de dados
            df = self._clean_data(df, mapping_config.get('cleaning_rules', {}))
            
            # Mapear para formato do sistema
            mapped_data = await self._map_to_system_format(df, mapping_config, user_id)
            
            # Validar dados
            validation_results = await self._validate_data(mapped_data)
            
            if validation_results['valid']:
                # Importar para o banco
                import_results = await self._import_to_database(mapped_data, user_id)
                
                return {
                    "success": True,
                    "imported_records": import_results['count'],
                    "summary": import_results['summary'],
                    "validation_results": validation_results
                }
            else:
                return {
                    "success": False,
                    "validation_errors": validation_results['errors']
                }
                
        except Exception as e:
            logger.error(f"Erro ao importar dados: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_synthetic_data(self, user_id: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera dados sintéticos baseados nos dados existentes
        """
        try:
            generator = self.mappers['synthetic']
            
            # Analisar dados existentes do usuário
            existing_data = await self._get_user_existing_data(user_id)
            
            # Gerar dados sintéticos
            synthetic_data = await generator.generate_realistic_data(
                existing_data, 
                config
            )
            
            return {
                "success": True,
                "generated_count": len(synthetic_data),
                "data": synthetic_data,
                "statistics": self._generate_statistics(pd.DataFrame(synthetic_data))
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar dados sintéticos: {e}")
            return {"success": False, "error": str(e)}
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detecta tipo do arquivo"""
        extension = Path(file_path).suffix.lower()
        if extension in ['.csv', '.txt']:
            return 'csv'
        elif extension in ['.xlsx', '.xls']:
            return 'excel'
        else:
            raise ValueError(f"Extensão não suportada: {extension}")
    
    def _analyze_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisa estrutura dos dados"""
        return {
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "unique_counts": df.nunique().to_dict(),
            "sample_values": {col: df[col].dropna().head(3).tolist() for col in df.columns}
        }
    
    def _detect_data_type(self, df: pd.DataFrame, structure: Dict[str, Any]) -> str:
        """Detecta tipo de dados baseado na estrutura"""
        columns = [col.lower() for col in df.columns]
        
        # Palavras-chave para diferentes tipos
        siog_keywords = ['id_lan', 'nm_natureza', 'dt_emissao', 'vl_original']
        financial_keywords = ['valor', 'vl_', 'preco', 'custo', 'receita', 'despesa']
        
        if any(keyword in ' '.join(columns) for keyword in siog_keywords):
            return 'siog'
        elif any(keyword in ' '.join(columns) for keyword in financial_keywords):
            return 'financeiro'
        else:
            return 'generico'
    
    def _auto_map_fields(self, df: pd.DataFrame, data_type: str) -> Dict[str, str]:
        """Mapeia campos automaticamente baseado no tipo"""
        if data_type == 'siog':
            return self._map_siog_fields(df)
        else:
            return self._map_financial_fields(df)
    
    def _map_siog_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Mapeia campos SIOG especificamente"""
        return {
            'valor': 'vl_original',
            'descricao': 'complemento', 
            'data_lancamento': 'dt_emissao',
            'tipo': 'tipo_lancamento',
            'categoria': 'nm_natureza',
            'subcategoria': 'sub_natureza',
            'conta': 'conta',
            'banco': 'banco'
        }
    
    def _map_financial_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Mapeia campos financeiros genéricos"""
        mapping = {}
        
        for col in df.columns:
            col_lower = col.lower()
            
            if any(keyword in col_lower for keyword in ['valor', 'vl_', 'preco']):
                mapping['valor'] = col
            elif any(keyword in col_lower for keyword in ['descricao', 'complemento']):
                mapping['descricao'] = col
            elif any(keyword in col_lower for keyword in ['data', 'dt_']):
                mapping['data_lancamento'] = col
            elif any(keyword in col_lower for keyword in ['tipo', 'natureza']):
                mapping['tipo'] = col
        
        return mapping
    
    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera estatísticas dos dados"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats = {
            "total_records": len(df),
            "numeric_columns": len(numeric_cols),
            "text_columns": len(df.columns) - len(numeric_cols),
            "missing_data_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
        
        if len(numeric_cols) > 0:
            stats["numeric_stats"] = df[numeric_cols].describe().to_dict()
        
        return stats
    
    def _suggest_cleaning(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Sugere limpeza de dados"""
        suggestions = []
        
        # Verificar valores nulos
        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            suggestions.append({
                "type": "null_values",
                "message": f"Colunas com valores nulos: {', '.join(null_cols)}",
                "action": "Substituir ou remover linhas com valores nulos"
            })
        
        # Verificar duplicatas
        if df.duplicated().any():
            suggestions.append({
                "type": "duplicates",
                "message": f"Encontradas {df.duplicated().sum()} linhas duplicadas",
                "action": "Remover duplicatas"
            })
        
        # Verificar formatos de data
        for col in df.columns:
            if 'data' in col.lower() or 'dt_' in col.lower():
                suggestions.append({
                    "type": "date_format",
                    "message": f"Verificar formato da coluna de data: {col}",
                    "action": "Converter para formato de data padrão"
                })
        
        return suggestions
    
    def _calculate_confidence(self, structure: Dict[str, Any], mapping: Dict[str, str]) -> float:
        """Calcula score de confiança do mapeamento"""
        mapped_fields = len([v for v in mapping.values() if v])
        total_fields = len(structure['columns'])
        
        if total_fields == 0:
            return 0.0
        
        base_score = mapped_fields / total_fields
        return min(base_score, 1.0)
    
    def _clean_data(self, df: pd.DataFrame, cleaning_rules: Dict[str, Any]) -> pd.DataFrame:
        """Aplica regras de limpeza aos dados"""
        df_clean = df.copy()
        
        # Remover duplicatas
        if cleaning_rules.get('remove_duplicates', True):
            df_clean = df_clean.drop_duplicates()
        
        # Tratar valores nulos
        null_strategy = cleaning_rules.get('null_strategy', 'drop')
        if null_strategy == 'drop':
            df_clean = df_clean.dropna()
        elif null_strategy == 'fill':
            df_clean = df_clean.fillna(cleaning_rules.get('fill_value', 0))
        
        return df_clean
    
    async def _map_to_system_format(self, df: pd.DataFrame, mapping: Dict[str, Any], user_id: int) -> List[Dict[str, Any]]:
        """Mapeia dados para formato do sistema"""
        mapped_data = []
        field_mapping = mapping['field_mapping']
        
        for _, row in df.iterrows():
            record = {'user_id': user_id}
            
            for system_field, source_field in field_mapping.items():
                if source_field and source_field in row.index:
                    value = row[source_field]
                    
                    # Aplicar transformações baseadas no campo
                    if system_field == 'valor':
                        record[system_field] = float(str(value).replace(',', '.'))
                    elif system_field == 'data_lancamento':
                        record[system_field] = pd.to_datetime(value)
                    elif system_field == 'tipo':
                        # Mapear tipo baseado em palavras-chave
                        if 'saída' in str(value).lower() or 'despesa' in str(value).lower():
                            record[system_field] = TipoLancamento.DESPESA
                        else:
                            record[system_field] = TipoLancamento.RECEITA
                    else:
                        record[system_field] = str(value)
            
            mapped_data.append(record)
        
        return mapped_data
    
    async def _validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida dados antes da importação"""
        errors = []
        valid_records = 0
        
        required_fields = ['valor', 'descricao', 'tipo']
        
        for i, record in enumerate(data):
            record_errors = []
            
            # Verificar campos obrigatórios
            for field in required_fields:
                if field not in record or not record[field]:
                    record_errors.append(f"Campo obrigatório '{field}' ausente")
            
            # Validar valor
            if 'valor' in record:
                try:
                    float(record['valor'])
                except (ValueError, TypeError):
                    record_errors.append("Valor deve ser numérico")
            
            if record_errors:
                errors.append(f"Linha {i+1}: {'; '.join(record_errors)}")
            else:
                valid_records += 1
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "valid_records": valid_records,
            "total_records": len(data)
        }
    
    async def _import_to_database(self, data: List[Dict[str, Any]], user_id: int) -> Dict[str, Any]:
        """Importa dados validados para o banco"""
        # Esta parte seria implementada com a sessão do banco
        # Por ora, retorna mock results
        
        return {
            "count": len(data),
            "summary": {
                "receitas": len([d for d in data if d.get('tipo') == TipoLancamento.RECEITA]),
                "despesas": len([d for d in data if d.get('tipo') == TipoLancamento.DESPESA]),
                "total_valor": sum(float(d.get('valor', 0)) for d in data)
            }
        }
    
    async def _get_user_existing_data(self, user_id: int) -> Dict[str, Any]:
        """Obtém dados existentes do usuário para baseline"""
        # Mock data - seria implementado com query real
        return {
            "lancamentos": [],
            "categorias": [],
            "contas": []
        }


class FinancialDataMapper:
    """Mapeador para dados financeiros genéricos"""
    
    def auto_map_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Mapeia campos automaticamente"""
        columns = [col.lower() for col in df.columns]
        mapping = {}
        
        # Mapeamento por palavras-chave
        for col in df.columns:
            col_lower = col.lower()
            
            if any(keyword in col_lower for keyword in ['valor', 'vl_', 'preco', 'custo']):
                mapping['valor'] = col
            elif any(keyword in col_lower for keyword in ['descricao', 'complemento', 'historico']):
                mapping['descricao'] = col
            elif any(keyword in col_lower for keyword in ['data', 'dt_']):
                mapping['data_lancamento'] = col
            elif any(keyword in col_lower for keyword in ['tipo', 'natureza']):
                mapping['tipo'] = col
            elif any(keyword in col_lower for keyword in ['categoria', 'classe']):
                mapping['categoria'] = col
            elif any(keyword in col_lower for keyword in ['conta', 'banco']):
                mapping['conta'] = col
        
        return mapping


class SiogDataMapper(FinancialDataMapper):
    """Mapeador específico para dados SIOG"""
    
    def auto_map_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Mapeia campos SIOG especificamente"""
        return {
            'valor': 'vl_original',
            'descricao': 'complemento', 
            'data_lancamento': 'dt_emissao',
            'tipo': 'tipo_lancamento',
            'categoria': 'nm_natureza',
            'subcategoria': 'sub_natureza',
            'conta': 'conta',
            'banco': 'banco',
            'fornecedor': 'cliente_fornecedor'
        }


class SyntheticDataGenerator:
    """Gerador de dados sintéticos realistas"""
    
    def __init__(self):
        self.fake = Faker('pt_BR')
        random.seed(42)  # Para reprodutibilidade
    
    async def generate_realistic_data(self, existing_data: Dict[str, Any], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera dados sintéticos realistas baseados nos existentes
        """
        count = config.get('count', 100)
        data_type = config.get('type', 'financeiro')
        
        if data_type == 'financeiro':
            return await self._generate_financial_data(existing_data, count)
        else:
            return await self._generate_generic_data(existing_data, count)
    
    async def _generate_financial_data(self, existing_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Gera dados financeiros sintéticos"""
        synthetic_data = []
        
        # Categorias realistas
        categorias_despesa = [
            "Alimentação", "Transporte", "Moradia", "Saúde", "Educação",
            "Lazer", "Vestuário", "Utilidades", "Seguros", "Impostos"
        ]
        
        categorias_receita = [
            "Salário", "Freelance", "Investimentos", "Vendas", "Outros"
        ]
        
        # Contas bancárias realistas
        bancos = ["Banco do Brasil", "Bradesco", "Itaú", "Santander", "Caixa", "Nubank"]
        
        for i in range(count):
            # Definir tipo (70% despesas, 30% receitas - mais realista)
            is_despesa = random.random() < 0.7
            tipo = TipoLancamento.DESPESA if is_despesa else TipoLancamento.RECEITA
            
            # Gerar valor baseado no tipo
            if is_despesa:
                # Despesas: mais frequentes valores baixos, alguns altos
                if random.random() < 0.8:
                    valor = round(random.uniform(15.0, 500.0), 2)
                else:
                    valor = round(random.uniform(500.0, 2000.0), 2)
                categoria = random.choice(categorias_despesa)
            else:
                # Receitas: valores maiores e mais estáveis
                valor = round(random.uniform(800.0, 5000.0), 2)
                categoria = random.choice(categorias_receita)
            
            # Data realista (últimos 12 meses)
            dias_atras = random.randint(0, 365)
            data_lancamento = datetime.now() - timedelta(days=dias_atras)
            
            # Descrição contextual
            descricao = self._generate_realistic_description(categoria, valor)
            
            record = {
                'valor': valor,
                'tipo': tipo,
                'descricao': descricao,
                'categoria': categoria,
                'data_lancamento': data_lancamento,
                'conta': f"Conta {random.choice(bancos)}",
                'synthetic': True  # Marcar como sintético
            }
            
            synthetic_data.append(record)
        
        return synthetic_data
    
    def _generate_realistic_description(self, categoria: str, valor: float) -> str:
        """Gera descrições realistas baseadas na categoria"""
        descriptions = {
            "Alimentação": [
                f"Supermercado - {self.fake.company()}", 
                f"Restaurante {self.fake.first_name()}",
                "Delivery - iFood", 
                "Padaria", 
                "Feira livre"
            ],
            "Transporte": [
                "Combustível", 
                "Uber/99", 
                "Passagem ônibus", 
                "Estacionamento",
                "Manutenção veículo"
            ],
            "Moradia": [
                "Aluguel", 
                "Condomínio", 
                "Energia elétrica", 
                "Água", 
                "Internet"
            ],
            "Salário": [
                f"Salário {self.fake.company()}", 
                "Pagamento freelance", 
                "Bonificação"
            ]
        }
        
        base_desc = random.choice(descriptions.get(categoria, [f"Transação {categoria}"]))
        
        # Adicionar contexto baseado no valor
        if valor > 1000:
            return f"{base_desc} - Valor alto"
        elif valor < 50:
            return f"{base_desc} - Pequena compra"
        else:
            return base_desc
    
    async def _generate_generic_data(self, existing_data: Dict[str, Any], count: int) -> List[Dict[str, Any]]:
        """Gera dados genéricos"""
        return [
            {
                'id': i + 1,
                'nome': self.fake.name(),
                'email': self.fake.email(),
                'data': self.fake.date_time_between(start_date='-1y', end_date='now'),
                'valor': round(random.uniform(10.0, 1000.0), 2),
                'synthetic': True
            }
            for i in range(count)
        ]


# Instância global do serviço
data_intelligence_service = DataIntelligenceService() 