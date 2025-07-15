"""
Script de inicialização do sistema BIUAI SaaS
Cria dados iniciais: tenant, roles, permissions, modules, e usuário admin
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.database import get_db
from app.models.tenant import Tenant
from app.models.role import Role, Permission, user_roles
from app.models.module import Module, TenantModule, ModuleStatus
from app.models.user import User
from app.core.permissions import PERMISSIONS, ROLE_PERMISSIONS, ModuleName
from app.core.config import settings


async def create_default_tenant(db: AsyncSession) -> Tenant:
    """Criar tenant padrão do sistema"""
    # Verificar se já existe
    result = await db.execute(select(Tenant).where(Tenant.slug == "biuai-default"))
    existing_tenant = result.scalar_one_or_none()
    
    if existing_tenant:
        print("✅ Tenant padrão já existe")
        return existing_tenant
    
    tenant = Tenant(
        name="BIUAI Default",
        slug="biuai-default",
        plan_type="enterprise",
        max_users=100,
        max_storage_mb=10000,
        settings={
            "theme": "default",
            "timezone": "America/Sao_Paulo",
            "language": "pt-BR",
            "features": {
                "multi_currency": True,
                "advanced_analytics": True,
                "ai_insights": True
            }
        }
    )
    
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    print("✅ Tenant padrão criado")
    return tenant


async def create_permissions(db: AsyncSession):
    """Criar todas as permissões do sistema"""
    created_count = 0
    
    for perm_name, perm_data in PERMISSIONS.items():
        # Verificar se já existe
        result = await db.execute(select(Permission).where(Permission.name == perm_name))
        existing_perm = result.scalar_one_or_none()
        
        if not existing_perm:
            permission = Permission(
                name=perm_name,
                display_name=perm_data["display_name"],
                description=perm_data["description"],
                module=perm_data["module"],
                category=perm_data["category"]
            )
            db.add(permission)
            created_count += 1
    
    await db.commit()
    print(f"✅ {created_count} permissões criadas")


async def create_roles(db: AsyncSession):
    """Criar roles do sistema"""
    roles_data = [
        {
            "name": "super_admin",
            "display_name": "Super Administrador",
            "description": "Administrador master do sistema",
            "level": 3,
            "is_system": True
        },
        {
            "name": "tenant_admin",
            "display_name": "Administrador do Tenant",
            "description": "Administrador da empresa/organização",
            "level": 2,
            "is_system": True
        },
        {
            "name": "sub_admin",
            "display_name": "Sub Administrador",
            "description": "Administrador delegado",
            "level": 1,
            "is_system": True
        },
        {
            "name": "user",
            "display_name": "Usuário",
            "description": "Usuário final do sistema",
            "level": 0,
            "is_system": True
        }
    ]
    
    created_count = 0
    
    for role_data in roles_data:
        # Verificar se já existe
        result = await db.execute(select(Role).where(Role.name == role_data["name"]))
        existing_role = result.scalar_one_or_none()
        
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            created_count += 1
    
    await db.commit()
    print(f"✅ {created_count} roles criados")


async def assign_permissions_to_roles(db: AsyncSession):
    """Atribuir permissões aos roles"""
    for role_name, permission_names in ROLE_PERMISSIONS.items():
        # Buscar role
        result = await db.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        
        if not role:
            continue
        
        # Buscar permissões
        for perm_name in permission_names:
            result = await db.execute(select(Permission).where(Permission.name == perm_name))
            permission = result.scalar_one_or_none()
            
            if permission and permission not in role.permissions:
                role.permissions.append(permission)
    
    await db.commit()
    print("✅ Permissões atribuídas aos roles")


async def create_modules(db: AsyncSession):
    """Criar módulos do sistema"""
    modules_data = [
        {
            "name": "core",
            "display_name": "Core",
            "description": "Módulo principal do sistema",
            "is_free": True,
            "dependencies": [],
            "default_settings": {
                "enabled": True,
                "auto_update": True
            }
        },
        {
            "name": "financial",
            "display_name": "Financeiro",
            "description": "Gestão financeira completa",
            "is_free": True,
            "dependencies": ["core"],
            "max_records": 5000,
            "default_settings": {
                "auto_categorize": True,
                "currency": "BRL"
            }
        },
        {
            "name": "investments",
            "display_name": "Investimentos",
            "description": "Análise e gestão de investimentos",
            "is_free": False,
            "price_monthly": 29.90,
            "price_yearly": 299.00,
            "dependencies": ["core", "financial"],
            "max_records": 1000,
            "default_settings": {
                "auto_sync": True,
                "risk_analysis": True
            }
        },
        {
            "name": "ai_insights",
            "display_name": "Insights de IA",
            "description": "Análises inteligentes com IA",
            "is_free": False,
            "price_monthly": 49.90,
            "price_yearly": 499.00,
            "dependencies": ["core", "financial"],
            "max_api_calls": 1000,
            "default_settings": {
                "auto_insights": True,
                "frequency": "daily"
            }
        },
        {
            "name": "chatbot",
            "display_name": "Chatbot",
            "description": "Assistente virtual inteligente",
            "is_free": False,
            "price_monthly": 19.90,
            "price_yearly": 199.00,
            "dependencies": ["core"],
            "max_api_calls": 500,
            "default_settings": {
                "personality": "professional",
                "context_memory": True
            }
        },
        {
            "name": "analytics",
            "display_name": "Analytics Avançado",
            "description": "Relatórios e dashboards avançados",
            "is_free": False,
            "price_monthly": 39.90,
            "price_yearly": 399.00,
            "dependencies": ["core", "financial"],
            "max_records": 10000,
            "default_settings": {
                "auto_reports": True,
                "export_formats": ["pdf", "excel", "csv"]
            }
        }
    ]
    
    created_count = 0
    
    for module_data in modules_data:
        # Verificar se já existe
        result = await db.execute(select(Module).where(Module.name == module_data["name"]))
        existing_module = result.scalar_one_or_none()
        
        if not existing_module:
            module = Module(**module_data)
            db.add(module)
            created_count += 1
    
    await db.commit()
    print(f"✅ {created_count} módulos criados")


async def assign_modules_to_tenant(db: AsyncSession, tenant: Tenant):
    """Atribuir módulos ao tenant padrão"""
    # Buscar todos os módulos
    result = await db.execute(select(Module))
    modules = result.scalars().all()
    
    assigned_count = 0
    
    for module in modules:
        # Verificar se já está atribuído
        result = await db.execute(
            select(TenantModule).where(
                TenantModule.tenant_id == tenant.id,
                TenantModule.module_id == module.id
            )
        )
        existing_assignment = result.scalar_one_or_none()
        
        if not existing_assignment:
            tenant_module = TenantModule(
                tenant_id=tenant.id,
                module_id=module.id,
                is_active=True,
                settings=module.default_settings or {},
                enabled_at=datetime.now(timezone.utc)
            )
            
            # Para módulos pagos, dar trial de 30 dias
            if not module.is_free:
                tenant_module.is_trial = True
                tenant_module.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=30)
            
            db.add(tenant_module)
            assigned_count += 1
    
    await db.commit()
    print(f"✅ {assigned_count} módulos atribuídos ao tenant")


async def create_super_admin(db: AsyncSession, tenant: Tenant):
    """Criar usuário super admin"""
    # Verificar se já existe
    result = await db.execute(select(User).where(User.email == "admin@biuai.com"))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print("✅ Super admin já existe")
        return existing_user
    
    # Criar usuário
    user = User(
        full_name="Administrador do Sistema",
        email="admin@biuai.com",
        hashed_password=User.gerar_hash_senha("admin123"),
        is_active=True,
        is_superuser=True,
        is_verified=True,
        tenant_id=tenant.id,
        timezone="America/Sao_Paulo",
        language="pt-BR"
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Atribuir role de super_admin
    result = await db.execute(select(Role).where(Role.name == "super_admin"))
    super_admin_role = result.scalar_one_or_none()
    
    if super_admin_role:
        user.roles.append(super_admin_role)
        await db.commit()
    
    print("✅ Super admin criado")
    return user


async def init_system_data():
    """Inicializar todos os dados do sistema"""
    print("🚀 Iniciando configuração do sistema BIUAI SaaS...")
    
    async for db in get_db():
        try:
            # 1. Criar tenant padrão
            tenant = await create_default_tenant(db)
            
            # 2. Criar permissões
            await create_permissions(db)
            
            # 3. Criar roles
            await create_roles(db)
            
            # 4. Atribuir permissões aos roles
            await assign_permissions_to_roles(db)
            
            # 5. Criar módulos
            await create_modules(db)
            
            # 6. Atribuir módulos ao tenant
            await assign_modules_to_tenant(db, tenant)
            
            # 7. Criar super admin
            await create_super_admin(db, tenant)
            
            print("✅ Sistema inicializado com sucesso!")
            print(f"📧 Login: admin@biuai.com")
            print(f"🔐 Senha: admin123")
            print(f"🏢 Tenant: {tenant.name} ({tenant.slug})")
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
        break


async def init_myfiis_module(db: AsyncSession) -> None:
    """Inicializa o módulo MyFIIs com dados padrão"""
    from sqlalchemy.future import select

    # Criar módulo MyFIIs
    myfiis_module = Module(
        name="myfiis",
        display_name="MyFIIs - Gestão de Fundos Imobiliários",
        description="Módulo para análise e gestão de Fundos de Investimento Imobiliário (FIIs)",
        version="1.0.0",
        is_core=False,
        is_paid=True,
        is_active=True,
        requires_setup=False,
        dependencies=[],
        default_settings={
            "max_fiis": 100,
            "enable_ai_insights": True,
            "enable_alerts": True,
            "enable_transactions": True
        },
        features=[
            {
                "name": "portfolio",
                "title": "Gestão de Carteira",
                "description": "Gerencie sua carteira de FIIs"
            },
            {
                "name": "analytics",
                "title": "Análises Avançadas",
                "description": "Análises detalhadas com IA"
            },
            {
                "name": "transactions",
                "title": "Controle de Transações",
                "description": "Registre compras e vendas"
            },
            {
                "name": "alerts",
                "title": "Sistema de Alertas",
                "description": "Alertas personalizados"
            }
        ],
        price_monthly=29.90,
        price_yearly=299.90,
        trial_days=30,
        max_users=5,
        max_storage_gb=1,
        api_rate_limit=1000
    )

    # Verificar se módulo já existe
    result = await db.execute(select(Module).where(Module.name == "myfiis"))
    existing_module = result.scalar_one_or_none()
    if not existing_module:
        db.add(myfiis_module)
        await db.commit()
        await db.refresh(myfiis_module)
    else:
        myfiis_module = existing_module

    # Criar tenant de exemplo se não existir
    result = await db.execute(select(Tenant).where(Tenant.slug == "demo"))
    demo_tenant = result.scalar_one_or_none()
    if not demo_tenant:
        demo_tenant = Tenant(
            name="Empresa Demonstração",
            slug="demo",
            domain="demo.biuai.com",
            is_active=True,
            settings={
                "theme": "light",
                "language": "pt-BR",
                "timezone": "America/Sao_Paulo"
            },
            features={
                "enable_ai": True,
                "enable_alerts": True
            },
            max_users=10,
            max_storage_gb=5,
            trial_ends_at=datetime.utcnow() + timedelta(days=30),
            tenant_meta_info={
                "created_by": "system",
                "demo": True
            }
        )
        db.add(demo_tenant)
        await db.commit()
        await db.refresh(demo_tenant)

    # Ativar módulo para o tenant de demo
    result = await db.execute(
        select(TenantModule).where(
            TenantModule.tenant_id == demo_tenant.id,
            TenantModule.module_id == myfiis_module.id
        )
    )
    tenant_module = result.scalar_one_or_none()
    if not tenant_module:
        tenant_module = TenantModule(
            tenant_id=demo_tenant.id,
            module_id=myfiis_module.id,
            is_active=True,
            is_configured=True,
            settings=myfiis_module.default_settings,
            features_enabled=[f["name"] for f in myfiis_module.features],
            activated_at=datetime.utcnow(),
            trial_ends_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(tenant_module)
        await db.commit()
        await db.refresh(tenant_module)


async def init_data(db: AsyncSession) -> None:
    """Inicializa dados do sistema"""
    await init_myfiis_module(db)


if __name__ == "__main__":
    asyncio.run(init_system_data()) 