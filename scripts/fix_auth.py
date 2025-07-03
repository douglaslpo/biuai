#!/usr/bin/env python3
"""
Script para corrigir credenciais de autenticação do BIUAI
Atualiza senhas e cria usuários de teste necessários
"""

import os
import sys
import psycopg2
from passlib.context import CryptContext
from datetime import datetime

# Configuração de criptografia (mesmo padrão usado no backend)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    return pwd_context.hash(password)

def create_connection():
    """Cria conexão com o banco PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="biuai",
            user="biuai",
            password="biuai123"
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco: {e}")
        return None

def update_user_password(conn, email: str, password: str, description: str):
    """Atualiza a senha de um usuário"""
    try:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        
        cursor.execute(
            "UPDATE users SET hashed_password = %s, updated_at = %s WHERE email = %s",
            (hashed_password, datetime.now(), email)
        )
        
        if cursor.rowcount > 0:
            print(f"✅ {description}: senha atualizada")
        else:
            print(f"⚠️  {description}: usuário não encontrado")
        
        conn.commit()
        cursor.close()
        
    except Exception as e:
        print(f"❌ Erro ao atualizar {description}: {e}")

def create_demo_user(conn):
    """Cria usuário demo se não existir"""
    try:
        cursor = conn.cursor()
        
        # Verificar se usuário demo existe
        cursor.execute("SELECT id FROM users WHERE email = %s", ('demo@biuai.com',))
        if cursor.fetchone():
            print("ℹ️  Usuário demo já existe")
            cursor.close()
            return
        
        # Criar usuário demo
        hashed_password = hash_password('demo123')
        cursor.execute("""
            INSERT INTO users (full_name, email, hashed_password, is_active, is_superuser, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            'Usuário Demo',
            'demo@biuai.com', 
            hashed_password,
            True,
            False,
            datetime.now(),
            datetime.now()
        ))
        
        print("✅ Usuário demo criado com sucesso")
        conn.commit()
        cursor.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário demo: {e}")

def show_credentials():
    """Mostra as credenciais atualizadas"""
    print("\n" + "="*60)
    print("🔑 CREDENCIAIS DE ACESSO ATUALIZADAS")
    print("="*60)
    print("📧 ADMINISTRADOR:")
    print("   Email: admin@biuai.com")
    print("   Senha: admin123")
    print("")
    print("🧪 USUÁRIO DEMO (Botão 'Testar Sistema'):")
    print("   Email: demo@biuai.com")
    print("   Senha: demo123")
    print("")
    print("🌐 Acesso: http://localhost:8080/login")
    print("="*60)

def main():
    print("🔧 Iniciando correção de credenciais BIUAI...")
    print("📍 Conectando ao banco de dados...")
    
    conn = create_connection()
    if not conn:
        sys.exit(1)
    
    try:
        # Atualizar senha do admin para uma senha mais óbvia
        print("\n🔄 Atualizando credenciais...")
        update_user_password(conn, 'admin@biuai.com', 'admin123', 'Administrador')
        
        # Criar usuário demo
        create_demo_user(conn)
        
        # Mostrar credenciais finais
        show_credentials()
        
        print("\n✅ Correção concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 