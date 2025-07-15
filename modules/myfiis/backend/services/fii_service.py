"""
Serviço de FIIs para o backend
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
import aiohttp
import pandas as pd

from app.core.security import SecurityAudit
from app.core.config import settings
from ..models.fii import FII, CarteiraFII, AnaliseFII
from ..schemas.fii import FIICreate, FIIUpdate, CarteiraFIICreate, CarteiraFIIUpdate


class FIIService:
    """Serviço para gerenciamento de FIIs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def list_fiis(
        self,
        skip: int = 0,
        limit: int = 100,
        segmento: Optional[str] = None
    ) -> List[FII]:
        """Lista todos os FIIs disponíveis"""
        query = self.db.query(FII)
        
        if segmento:
            query = query.filter(FII.segmento == segmento)
        
        return query.offset(skip).limit(limit).all()
    
    async def search_fiis(self, query: str) -> List[FII]:
        """Busca FIIs por código ou nome"""
        return self.db.query(FII).filter(
            or_(
                FII.codigo.ilike(f"%{query}%"),
                FII.nome.ilike(f"%{query}%")
            )
        ).all()
    
    async def get_fii(self, fii_id: int) -> Optional[FII]:
        """Obtém um FII específico"""
        return self.db.query(FII).filter(FII.id == fii_id).first()
    
    async def create_fii(self, fii: FIICreate) -> FII:
        """Cria um novo FII"""
        db_fii = FII(**fii.dict())
        self.db.add(db_fii)
        self.db.commit()
        self.db.refresh(db_fii)
        return db_fii
    
    async def update_fii(self, fii_id: int, fii_update: FIIUpdate) -> Optional[FII]:
        """Atualiza um FII existente"""
        db_fii = await self.get_fii(fii_id)
        if not db_fii:
            return None
            
        for field, value in fii_update.dict(exclude_unset=True).items():
            setattr(db_fii, field, value)
            
        self.db.commit()
        self.db.refresh(db_fii)
        return db_fii
    
    async def delete_fii(self, fii_id: int) -> bool:
        """Remove um FII"""
        db_fii = await self.get_fii(fii_id)
        if not db_fii:
            return False
            
        self.db.delete(db_fii)
        self.db.commit()
        return True
    
    async def get_user_portfolio(self, user_id: int) -> List[CarteiraFII]:
        """Obtém a carteira de FIIs do usuário"""
        return self.db.query(CarteiraFII).filter(
            CarteiraFII.user_id == user_id
        ).all()
    
    async def add_to_portfolio(
        self,
        user_id: int,
        fii: CarteiraFIICreate
    ) -> CarteiraFII:
        """Adiciona um FII à carteira do usuário"""
        try:
            # Verifica se o FII já existe na carteira
            existing = self.db.query(CarteiraFII).filter(
                CarteiraFII.user_id == user_id,
                CarteiraFII.fii_id == fii.fii_id
            ).first()
            
            if existing:
                # Atualiza quantidade e preço médio
                new_total = (
                    existing.quantidade * existing.preco_medio +
                    fii.quantidade * fii.preco_medio
                )
                new_quantidade = existing.quantidade + fii.quantidade
                existing.quantidade = new_quantidade
                existing.preco_medio = new_total / new_quantidade
                existing.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(existing)
                
                SecurityAudit.log_action(
                    "portfolio_item_updated",
                    details={
                        "user_id": user_id,
                        "fii_id": fii.fii_id,
                        "new_quantity": new_quantidade
                    }
                )
                
                return existing
            
            # Cria novo item na carteira
            db_carteira = CarteiraFII(
                user_id=user_id,
                **fii.dict()
            )
            self.db.add(db_carteira)
            self.db.commit()
            self.db.refresh(db_carteira)
            
            SecurityAudit.log_action(
                "portfolio_item_created",
                details={
                    "user_id": user_id,
                    "fii_id": fii.fii_id
                }
            )
            
            return db_carteira
            
        except Exception as e:
            SecurityAudit.log_error(
                "portfolio_add_failed",
                error=str(e),
                details={
                    "user_id": user_id,
                    "fii_data": fii.dict()
                }
            )
            self.db.rollback()
            raise
    
    async def update_portfolio_item(
        self,
        user_id: int,
        fii_id: int,
        fii_data: CarteiraFIIUpdate
    ) -> Optional[CarteiraFII]:
        """Atualiza um FII na carteira do usuário"""
        try:
            db_carteira = self.db.query(CarteiraFII).filter(
                CarteiraFII.user_id == user_id,
                CarteiraFII.fii_id == fii_id
            ).first()
            
            if not db_carteira:
                return None
            
            # Atualiza apenas campos não nulos
            for field, value in fii_data.dict(exclude_unset=True).items():
                setattr(db_carteira, field, value)
            
            db_carteira.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_carteira)
            
            SecurityAudit.log_action(
                "portfolio_item_updated",
                details={
                    "user_id": user_id,
                    "fii_id": fii_id,
                    "updated_fields": fii_data.dict(exclude_unset=True)
                }
            )
            
            return db_carteira
            
        except Exception as e:
            SecurityAudit.log_error(
                "portfolio_update_failed",
                error=str(e),
                details={
                    "user_id": user_id,
                    "fii_id": fii_id,
                    "fii_data": fii_data.dict()
                }
            )
            self.db.rollback()
            raise
    
    async def remove_from_portfolio(self, user_id: int, fii_id: int) -> bool:
        """Remove um FII da carteira do usuário"""
        try:
            db_carteira = self.db.query(CarteiraFII).filter(
                CarteiraFII.user_id == user_id,
                CarteiraFII.fii_id == fii_id
            ).first()
            
            if not db_carteira:
                return False
            
            self.db.delete(db_carteira)
            self.db.commit()
            
            SecurityAudit.log_action(
                "portfolio_item_deleted",
                details={
                    "user_id": user_id,
                    "fii_id": fii_id
                }
            )
            
            return True
            
        except Exception as e:
            SecurityAudit.log_error(
                "portfolio_deletion_failed",
                error=str(e),
                details={
                    "user_id": user_id,
                    "fii_id": fii_id
                }
            )
            self.db.rollback()
            raise
    
    async def toggle_favorite(self, user_id: int, fii_id: int) -> Optional[bool]:
        """Alterna favorito de um FII"""
        try:
            db_carteira = self.db.query(CarteiraFII).filter(
                CarteiraFII.user_id == user_id,
                CarteiraFII.fii_id == fii_id
            ).first()
            
            if not db_carteira:
                return None
            
            db_carteira.favorito = not db_carteira.favorito
            db_carteira.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_carteira)
            
            SecurityAudit.log_action(
                "portfolio_favorite_toggled",
                details={
                    "user_id": user_id,
                    "fii_id": fii_id,
                    "favorito": db_carteira.favorito
                }
            )
            
            return db_carteira.favorito
            
        except Exception as e:
            SecurityAudit.log_error(
                "portfolio_favorite_toggle_failed",
                error=str(e),
                details={
                    "user_id": user_id,
                    "fii_id": fii_id
                }
            )
            self.db.rollback()
            raise
    
    async def set_alert(
        self,
        user_id: int,
        fii_id: int,
        preco_alerta: float
    ) -> Optional[Dict[str, Any]]:
        """Configura alerta de preço para um FII"""
        try:
            db_carteira = self.db.query(CarteiraFII).filter(
                CarteiraFII.user_id == user_id,
                CarteiraFII.fii_id == fii_id
            ).first()
            
            if not db_carteira:
                return None
            
            db_carteira.alerta_ativo = True
            db_carteira.preco_alerta = preco_alerta
            db_carteira.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_carteira)
            
            SecurityAudit.log_action(
                "portfolio_alert_set",
                details={
                    "user_id": user_id,
                    "fii_id": fii_id,
                    "preco_alerta": preco_alerta
                }
            )
            
            return {
                "alerta_ativo": db_carteira.alerta_ativo,
                "preco_alerta": db_carteira.preco_alerta
            }
            
        except Exception as e:
            SecurityAudit.log_error(
                "portfolio_alert_set_failed",
                error=str(e),
                details={
                    "user_id": user_id,
                    "fii_id": fii_id,
                    "preco_alerta": preco_alerta
                }
            )
            self.db.rollback()
            raise
    
    async def get_historical_data(
        self,
        fii_id: int,
        period: str = "1y"
    ) -> List[Dict[str, Any]]:
        """Obtém dados históricos de um FII
        
        Args:
            fii_id: ID do FII
            period: Período dos dados (1m, 3m, 6m, 1y, 2y, 5y)
            
        Returns:
            Lista de dicionários com dados históricos
        """
        try:
            # Busca o FII
            fii = await self.get_fii(fii_id)
            if not fii:
                return []
                
            # Calcula datas
            end_date = datetime.now()
            periods = {
                "1m": 30,
                "3m": 90,
                "6m": 180,
                "1y": 365,
                "2y": 730,
                "5y": 1825
            }
            days = periods.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            # Busca dados da API externa
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{settings.MARKET_DATA_API_URL}/historical/{fii.codigo}",
                    params={
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "api_key": settings.MARKET_DATA_API_KEY
                    }
                ) as response:
                    if response.status != 200:
                        return []
                        
                    data = await response.json()
                    
            # Processa e formata dados
            historical_data = []
            for item in data:
                historical_data.append({
                    "data": item["date"],
                    "preco_fechamento": float(item["close"]),
                    "preco_abertura": float(item["open"]),
                    "preco_maximo": float(item["high"]),
                    "preco_minimo": float(item["low"]),
                    "volume": int(item["volume"]),
                    "dividend_yield": float(item.get("dividend_yield", 0)),
                    "valor_patrimonial": float(item.get("nav", 0))
                })
                
            # Ordena por data
            historical_data.sort(key=lambda x: x["data"])
            
            SecurityAudit.log_action(
                "historical_data_fetched",
                details={
                    "fii_id": fii_id,
                    "period": period,
                    "records": len(historical_data)
                }
            )
            
            return historical_data
            
        except Exception as e:
            SecurityAudit.log_error(
                "historical_data_fetch_failed",
                error=str(e),
                details={
                    "fii_id": fii_id,
                    "period": period
                }
            )
            return [] 