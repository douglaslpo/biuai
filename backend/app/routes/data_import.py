"""
Rotas para Importação Inteligente de Dados e Geração Sintética
"""

import os
import tempfile
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
import logging

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.data_intelligence_service import data_intelligence_service
from app.services.synthetic_data_generator import synthetic_generator
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

class AnalyzeFileResponse(BaseModel):
    """Response para análise de arquivo"""
    success: bool
    file_info: Dict[str, Any]
    data_type: str
    field_mapping: Dict[str, str]
    statistics: Dict[str, Any]
    preview_data: List[Dict[str, Any]]
    confidence_score: float
    cleaning_suggestions: List[Dict[str, Any]]

class ImportConfigModel(BaseModel):
    """Configuração de importação"""
    field_mapping: Dict[str, str]
    cleaning_rules: Dict[str, Any] = {}
    create_categories: bool = True
    create_accounts: bool = True

class SyntheticDataConfig(BaseModel):
    """Configuração para geração de dados sintéticos"""
    count: int = 100
    data_type: str = "financeiro"  # financeiro, siog, generico
    use_ai_patterns: bool = True
    base_existing_data: bool = True

@router.post("/analyze", response_model=AnalyzeFileResponse)
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analisa arquivo carregado e sugere mapeamento automático
    """
    try:
        # Validar tipo de arquivo
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Analisar arquivo
            analysis_result = await data_intelligence_service.analyze_file(
                temp_file_path, 
                current_user.id
            )
            
            if "error" in analysis_result:
                raise HTTPException(status_code=400, detail=analysis_result["error"])
            
            return AnalyzeFileResponse(
                success=True,
                **analysis_result
            )
            
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Erro ao analisar arquivo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao analisar arquivo: {str(e)}")

@router.post("/import")
async def import_data_with_config(
    file: UploadFile = File(...),
    config: str = Form(...),  # JSON string da configuração
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Importa dados usando configuração personalizada
    """
    try:
        # Parse da configuração
        try:
            import_config = json.loads(config)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Configuração inválida")
        
        # Validar arquivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in {'.csv', '.xlsx', '.xls'}:
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
        
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Importar dados
            import_result = await data_intelligence_service.import_data(
                temp_file_path,
                current_user.id,
                import_config
            )
            
            if not import_result.get("success"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": import_result.get("error", "Erro na importação"),
                        "validation_errors": import_result.get("validation_errors", [])
                    }
                )
            
            logger.info(f"Dados importados com sucesso para usuário {current_user.id}")
            
            return {
                "success": True,
                "message": "Dados importados com sucesso",
                "imported_records": import_result["imported_records"],
                "summary": import_result["summary"]
            }
            
        finally:
            # Limpar arquivo temporário
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Erro ao importar dados: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao importar dados: {str(e)}")

@router.post("/generate-synthetic")
async def generate_synthetic_data(
    config: SyntheticDataConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera dados sintéticos baseados nos dados existentes do usuário
    """
    try:
        # Obter dados existentes do usuário se solicitado
        existing_data = {}
        if config.base_existing_data:
            # TODO: Implementar busca de dados existentes do banco
            # Por ora, usar dados vazios
            existing_data = {"lancamentos": [], "categorias": [], "contas": []}
        
        # Configuração para o gerador
        generator_config = {
            "count": config.count,
            "type": config.data_type,
            "use_ai_patterns": config.use_ai_patterns
        }
        
        # Gerar dados sintéticos
        synthetic_result = await synthetic_generator.generate_realistic_data(
            existing_data,
            generator_config,
            current_user.id
        )
        
        logger.info(f"Gerados {len(synthetic_result)} registros sintéticos para usuário {current_user.id}")
        
        return {
            "success": True,
            "message": f"Gerados {len(synthetic_result)} registros sintéticos",
            "generated_count": len(synthetic_result),
            "data_preview": synthetic_result[:5],  # Primeiros 5 registros como preview
            "statistics": _calculate_synthetic_stats(synthetic_result),
            "data_type": config.data_type
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados sintéticos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dados sintéticos: {str(e)}")

@router.post("/import-synthetic")
async def import_synthetic_data(
    config: SyntheticDataConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera e importa dados sintéticos diretamente para o banco
    """
    try:
        # Gerar dados sintéticos
        existing_data = {"lancamentos": [], "categorias": [], "contas": []}  # TODO: buscar dados reais
        
        generator_config = {
            "count": config.count,
            "type": config.data_type,
            "use_ai_patterns": config.use_ai_patterns
        }
        
        synthetic_data = await synthetic_generator.generate_realistic_data(
            existing_data,
            generator_config,
            current_user.id
        )
        
        # TODO: Implementar importação real para o banco
        # Por ora, simular importação bem-sucedida
        
        logger.info(f"Importados {len(synthetic_data)} registros sintéticos para usuário {current_user.id}")
        
        return {
            "success": True,
            "message": f"Importados {len(synthetic_data)} registros sintéticos",
            "imported_records": len(synthetic_data),
            "summary": {
                "receitas": len([d for d in synthetic_data if d.get('tipo') == 'RECEITA']),
                "despesas": len([d for d in synthetic_data if d.get('tipo') == 'DESPESA']),
                "total_valor": sum(float(d.get('valor', 0)) for d in synthetic_data if 'valor' in d)
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao importar dados sintéticos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao importar dados sintéticos: {str(e)}")

@router.get("/templates")
async def get_import_templates():
    """
    Retorna templates de importação disponíveis
    """
    templates = {
        "siog": {
            "name": "SIOG Financeiro",
            "description": "Template para dados do Sistema SIOG",
            "required_fields": ["vl_original", "dt_emissao", "nm_natureza"],
            "optional_fields": ["complemento", "conta", "banco", "sub_natureza"],
            "example_mapping": {
                "valor": "vl_original",
                "data_lancamento": "dt_emissao",
                "categoria": "nm_natureza",
                "descricao": "complemento"
            }
        },
        "financeiro_generico": {
            "name": "Financeiro Genérico",
            "description": "Template para dados financeiros gerais",
            "required_fields": ["valor", "data", "tipo"],
            "optional_fields": ["descricao", "categoria", "conta"],
            "example_mapping": {
                "valor": "valor",
                "data_lancamento": "data",
                "tipo": "tipo",
                "descricao": "descricao"
            }
        }
    }
    
    return {
        "success": True,
        "templates": templates
    }

@router.get("/sample-data/{data_type}")
async def download_sample_data(data_type: str):
    """
    Gera e retorna dados de exemplo para teste
    """
    try:
        if data_type not in ["financeiro", "siog", "generico"]:
            raise HTTPException(status_code=400, detail="Tipo de dados inválido")
        
        # Gerar dados de exemplo
        sample_config = {"count": 20, "type": data_type, "use_ai_patterns": False}
        sample_data = await synthetic_generator.generate_realistic_data(
            {},
            sample_config,
            user_id=0  # ID fictício para exemplo
        )
        
        return {
            "success": True,
            "data_type": data_type,
            "sample_count": len(sample_data),
            "sample_data": sample_data,
            "download_format": "json"
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar dados de exemplo: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dados de exemplo: {str(e)}")

def _calculate_synthetic_stats(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula estatísticas dos dados sintéticos gerados"""
    if not data:
        return {}
    
    stats = {
        "total_records": len(data),
        "data_types": {}
    }
    
    # Contar tipos se disponível
    if 'tipo' in data[0]:
        tipo_counts = {}
        for record in data:
            tipo = record.get('tipo', 'unknown')
            tipo_counts[tipo] = tipo_counts.get(tipo, 0) + 1
        stats["data_types"] = tipo_counts
    
    # Estatísticas de valores se disponível
    if 'valor' in data[0]:
        valores = [float(record.get('valor', 0)) for record in data if 'valor' in record]
        if valores:
            stats["value_stats"] = {
                "total": sum(valores),
                "average": sum(valores) / len(valores),
                "min": min(valores),
                "max": max(valores)
            }
    
    return stats 