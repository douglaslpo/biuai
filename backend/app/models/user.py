from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import Optional, List
from datetime import datetime

from app.models.base import Base
from app.core.security import verify_password, get_password_hash
from app.models.role import user_roles

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Status do usuário
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Multi-tenancy
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    
    # Informações adicionais
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="pt-BR")
    
    # Configurações do usuário
    settings = Column(String, default="{}")  # JSON string for user settings
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    # Relacionamentos com dados do usuário
    categorias = relationship("Categoria", back_populates="user")
    lancamentos = relationship("Lancamento", back_populates="user")
    contas = relationship("Conta", back_populates="user")
    metas = relationship("MetaFinanceira", back_populates="user")
    fiis = relationship("FII", back_populates="user")

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Optional["User"]:
        """Get user by email"""
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> Optional["User"]:
        """Get user by ID"""
        result = await db.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()

    async def save(self, db: AsyncSession):
        """Save user to database"""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self

    async def update(self, db: AsyncSession, **kwargs):
        """Update user"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(self)
        return self

    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        return verify_password(senha_plana, senha_hash)

    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        return get_password_hash(senha)

    @classmethod
    async def criar_usuario(cls, nome: str, email: str, senha: str, tenant_id: int = None):
        senha_hash = cls.gerar_hash_senha(senha)
        return cls(
            full_name=nome, 
            email=email, 
            hashed_password=senha_hash,
            tenant_id=tenant_id
        )

    @classmethod
    async def autenticar(cls, email: str, senha: str):
        # Este método será implementado com a sessão do banco
        pass

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        # Check role permissions
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        
        # Check direct user permissions
        # TODO: Implement user-specific permissions
        return False

    def get_role_level(self) -> int:
        """Get the highest role level for this user"""
        if not self.roles:
            return 0
        return max(role.level for role in self.roles)

    def can_manage_user(self, other_user: "User") -> bool:
        """Check if this user can manage another user"""
        # Super admin can manage everyone
        if self.is_superuser:
            return True
        
        # Must be in same tenant
        if self.tenant_id != other_user.tenant_id:
            return False
        
        # Must have higher role level
        return self.get_role_level() > other_user.get_role_level()

    def get_accessible_modules(self) -> List[str]:
        """Get list of modules this user can access"""
        if not self.tenant:
            return []
        
        # Get all active modules for this tenant
        accessible_modules = []
        for tenant_module in self.tenant.modules:
            if tenant_module.is_active and tenant_module.module.is_available():
                accessible_modules.append(tenant_module.module.name)
        
        return accessible_modules

    def dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "tenant_id": self.tenant_id,
            "roles": [role.name for role in self.roles] if self.roles else [],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_login": self.last_login
        } 