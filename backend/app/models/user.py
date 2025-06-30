from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

from app.models.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

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
        return pwd_context.verify(senha_plana, senha_hash)

    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        return pwd_context.hash(senha)

    @classmethod
    async def criar_usuario(cls, nome: str, email: str, senha: str):
        senha_hash = cls.gerar_hash_senha(senha)
        return cls(full_name=nome, email=email, hashed_password=senha_hash)

    @classmethod
    async def autenticar(cls, email: str, senha: str):
        # Este método será implementado com a sessão do banco
        pass

    def dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        } 