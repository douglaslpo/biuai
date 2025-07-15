from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.tenant import Tenant
from app.models.module import Module, TenantModule
from app.core.security import get_password_hash
from app.models.user import User

class TenantService:
    """Serviço para gerenciar tenants"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_tenant(
        self,
        name: str,
        slug: str,
        email: str,
        password: str,
        domain: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, bool]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tenant:
        """Cria um novo tenant"""
        
        # Verificar se slug já existe
        if self.db.query(Tenant).filter(Tenant.slug == slug).first():
            raise HTTPException(
                status_code=400,
                detail="Slug já está em uso"
            )
        
        # Verificar se domínio já existe
        if domain and self.db.query(Tenant).filter(Tenant.domain == domain).first():
            raise HTTPException(
                status_code=400,
                detail="Domínio já está em uso"
            )
        
        # Criar tenant
        tenant = Tenant(
            name=name,
            slug=slug,
            domain=domain,
            is_active=True,
            settings=settings or {
                "theme": "light",
                "language": "pt-BR",
                "timezone": "America/Sao_Paulo"
            },
            features=features or {
                "enable_ai": True,
                "enable_alerts": True
            },
            max_users=5,
            max_storage_gb=1,
            trial_ends_at=datetime.utcnow() + timedelta(days=30),
            tenant_meta_info=metadata or {}
        )
        
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        
        # Criar usuário admin
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,
            tenant_id=tenant.id,
            full_name=f"Admin {tenant.name}",
            role="TENANT_ADMIN"
        )
        
        self.db.add(admin)
        self.db.commit()
        
        # Ativar módulos gratuitos
        await self._activate_free_modules(tenant)
        
        return tenant
    
    async def update_tenant(
        self,
        tenant_id: int,
        name: Optional[str] = None,
        domain: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, bool]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Tenant]:
        """Atualiza um tenant"""
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return None
        
        # Atualizar campos
        if name:
            tenant.name = name
        if domain:
            if self.db.query(Tenant).filter(
                Tenant.domain == domain,
                Tenant.id != tenant_id
            ).first():
                raise HTTPException(
                    status_code=400,
                    detail="Domínio já está em uso"
                )
            tenant.domain = domain
        if settings:
            tenant.settings.update(settings)
        if features:
            tenant.features.update(features)
        if metadata:
            tenant.tenant_meta_info.update(metadata)
        
        self.db.commit()
        self.db.refresh(tenant)
        
        return tenant
    
    async def delete_tenant(self, tenant_id: int) -> bool:
        """Remove um tenant"""
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return False
        
        # Soft delete
        tenant.deleted_at = datetime.utcnow()
        tenant.is_active = False
        
        self.db.commit()
        
        return True
    
    async def activate_module(
        self,
        tenant_id: int,
        module_name: str,
        trial: bool = False
    ) -> Optional[TenantModule]:
        """Ativa um módulo para um tenant"""
        
        # Obter tenant e módulo
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        module = self.db.query(Module).filter(Module.name == module_name).first()
        
        if not tenant or not module:
            return None
        
        # Verificar se já está ativo
        tenant_module = self.db.query(TenantModule).filter(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_id == module.id
        ).first()
        
        if tenant_module:
            return tenant_module
        
        # Ativar módulo
        tenant_module = TenantModule(
            tenant_id=tenant_id,
            module_id=module.id,
            is_active=True,
            is_configured=True,
            settings=module.default_settings,
            features_enabled=[f["name"] for f in module.features],
            activated_at=datetime.utcnow(),
            trial_ends_at=datetime.utcnow() + timedelta(days=module.trial_days) if trial else None
        )
        
        self.db.add(tenant_module)
        self.db.commit()
        self.db.refresh(tenant_module)
        
        return tenant_module
    
    async def deactivate_module(
        self,
        tenant_id: int,
        module_name: str
    ) -> bool:
        """Desativa um módulo para um tenant"""
        
        # Obter tenant module
        module = self.db.query(Module).filter(Module.name == module_name).first()
        if not module:
            return False
        
        tenant_module = self.db.query(TenantModule).filter(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_id == module.id
        ).first()
        
        if not tenant_module:
            return False
        
        # Desativar módulo
        tenant_module.is_active = False
        tenant_module.deleted_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    async def _activate_free_modules(self, tenant: Tenant) -> None:
        """Ativa módulos gratuitos para um tenant"""
        
        free_modules = self.db.query(Module).filter(
            Module.is_core == True,
            Module.is_paid == False
        ).all()
        
        for module in free_modules:
            await self.activate_module(tenant.id, module.name) 