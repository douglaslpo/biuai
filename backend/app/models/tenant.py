from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel
from typing import Dict, Any

class Tenant(BaseModel):
    __tablename__ = "tenants"
    """Modelo para gerenciar tenants do sistema"""
    
    # Informações básicas
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    domain = Column(String(255), nullable=True, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Configurações
    settings = Column(JSON, default={}, nullable=False)
    features = Column(JSON, default={}, nullable=False)
    
    # Limites e quotas
    max_users = Column(Integer, default=5, nullable=False)
    max_storage_gb = Column(Integer, default=1, nullable=False)
    
    # Datas importantes
    subscription_ends_at = Column(DateTime, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    last_billing_at = Column(DateTime, nullable=True)
    
    # Metadados
    tenant_meta_info = Column(JSON, default={}, nullable=False)
    
    # Relacionamentos
    users = relationship("User", back_populates="tenant")
    modules = relationship("TenantModule", back_populates="tenant")
    
    @property
    def is_on_trial(self) -> bool:
        """Verifica se o tenant está em período de trial"""
        if not self.trial_ends_at:
            return False
        return datetime.utcnow() < self.trial_ends_at
    
    @property
    def is_subscription_active(self) -> bool:
        """Verifica se a assinatura está ativa"""
        if not self.subscription_ends_at:
            return False
        return datetime.utcnow() < self.subscription_ends_at
    
    @property
    def has_active_subscription(self) -> bool:
        """Verifica se tem acesso ao sistema"""
        return self.is_active and (self.is_on_trial or self.is_subscription_active)
    
    def get_feature_flag(self, feature: str) -> bool:
        """Obtém status de uma feature flag"""
        return self.features.get(feature, False)
    
    def get_setting(self, key: str, default: any = None) -> any:
        """Obtém uma configuração do tenant"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: any) -> None:
        """Define uma configuração do tenant"""
        self.settings[key] = value
    
    def get_meta_info(self, key: str, default: any = None) -> any:
        """Obtém um metadado do tenant"""
        return self.tenant_meta_info.get(key, default)
    
    def set_meta_info(self, key: str, value: any) -> None:
        """Define um metadado do tenant"""
        self.tenant_meta_info[key] = value
    
    def __str__(self):
        return f"Tenant({self.name})"
    
    def get_user_count(self) -> int:
        """Get current user count for this tenant"""
        return len([u for u in self.users if u.is_active])
    
    def can_add_user(self) -> bool:
        """Check if tenant can add more users"""
        return self.get_user_count() < self.max_users 