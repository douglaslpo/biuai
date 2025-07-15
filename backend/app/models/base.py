from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

class TenantMixin:
    """Mixin para adicionar suporte a multi-tenancy"""
    
    @declared_attr
    def tenant_id(cls):
        return Column(Integer, ForeignKey("tenants.id"), nullable=False)
        
    @declared_attr
    def tenant(cls):
        return relationship("Tenant")
    
    @hybrid_property
    def is_active(self):
        """Verifica se o tenant está ativo"""
        return self.tenant.is_active if self.tenant else False

class BaseModel(Base):
    """Modelo base com suporte a timestamps e soft delete"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
    
    def soft_delete(self, session: Session) -> None:
        """Realiza soft delete do registro"""
        self.deleted_at = datetime.utcnow()
        session.add(self)
        session.commit()
    
    def restore(self, session: Session) -> None:
        """Restaura um registro soft deleted"""
        self.deleted_at = None
        session.add(self)
        session.commit()

class TenantModel(BaseModel, TenantMixin):
    """Modelo base com suporte a multi-tenancy"""
    __abstract__ = True

# Event listeners para garantir tenant_id
@event.listens_for(TenantModel, 'before_insert', propagate=True)
def tenant_model_before_insert(mapper, connection, target):
    """Garante que tenant_id está presente antes de inserir"""
    if target.tenant_id is None:
        raise ValueError("tenant_id é obrigatório")

@event.listens_for(Session, 'after_begin')
def session_after_begin(session, transaction, connection):
    """Configura filtro de tenant automaticamente"""
    if hasattr(session, 'tenant_id'):
        for mapper in session.get_bind().get_table_names():
            if issubclass(mapper.class_, TenantModel):
                session.enable_relationship_loading(mapper)
                session.add_filter(
                    lambda cls: cls.tenant_id == session.tenant_id,
                    mapper,
                    allow_none=False
                ) 