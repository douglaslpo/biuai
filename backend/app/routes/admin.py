"""
Rotas administrativas para gestão de usuários, módulos e permissões
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.role import Role, Permission
from app.models.module import Module, TenantModule
from app.auth.jwt import get_current_user
from app.core.permissions import get_permissions_for_role

router = APIRouter(prefix="/admin", tags=["admin"])


def require_permission(permission: str):
    """Decorator para verificar permissões"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Não autenticado")
            
            if not current_user.has_permission(permission):
                raise HTTPException(status_code=403, detail="Permissão negada")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ===== GESTÃO DE USUÁRIOS =====

@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    """Listar usuários com paginação e busca"""
    if not current_user.has_permission("core.user.read"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    query = select(User).options(
        selectinload(User.roles),
        selectinload(User.tenant)
    )
    
    # Filtro por tenant (exceto super admin)
    if not current_user.is_superuser:
        query = query.where(User.tenant_id == current_user.tenant_id)
    
    # Busca por nome ou email
    if search:
        query = query.where(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    # Paginação
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Converter para dict
    users_data = []
    for user in users:
        user_dict = user.dict()
        user_dict["tenant_name"] = user.tenant.name if user.tenant else None
        user_dict["roles"] = [{"name": role.name, "display_name": role.display_name} for role in user.roles]
        users_data.append(user_dict)
    
    return {
        "users": users_data,
        "page": page,
        "size": size,
        "total": len(users_data)
    }


@router.post("/users")
async def create_user(
    user_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo usuário"""
    if not current_user.has_permission("core.user.create"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Verificar se email já existe
    result = await db.execute(select(User).where(User.email == user_data["email"]))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Definir tenant
    tenant_id = user_data.get("tenant_id")
    if not current_user.is_superuser:
        tenant_id = current_user.tenant_id
    
    # Verificar se pode adicionar usuário ao tenant
    if tenant_id:
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        if tenant and not tenant.can_add_user():
            raise HTTPException(status_code=400, detail="Limite de usuários atingido")
    
    # Criar usuário
    new_user = User(
        full_name=user_data["full_name"],
        email=user_data["email"],
        hashed_password=User.gerar_hash_senha(user_data["password"]),
        tenant_id=tenant_id,
        is_active=user_data.get("is_active", True)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Atribuir role padrão
    role_name = user_data.get("role", "user")
    result = await db.execute(select(Role).where(Role.name == role_name))
    role = result.scalar_one_or_none()
    if role:
        new_user.roles.append(role)
        await db.commit()
    
    return {"message": "Usuário criado com sucesso", "user_id": new_user.id}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar usuário"""
    if not current_user.has_permission("core.user.update"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Buscar usuário
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se pode gerenciar este usuário
    if not current_user.can_manage_user(user):
        raise HTTPException(status_code=403, detail="Não pode gerenciar este usuário")
    
    # Atualizar campos
    for field, value in user_data.items():
        if field == "password" and value:
            user.hashed_password = User.gerar_hash_senha(value)
        elif hasattr(user, field) and field not in ["id", "created_at", "hashed_password"]:
            setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {"message": "Usuário atualizado com sucesso"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desativar usuário"""
    if not current_user.has_permission("core.user.delete"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Buscar usuário
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se pode gerenciar este usuário
    if not current_user.can_manage_user(user):
        raise HTTPException(status_code=403, detail="Não pode gerenciar este usuário")
    
    # Não permitir deletar a si mesmo
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não pode deletar a si mesmo")
    
    # Desativar em vez de deletar
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {"message": "Usuário desativado com sucesso"}


# ===== GESTÃO DE ROLES E PERMISSÕES =====

@router.get("/roles")
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar roles disponíveis"""
    if not current_user.has_permission("admin.role.read"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    result = await db.execute(
        select(Role).options(selectinload(Role.permissions))
    )
    roles = result.scalars().all()
    
    roles_data = []
    for role in roles:
        # Filtrar roles que o usuário pode gerenciar
        if current_user.is_superuser or current_user.get_role_level() > role.level:
            role_dict = {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "level": role.level,
                "permissions": [p.name for p in role.permissions]
            }
            roles_data.append(role_dict)
    
    return {"roles": roles_data}


@router.put("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: int,
    roles_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atribuir roles a um usuário"""
    if not current_user.has_permission("admin.permission.assign"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Buscar usuário
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se pode gerenciar este usuário
    if not current_user.can_manage_user(user):
        raise HTTPException(status_code=403, detail="Não pode gerenciar este usuário")
    
    # Buscar novos roles
    role_names = roles_data.get("roles", [])
    result = await db.execute(select(Role).where(Role.name.in_(role_names)))
    new_roles = result.scalars().all()
    
    # Verificar se pode atribuir estes roles
    for role in new_roles:
        if not current_user.is_superuser and current_user.get_role_level() <= role.level:
            raise HTTPException(
                status_code=403, 
                detail=f"Não pode atribuir o role {role.display_name}"
            )
    
    # Atualizar roles
    user.roles.clear()
    user.roles.extend(new_roles)
    await db.commit()
    
    return {"message": "Roles atribuídos com sucesso"}


# ===== GESTÃO DE MÓDULOS =====

@router.get("/modules")
async def list_modules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar módulos disponíveis"""
    if not current_user.has_permission("admin.module.assign"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    result = await db.execute(select(Module))
    modules = result.scalars().all()
    
    modules_data = []
    for module in modules:
        module_dict = {
            "id": module.id,
            "name": module.name,
            "display_name": module.display_name,
            "description": module.description,
            "version": module.version,
            "status": module.status,
            "is_free": module.is_free,
            "price_monthly": module.price_monthly,
            "price_yearly": module.price_yearly,
            "dependencies": module.dependencies
        }
        modules_data.append(module_dict)
    
    return {"modules": modules_data}


@router.get("/tenants/{tenant_id}/modules")
async def list_tenant_modules(
    tenant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar módulos de um tenant"""
    if not current_user.has_permission("admin.module.assign"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Verificar acesso ao tenant
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado ao tenant")
    
    result = await db.execute(
        select(TenantModule).options(
            selectinload(TenantModule.module)
        ).where(TenantModule.tenant_id == tenant_id)
    )
    tenant_modules = result.scalars().all()
    
    modules_data = []
    for tm in tenant_modules:
        module_dict = {
            "id": tm.module.id,
            "name": tm.module.name,
            "display_name": tm.module.display_name,
            "is_active": tm.is_active,
            "is_trial": tm.is_trial,
            "trial_ends_at": tm.trial_ends_at,
            "enabled_at": tm.enabled_at,
            "settings": tm.settings
        }
        modules_data.append(module_dict)
    
    return {"modules": modules_data}


@router.post("/tenants/{tenant_id}/modules/{module_id}")
async def assign_module_to_tenant(
    tenant_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atribuir módulo a um tenant"""
    if not current_user.has_permission("admin.module.assign"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Verificar acesso ao tenant
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado ao tenant")
    
    # Verificar se já existe
    result = await db.execute(
        select(TenantModule).where(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_id == module_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Módulo já atribuído")
    
    # Buscar módulo
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    
    # Criar atribuição
    tenant_module = TenantModule(
        tenant_id=tenant_id,
        module_id=module_id,
        is_active=True,
        settings=module.default_settings or {},
        enabled_at=datetime.now(timezone.utc),
        enabled_by=current_user.id
    )
    
    # Se módulo é pago, dar trial
    if not module.is_free:
        tenant_module.is_trial = True
        tenant_module.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    db.add(tenant_module)
    await db.commit()
    
    return {"message": "Módulo atribuído com sucesso"}


@router.delete("/tenants/{tenant_id}/modules/{module_id}")
async def remove_module_from_tenant(
    tenant_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remover módulo de um tenant"""
    if not current_user.has_permission("admin.module.assign"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Verificar acesso ao tenant
    if not current_user.is_superuser and current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Acesso negado ao tenant")
    
    # Buscar atribuição
    result = await db.execute(
        select(TenantModule).where(
            TenantModule.tenant_id == tenant_id,
            TenantModule.module_id == module_id
        )
    )
    tenant_module = result.scalar_one_or_none()
    if not tenant_module:
        raise HTTPException(status_code=404, detail="Atribuição não encontrada")
    
    # Verificar se é módulo core (não pode ser removido)
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    if module and module.name == "core":
        raise HTTPException(status_code=400, detail="Módulo core não pode ser removido")
    
    # Desativar em vez de deletar
    tenant_module.is_active = False
    await db.commit()
    
    return {"message": "Módulo removido com sucesso"}


# ===== DASHBOARD ADMINISTRATIVO =====

@router.get("/dashboard")
async def admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Dashboard administrativo com estatísticas"""
    if not current_user.has_permission("admin.usage.read"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    stats = {}
    
    # Estatísticas de usuários
    if current_user.is_superuser:
        # Super admin vê tudo
        result = await db.execute(select(User))
        total_users = len(result.scalars().all())
        
        result = await db.execute(select(User).where(User.is_active == True))
        active_users = len(result.scalars().all())
        
        result = await db.execute(select(Tenant))
        total_tenants = len(result.scalars().all())
        
        stats.update({
            "total_users": total_users,
            "active_users": active_users,
            "total_tenants": total_tenants
        })
    else:
        # Admin do tenant vê apenas seu tenant
        result = await db.execute(
            select(User).where(User.tenant_id == current_user.tenant_id)
        )
        tenant_users = result.scalars().all()
        
        stats.update({
            "tenant_users": len(tenant_users),
            "active_tenant_users": len([u for u in tenant_users if u.is_active])
        })
    
    # Estatísticas de módulos
    result = await db.execute(select(Module))
    total_modules = len(result.scalars().all())
    
    result = await db.execute(select(Module).where(Module.is_free == True))
    free_modules = len(result.scalars().all())
    
    stats.update({
        "total_modules": total_modules,
        "free_modules": free_modules,
        "paid_modules": total_modules - free_modules
    })
    
    return {"stats": stats}


# ===== LOGS E AUDITORIA =====

@router.get("/logs")
async def get_system_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100)
):
    """Visualizar logs do sistema"""
    if not current_user.has_permission("system.logs.read"):
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # TODO: Implementar busca de logs do banco ou arquivo
    # Por enquanto retorna placeholder
    return {
        "logs": [],
        "page": page,
        "size": size,
        "total": 0,
        "message": "Logs serão implementados em versão futura"
    } 