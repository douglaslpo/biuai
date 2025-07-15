from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class UserRole(str, enum.Enum):
    """Hierarquia de usuários no sistema SaaS"""
    SUPER_ADMIN = "super_admin"      # Master do sistema
    TENANT_ADMIN = "tenant_admin"    # Admin do tenant
    SUB_ADMIN = "sub_admin"          # Admin delegado
    USER = "user"                    # Usuário final

# Tabela de associação para many-to-many entre User e Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Tabela de associação para many-to-many entre Role e Permission
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Role(Base):
    """Modelo de Role para RBAC"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Hierarquia de roles
    level = Column(Integer, default=0)  # 0=user, 1=sub_admin, 2=tenant_admin, 3=super_admin
    
    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # Role do sistema (não pode ser deletada)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def __str__(self):
        return f"Role({self.name})"
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission"""
        return any(p.name == permission_name for p in self.permissions)
    
    def can_manage_role(self, other_role: "Role") -> bool:
        """Check if this role can manage another role"""
        return self.level > other_role.level

class Permission(Base):
    """Modelo de Permission para RBAC"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    
    # Categorização
    module = Column(String(50), nullable=False)  # core, financial, investments, etc.
    category = Column(String(50), nullable=False)  # user, data, admin, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __str__(self):
        return f"Permission({self.name})"

class UserPermission(Base):
    """Permissões específicas do usuário (override das permissões do role)"""
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Override type
    granted = Column(Boolean, default=True)  # True=grant, False=revoke
    
    # Contexto (opcional)
    context = Column(String(255), nullable=True)  # Para permissões contextuais
    
    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relacionamentos
    user = relationship("User", foreign_keys=[user_id])
    permission = relationship("Permission")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __str__(self):
        action = "granted" if self.granted else "revoked"
        return f"UserPermission({self.user.email} - {self.permission.name} - {action})" 