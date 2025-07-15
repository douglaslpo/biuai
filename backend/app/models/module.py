from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum
from datetime import datetime
from typing import Optional, List, Dict, Any

class ModuleStatus(str, enum.Enum):
    """Status dos módulos"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    BETA = "beta"

class Module(Base):
    """Modelo para gerenciar módulos do sistema"""
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Configurações
    version = Column(String(20), nullable=False)
    is_core = Column(Boolean, default=False, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    requires_setup = Column(Boolean, default=False, nullable=False)
    
    # Dependências e configurações
    dependencies = Column(JSON, default=[], nullable=False)
    default_settings = Column(JSON, default={}, nullable=False)
    features = Column(JSON, default=[], nullable=False)
    
    # Pricing
    price_monthly = Column(Float, nullable=True)
    price_yearly = Column(Float, nullable=True)
    trial_days = Column(Integer, default=30, nullable=False)
    
    # Limites
    max_users = Column(Integer, nullable=True)
    max_storage_gb = Column(Integer, nullable=True)
    api_rate_limit = Column(Integer, nullable=True)
    
    # Configurações
    status = Column(String(20), default=ModuleStatus.ACTIVE)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    tenant_modules = relationship("TenantModule", back_populates="module")
    
    @property
    def is_available(self) -> bool:
        """Verifica se o módulo está disponível para uso"""
        return self.is_active and not self.deleted_at
    
    def get_feature(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de uma feature do módulo"""
        return next((f for f in self.features if f.get('name') == feature_name), None)
    
    def has_feature(self, feature_name: str) -> bool:
        """Verifica se o módulo tem uma feature específica"""
        return any(f.get('name') == feature_name for f in self.features)
    
    def __str__(self):
        return f"Module({self.name})"

class TenantModule(Base):
    """Modelo para gerenciar assinaturas de módulos por tenant"""
    __tablename__ = "tenant_modules"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_configured = Column(Boolean, default=False, nullable=False)
    
    # Configurações
    settings = Column(JSON, default={}, nullable=False)
    features_enabled = Column(JSON, default=[], nullable=False)
    
    # Datas
    activated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
    last_billing_at = Column(DateTime, nullable=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="modules")
    module = relationship("Module", back_populates="tenant_modules")
    
    @property
    def is_on_trial(self) -> bool:
        """Verifica se está em período de trial"""
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
        """Verifica se tem acesso ao módulo"""
        return (
            self.is_active and 
            self.is_configured and
            (self.module.is_core or self.is_on_trial or self.is_subscription_active)
        )
    
    def get_setting(self, key: str, default: any = None) -> any:
        """Obtém uma configuração do módulo"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: any) -> None:
        """Define uma configuração do módulo"""
        self.settings[key] = value
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Verifica se uma feature está habilitada"""
        if not self.module.has_feature(feature_name):
            return False
        return feature_name in self.features_enabled
    
    def __str__(self):
        return f"TenantModule({self.tenant.name} - {self.module.name})"

class ModuleUsage(Base):
    """Tracking de uso dos módulos por tenant"""
    __tablename__ = "module_usage"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    
    # Métricas de uso
    records_count = Column(Integer, default=0)
    api_calls_count = Column(Integer, default=0)
    
    # Período de medição
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    tenant = relationship("Tenant")
    module = relationship("Module")
    
    def __str__(self):
        return f"ModuleUsage({self.tenant.name} - {self.module.name})"
    
    def is_over_limit(self, tenant_module: TenantModule) -> bool:
        """Check if usage is over limits"""
        return (self.records_count > tenant_module.get_max_records() or
                self.api_calls_count > tenant_module.get_max_api_calls()) 