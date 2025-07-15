from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantModuleActivate
)
from app.services.tenant_service import TenantService

router = APIRouter()

@router.post("/register", response_model=TenantResponse)
async def register_tenant(
    tenant_in: TenantCreate,
    db: Session = Depends(deps.get_db)
) -> Tenant:
    """
    Registra um novo tenant.
    """
    service = TenantService(db)
    return await service.create_tenant(
        name=tenant_in.name,
        slug=tenant_in.slug,
        email=tenant_in.admin_email,
        password=tenant_in.admin_password,
        domain=tenant_in.domain,
        settings=tenant_in.settings,
        features=tenant_in.features,
        metadata=tenant_in.meta_info
    )

@router.get("/me", response_model=TenantResponse)
async def get_my_tenant(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Retorna o tenant do usuário atual.
    """
    if not current_user.tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    return current_user.tenant

@router.put("/me", response_model=TenantResponse)
async def update_my_tenant(
    tenant_in: TenantUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Atualiza o tenant do usuário atual.
    """
    if not current_user.tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    if not current_user.is_superuser and current_user.role != "TENANT_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    service = TenantService(db)
    tenant = await service.update_tenant(
        tenant_id=current_user.tenant_id,
        name=tenant_in.name,
        domain=tenant_in.domain,
        settings=tenant_in.settings,
        features=tenant_in.features,
        metadata=tenant_in.meta_info
    )
    
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    return tenant

@router.post("/me/modules/{module_name}/activate", response_model=TenantResponse)
async def activate_module(
    module_name: str,
    activation: TenantModuleActivate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Ativa um módulo para o tenant atual.
    """
    if not current_user.tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    if not current_user.is_superuser and current_user.role != "TENANT_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    service = TenantService(db)
    tenant_module = await service.activate_module(
        tenant_id=current_user.tenant_id,
        module_name=module_name,
        trial=activation.trial
    )
    
    if not tenant_module:
        raise HTTPException(
            status_code=404,
            detail="Módulo não encontrado"
        )
    
    return current_user.tenant

@router.post("/me/modules/{module_name}/deactivate", response_model=TenantResponse)
async def deactivate_module(
    module_name: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Desativa um módulo para o tenant atual.
    """
    if not current_user.tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    if not current_user.is_superuser and current_user.role != "TENANT_ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    service = TenantService(db)
    success = await service.deactivate_module(
        tenant_id=current_user.tenant_id,
        module_name=module_name
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Módulo não encontrado"
        )
    
    return current_user.tenant

# Rotas administrativas (apenas para super admin)

@router.get("/", response_model=List[TenantResponse])
async def list_tenants(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[Tenant]:
    """
    Lista todos os tenants (apenas super admin).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    return db.query(Tenant).offset(skip).limit(limit).all()

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Retorna um tenant específico (apenas super admin).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    return tenant

@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    tenant_in: TenantUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Atualiza um tenant específico (apenas super admin).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    service = TenantService(db)
    tenant = await service.update_tenant(
        tenant_id=tenant_id,
        name=tenant_in.name,
        domain=tenant_in.domain,
        settings=tenant_in.settings,
        features=tenant_in.features,
        metadata=tenant_in.meta_info
    )
    
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    return tenant

@router.delete("/{tenant_id}", response_model=TenantResponse)
async def delete_tenant(
    tenant_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Tenant:
    """
    Remove um tenant (apenas super admin).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Permissão negada"
        )
    
    service = TenantService(db)
    success = await service.delete_tenant(tenant_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Tenant não encontrado"
        )
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    return tenant 