#!/usr/bin/env python3
"""
Script para criar usuário admin no sistema BIUAI
"""

import sys
import os
import asyncio
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Adicionar o diretório backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.core.config import settings

async def create_admin_user():
    """Criar usuário admin"""
    
    # Conectar ao banco
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=True
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Verificar se admin já existe
            result = await session.execute(
                text("SELECT id FROM usuarios WHERE email = :email"),
                {"email": "admin@biuai.com"}
            )
            
            if result.fetchone():
                print("✅ Usuário admin já existe!")
                return
            
            # Gerar hash da senha
            password = "admin123"
            senha_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Criar usuário admin
            await session.execute(
                text("""
                    INSERT INTO usuarios (nome, email, senha_hash, ativo, created_at)
                    VALUES (:nome, :email, :senha_hash, :ativo, NOW())
                """),
                {
                    "nome": "Administrador BIUAI",
                    "email": "admin@biuai.com", 
                    "senha_hash": senha_hash,
                    "ativo": True
                }
            )
            
            await session.commit()
            print("✅ Usuário admin criado com sucesso!")
            print("📧 Email: admin@biuai.com")
            print("🔒 Senha: admin123")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Erro ao criar usuário admin: {e}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin_user()) 