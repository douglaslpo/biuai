#!/usr/bin/env python3
"""
Script para criar usuário admin no sistema BIUAI
Versão atualizada que usa a tabela 'users' correta
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

try:
    from app.core.config import settings
    from app.core.security import get_password_hash
    USE_BCRYPT = True
    print("🔐 Usando bcrypt do sistema (recomendado)")
except ImportError:
    print("⚠️  Usando SHA256 como fallback")
    USE_BCRYPT = False

async def create_admin_user():
    """Criar usuário admin na tabela users (atual)"""
    
    # Conectar ao banco (usando variáveis de ambiente ou padrão Docker Compose)
    POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "db")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "biuai")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "biuai123")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "biuai")
    database_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:5432/{POSTGRES_DB}"
    engine = create_async_engine(database_url, echo=False)  # Reduzir verbosidade
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Verificar se admin existe na tabela ATUAL (users)
            result = await session.execute(
                text("SELECT id, email FROM users WHERE email = :email"),
                {"email": "admin@biuai.com"}
            )
            
            existing_user = result.fetchone()
            if existing_user:
                print("✅ Usuário admin já existe na tabela 'users' (atual)!")
                print(f"📧 Email: {existing_user.email}")
                print(f"🔢 ID: {existing_user.id}")
                return
            
            # Verificar se existe na tabela ANTIGA (usuarios) para migração
            try:
                result_old = await session.execute(
                    text("SELECT id, email, nome FROM usuarios WHERE email = :email"),
                    {"email": "admin@biuai.com"}
                )
                old_user = result_old.fetchone()
                if old_user:
                    print(f"ℹ️  Encontrado usuário na tabela antiga 'usuarios': {old_user.nome}")
                    print("🔄 Migrando para tabela atual 'users'...")
            except:
                old_user = None
            
            # Gerar hash da senha
            password = "admin123"
            if USE_BCRYPT:
                hashed_password = get_password_hash(password)
                print("🔐 Senha criptografada com bcrypt")
            else:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                print("🔐 Senha criptografada com SHA256 (fallback)")
            
            # Criar usuário admin na tabela ATUAL (users)
            await session.execute(
                text("""
                    INSERT INTO users (full_name, email, hashed_password, is_active, is_superuser, created_at, updated_at)
                    VALUES (:full_name, :email, :hashed_password, :is_active, :is_superuser, NOW(), NOW())
                """),
                {
                    "full_name": "Administrador BIUAI",
                    "email": "admin@biuai.com", 
                    "hashed_password": hashed_password,
                    "is_active": True,
                    "is_superuser": True
                }
            )
            
            await session.commit()
            print("✅ Usuário admin criado com sucesso na tabela 'users'!")
            print("📧 Email: admin@biuai.com")
            print("🔒 Senha: admin123")
            print("👤 Tabela: users (atual)")
            print("🔧 Endpoint: POST /api/v1/auth/login")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Erro ao criar usuário admin: {e}")
            print("💡 Dica: Verifique se o banco está acessível e a tabela 'users' existe")
        
    await engine.dispose()

async def verify_tables():
    """Verificar quais tabelas de usuários existem"""
    POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "db")
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "biuai")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "biuai123")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "biuai")
    database_url = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:5432/{POSTGRES_DB}"
    engine = create_async_engine(database_url, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Verificar tabela users (atual)
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            print(f"📊 Tabela 'users' (atual): {users_count} usuários")
            
            # Verificar tabela usuarios (antiga)
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM usuarios"))
                usuarios_count = result.scalar()
                print(f"📊 Tabela 'usuarios' (antiga): {usuarios_count} usuários")
            except:
                print("📊 Tabela 'usuarios' (antiga): não existe")
                
        except Exception as e:
            print(f"❌ Erro ao verificar tabelas: {e}")
    
    await engine.dispose()

if __name__ == "__main__":
    print("🚀 BIUAI - Criador de Usuário Admin")
    print("=" * 50)
    
    # Verificar estado das tabelas
    print("🔍 Verificando tabelas de usuários...")
    asyncio.run(verify_tables())
    
    print("\n🔄 Criando usuário admin...")
    asyncio.run(create_admin_user())
    
    print("\n" + "=" * 50)
    print("✨ Processo concluído!") 