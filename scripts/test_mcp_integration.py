#!/usr/bin/env python3
"""
Script de teste para verificar a integração MCP Memory
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

# Configurações
BACKEND_BASE_URL = "http://localhost:3000/api/v1"
MCP_SERVICE_URL = "http://localhost:8001"

# Credenciais de teste (usuário demo)
TEST_USER = {
    "email": "demo@biuai.com",
    "password": "demo123"
}

async def test_mcp_direct():
    """Testar conexão direta com o serviço MCP"""
    print("🔧 Testando conexão direta com o serviço MCP...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVICE_URL}/health")
            if response.status_code == 200:
                print("✅ Serviço MCP Memory está healthy")
                print(f"   Resposta: {response.json()}")
                return True
            else:
                print(f"❌ Erro no health check: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Erro de conexão com MCP: {e}")
        return False

async def authenticate():
    """Autenticar no backend e obter token JWT"""
    print("🔐 Autenticando no backend...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_BASE_URL}/auth/login",
                data={
                    "username": TEST_USER["email"],
                    "password": TEST_USER["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print("✅ Autenticação bem-sucedida")
                return token_data["access_token"]
            else:
                print(f"❌ Erro na autenticação: {response.status_code}")
                print(f"   Resposta: {response.text}")
                return None
    except Exception as e:
        print(f"❌ Erro de autenticação: {e}")
        return None

async def test_memoria_endpoints(token):
    """Testar endpoints de memória via backend"""
    print("🧠 Testando endpoints de memória...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Testar health check da memória
            print("   → Testando health check...")
            response = await client.get(
                f"{BACKEND_BASE_URL}/memoria/health",
                headers=headers
            )
            
            if response.status_code == 200:
                print("   ✅ Health check da memória OK")
            else:
                print(f"   ❌ Erro no health check: {response.status_code}")
                return False
            
            # 2. Criar uma memória de teste
            print("   → Criando memória de teste...")
            memoria_data = {
                "content": f"Teste de integração MCP realizado em {datetime.now().isoformat()}",
                "user_id": "demo_user",
                "metadata": {
                    "categoria": "teste",
                    "contexto": "integracao_mcp",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = await client.post(
                f"{BACKEND_BASE_URL}/memoria/",
                json=memoria_data,
                headers=headers
            )
            
            if response.status_code == 200:
                memoria_criada = response.json()
                print("   ✅ Memória criada com sucesso")
                print(f"      ID: {memoria_criada.get('id', 'N/A')}")
                memory_id = memoria_criada.get('id')
            else:
                print(f"   ❌ Erro ao criar memória: {response.status_code}")
                print(f"      Resposta: {response.text}")
                return False
            
            # 3. Buscar memórias
            print("   → Buscando memórias...")
            response = await client.get(
                f"{BACKEND_BASE_URL}/memoria/search",
                params={"query": "teste", "user_id": "demo_user", "limit": 5},
                headers=headers
            )
            
            if response.status_code == 200:
                resultado_busca = response.json()
                print("   ✅ Busca de memórias realizada")
                print(f"      Total encontrado: {resultado_busca.get('total', 0)}")
            else:
                print(f"   ❌ Erro na busca: {response.status_code}")
            
            # 4. Listar memórias do usuário
            print("   → Listando memórias do usuário...")
            response = await client.get(
                f"{BACKEND_BASE_URL}/memoria/",
                params={"limit": 10},
                headers=headers
            )
            
            if response.status_code == 200:
                memorias_usuario = response.json()
                print("   ✅ Listagem de memórias realizada")
                print(f"      Total do usuário: {memorias_usuario.get('total', 0)}")
            else:
                print(f"   ❌ Erro na listagem: {response.status_code}")
            
            # 5. Atualizar memória (se foi criada)
            if memory_id:
                print("   → Atualizando memória...")
                update_data = {
                    "content": f"Memória atualizada em {datetime.now().isoformat()}",
                    "metadata": {
                        "categoria": "teste_atualizado",
                        "contexto": "integracao_mcp",
                        "atualizado_em": datetime.now().isoformat()
                    }
                }
                
                response = await client.put(
                    f"{BACKEND_BASE_URL}/memoria/{memory_id}",
                    json=update_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("   ✅ Memória atualizada com sucesso")
                else:
                    print(f"   ❌ Erro ao atualizar: {response.status_code}")
                
                # 6. Deletar memória de teste
                print("   → Deletando memória de teste...")
                response = await client.delete(
                    f"{BACKEND_BASE_URL}/memoria/{memory_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("   ✅ Memória deletada com sucesso")
                else:
                    print(f"   ❌ Erro ao deletar: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro nos testes de memória: {e}")
        return False

async def main():
    """Função principal do teste"""
    print("🚀 Iniciando testes de integração MCP Memory")
    print("=" * 50)
    
    # 1. Testar serviço MCP diretamente
    mcp_ok = await test_mcp_direct()
    if not mcp_ok:
        print("❌ Falha no teste direto do MCP. Parando testes.")
        return False
    
    print()
    
    # 2. Autenticar no backend
    token = await authenticate()
    if not token:
        print("❌ Falha na autenticação. Parando testes.")
        return False
    
    print()
    
    # 3. Testar endpoints de memória
    memoria_ok = await test_memoria_endpoints(token)
    if not memoria_ok:
        print("❌ Falha nos testes de memória.")
        return False
    
    print()
    print("🎉 Todos os testes de integração MCP Memory foram bem-sucedidos!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 