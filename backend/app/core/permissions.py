from typing import Dict, List, Set
from enum import Enum

class ModuleName(str, Enum):
    """Módulos disponíveis no sistema"""
    CORE = "core"
    FINANCIAL = "financial"
    INVESTMENTS = "investments"
    AI_INSIGHTS = "ai_insights"
    CHATBOT = "chatbot"
    ANALYTICS = "analytics"
    ADMIN = "admin"

class PermissionCategory(str, Enum):
    """Categorias de permissões"""
    USER = "user"
    DATA = "data"
    ADMIN = "admin"
    SYSTEM = "system"
    BILLING = "billing"

# Definição de todas as permissões do sistema
PERMISSIONS: Dict[str, Dict[str, str]] = {
    # CORE MODULE
    "core.user.read": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Visualizar Usuários",
        "description": "Visualizar informações de usuários"
    },
    "core.user.create": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Criar Usuários",
        "description": "Criar novos usuários"
    },
    "core.user.update": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Editar Usuários",
        "description": "Editar informações de usuários"
    },
    "core.user.delete": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Deletar Usuários",
        "description": "Deletar usuários do sistema"
    },
    "core.profile.read": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Visualizar Perfil",
        "description": "Visualizar próprio perfil"
    },
    "core.profile.update": {
        "module": ModuleName.CORE,
        "category": PermissionCategory.USER,
        "display_name": "Editar Perfil",
        "description": "Editar próprio perfil"
    },
    
    # FINANCIAL MODULE
    "financial.lancamento.read": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Lançamentos",
        "description": "Visualizar lançamentos financeiros"
    },
    "financial.lancamento.create": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Criar Lançamentos",
        "description": "Criar novos lançamentos financeiros"
    },
    "financial.lancamento.update": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Editar Lançamentos",
        "description": "Editar lançamentos financeiros"
    },
    "financial.lancamento.delete": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Deletar Lançamentos",
        "description": "Deletar lançamentos financeiros"
    },
    "financial.categoria.read": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Categorias",
        "description": "Visualizar categorias financeiras"
    },
    "financial.categoria.create": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Criar Categorias",
        "description": "Criar novas categorias financeiras"
    },
    "financial.categoria.update": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Editar Categorias",
        "description": "Editar categorias financeiras"
    },
    "financial.categoria.delete": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Deletar Categorias",
        "description": "Deletar categorias financeiras"
    },
    "financial.conta.read": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Contas",
        "description": "Visualizar contas financeiras"
    },
    "financial.conta.create": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Criar Contas",
        "description": "Criar novas contas financeiras"
    },
    "financial.conta.update": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Editar Contas",
        "description": "Editar contas financeiras"
    },
    "financial.conta.delete": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Deletar Contas",
        "description": "Deletar contas financeiras"
    },
    "financial.meta.read": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Metas",
        "description": "Visualizar metas financeiras"
    },
    "financial.meta.create": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Criar Metas",
        "description": "Criar novas metas financeiras"
    },
    "financial.meta.update": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Editar Metas",
        "description": "Editar metas financeiras"
    },
    "financial.meta.delete": {
        "module": ModuleName.FINANCIAL,
        "category": PermissionCategory.DATA,
        "display_name": "Deletar Metas",
        "description": "Deletar metas financeiras"
    },
    
    # INVESTMENTS MODULE
    "investments.fii.read": {
        "module": ModuleName.INVESTMENTS,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar FIIs",
        "description": "Visualizar fundos imobiliários"
    },
    "investments.fii.create": {
        "module": ModuleName.INVESTMENTS,
        "category": PermissionCategory.DATA,
        "display_name": "Criar FIIs",
        "description": "Adicionar novos fundos imobiliários"
    },
    "investments.fii.update": {
        "module": ModuleName.INVESTMENTS,
        "category": PermissionCategory.DATA,
        "display_name": "Editar FIIs",
        "description": "Editar fundos imobiliários"
    },
    "investments.fii.delete": {
        "module": ModuleName.INVESTMENTS,
        "category": PermissionCategory.DATA,
        "display_name": "Deletar FIIs",
        "description": "Deletar fundos imobiliários"
    },
    "investments.analysis.read": {
        "module": ModuleName.INVESTMENTS,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Análises",
        "description": "Visualizar análises de investimentos"
    },
    
    # AI_INSIGHTS MODULE
    "ai_insights.read": {
        "module": ModuleName.AI_INSIGHTS,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Insights de IA",
        "description": "Visualizar insights gerados por IA"
    },
    "ai_insights.generate": {
        "module": ModuleName.AI_INSIGHTS,
        "category": PermissionCategory.DATA,
        "display_name": "Gerar Insights",
        "description": "Gerar novos insights com IA"
    },
    
    # CHATBOT MODULE
    "chatbot.use": {
        "module": ModuleName.CHATBOT,
        "category": PermissionCategory.DATA,
        "display_name": "Usar Chatbot",
        "description": "Interagir com o chatbot"
    },
    "chatbot.history.read": {
        "module": ModuleName.CHATBOT,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Histórico",
        "description": "Visualizar histórico de conversas"
    },
    
    # ANALYTICS MODULE
    "analytics.dashboard.read": {
        "module": ModuleName.ANALYTICS,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Dashboards",
        "description": "Visualizar dashboards analíticos"
    },
    "analytics.report.read": {
        "module": ModuleName.ANALYTICS,
        "category": PermissionCategory.DATA,
        "display_name": "Visualizar Relatórios",
        "description": "Visualizar relatórios analíticos"
    },
    "analytics.report.export": {
        "module": ModuleName.ANALYTICS,
        "category": PermissionCategory.DATA,
        "display_name": "Exportar Relatórios",
        "description": "Exportar relatórios em diferentes formatos"
    },
    
    # ADMIN MODULE
    "admin.tenant.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Visualizar Tenants",
        "description": "Visualizar informações de tenants"
    },
    "admin.tenant.create": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Criar Tenants",
        "description": "Criar novos tenants"
    },
    "admin.tenant.update": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Editar Tenants",
        "description": "Editar configurações de tenants"
    },
    "admin.tenant.delete": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Deletar Tenants",
        "description": "Deletar tenants do sistema"
    },
    "admin.module.assign": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Atribuir Módulos",
        "description": "Atribuir módulos a usuários/tenants"
    },
    "admin.role.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Visualizar Roles",
        "description": "Visualizar roles do sistema"
    },
    "admin.role.create": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Criar Roles",
        "description": "Criar novos roles"
    },
    "admin.role.update": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Editar Roles",
        "description": "Editar roles existentes"
    },
    "admin.role.delete": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Deletar Roles",
        "description": "Deletar roles do sistema"
    },
    "admin.permission.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Visualizar Permissões",
        "description": "Visualizar permissões do sistema"
    },
    "admin.permission.assign": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Atribuir Permissões",
        "description": "Atribuir permissões a roles/usuários"
    },
    "admin.billing.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.BILLING,
        "display_name": "Visualizar Billing",
        "description": "Visualizar informações de cobrança"
    },
    "admin.billing.update": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.BILLING,
        "display_name": "Editar Billing",
        "description": "Editar configurações de cobrança"
    },
    "admin.usage.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.ADMIN,
        "display_name": "Visualizar Uso",
        "description": "Visualizar estatísticas de uso"
    },
    
    # SYSTEM PERMISSIONS
    "system.logs.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.SYSTEM,
        "display_name": "Visualizar Logs",
        "description": "Visualizar logs do sistema"
    },
    "system.settings.read": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.SYSTEM,
        "display_name": "Visualizar Configurações",
        "description": "Visualizar configurações do sistema"
    },
    "system.settings.update": {
        "module": ModuleName.ADMIN,
        "category": PermissionCategory.SYSTEM,
        "display_name": "Editar Configurações",
        "description": "Editar configurações do sistema"
    }
}

# Permissões por role
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "super_admin": list(PERMISSIONS.keys()),  # Super admin tem todas as permissões
    
    "tenant_admin": [
        # Core permissions
        "core.user.read", "core.user.create", "core.user.update", "core.user.delete",
        "core.profile.read", "core.profile.update",
        
        # Financial permissions
        "financial.lancamento.read", "financial.lancamento.create", "financial.lancamento.update", "financial.lancamento.delete",
        "financial.categoria.read", "financial.categoria.create", "financial.categoria.update", "financial.categoria.delete",
        "financial.conta.read", "financial.conta.create", "financial.conta.update", "financial.conta.delete",
        "financial.meta.read", "financial.meta.create", "financial.meta.update", "financial.meta.delete",
        
        # Investments permissions
        "investments.fii.read", "investments.fii.create", "investments.fii.update", "investments.fii.delete",
        "investments.analysis.read",
        
        # AI Insights permissions
        "ai_insights.read", "ai_insights.generate",
        
        # Chatbot permissions
        "chatbot.use", "chatbot.history.read",
        
        # Analytics permissions
        "analytics.dashboard.read", "analytics.report.read", "analytics.report.export",
        
        # Admin permissions (limited)
        "admin.module.assign", "admin.role.read", "admin.permission.read", "admin.permission.assign",
        "admin.billing.read", "admin.usage.read"
    ],
    
    "sub_admin": [
        # Core permissions (limited)
        "core.user.read", "core.profile.read", "core.profile.update",
        
        # Financial permissions
        "financial.lancamento.read", "financial.lancamento.create", "financial.lancamento.update",
        "financial.categoria.read", "financial.categoria.create", "financial.categoria.update",
        "financial.conta.read", "financial.conta.create", "financial.conta.update",
        "financial.meta.read", "financial.meta.create", "financial.meta.update",
        
        # Investments permissions
        "investments.fii.read", "investments.fii.create", "investments.fii.update",
        "investments.analysis.read",
        
        # AI Insights permissions
        "ai_insights.read", "ai_insights.generate",
        
        # Chatbot permissions
        "chatbot.use", "chatbot.history.read",
        
        # Analytics permissions
        "analytics.dashboard.read", "analytics.report.read", "analytics.report.export"
    ],
    
    "user": [
        # Core permissions (basic)
        "core.profile.read", "core.profile.update",
        
        # Financial permissions (basic)
        "financial.lancamento.read", "financial.lancamento.create", "financial.lancamento.update",
        "financial.categoria.read", "financial.categoria.create",
        "financial.conta.read", "financial.conta.create",
        "financial.meta.read", "financial.meta.create", "financial.meta.update",
        
        # Investments permissions (basic)
        "investments.fii.read", "investments.analysis.read",
        
        # AI Insights permissions (basic)
        "ai_insights.read",
        
        # Chatbot permissions
        "chatbot.use", "chatbot.history.read",
        
        # Analytics permissions (basic)
        "analytics.dashboard.read", "analytics.report.read"
    ]
}

def get_permissions_for_role(role_name: str) -> List[str]:
    """Get all permissions for a specific role"""
    return ROLE_PERMISSIONS.get(role_name, [])

def get_permissions_by_module(module_name: str) -> List[str]:
    """Get all permissions for a specific module"""
    return [perm for perm, details in PERMISSIONS.items() 
            if details["module"] == module_name]

def get_permissions_by_category(category: str) -> List[str]:
    """Get all permissions for a specific category"""
    return [perm for perm, details in PERMISSIONS.items() 
            if details["category"] == category]

def is_valid_permission(permission_name: str) -> bool:
    """Check if a permission exists"""
    return permission_name in PERMISSIONS 