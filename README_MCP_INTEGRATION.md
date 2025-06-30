# Integração MCP Memory - BIUAI

## Visão Geral

Este documento descreve a integração do sistema BIUAI com o servidor MCP (Model Context Protocol) de memória da Mem0 AI. Esta integração permite que o sistema mantenha memórias contextuais sobre usuários e suas preferências financeiras.

## Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Frontend      │    │   Backend        │    │   MCP Memory        │
│   (Vue.js)      │◄──►│   (FastAPI)      │◄──►│   Service           │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                                                           │
                                                           ▼
                                                ┌─────────────────────┐
                                                │   Mem0 AI Server    │
                                                │   (External API)    │
                                                └─────────────────────┘
```

## Componentes

### 1. MCP Memory Service
- **Localização**: `./mcp-memory-service/`
- **Porta**: 8001
- **Função**: Proxy/adaptador entre o backend BIUAI e o servidor Mem0 AI

### 2. Backend Integration
- **Schemas**: `backend/app/schemas/memoria.py`
- **Services**: `backend/app/services/memoria_service.py`
- **Routes**: `backend/app/routes/memoria.py`

## Funcionalidades

### Endpoints Disponíveis

#### 1. Criar Memória
```http
POST /api/v1/memoria/
```
**Payload:**
```json
{
  "content": "Usuário preferiu investimentos de baixo risco",
  "user_id": "user123",
  "metadata": {
    "categoria": "preferencias",
    "contexto": "dashboard_financeiro"
  }
}
```

#### 2. Buscar Memórias
```http
GET /api/v1/memoria/search?query=investimentos&user_id=user123&limit=10
```

#### 3. Obter Memórias do Usuário
```http
GET /api/v1/memoria/{user_id}?limit=100
```

#### 4. Atualizar Memória
```http
PUT /api/v1/memoria/{memory_id}
```

#### 5. Deletar Memória
```http
DELETE /api/v1/memoria/{memory_id}
```

#### 6. Health Check
```http
GET /api/v1/memoria/health
```

## Configuração

### Variáveis de Ambiente

#### Docker Compose
```yaml
mcp-memory-server:
  environment:
    - MEM0_API_KEY=a4ed31ec-0cee-4385-b796-4dd33ef1ffb9
    - MEM0_PROFILE=resident-coral-8A1GGg
    - MEM0_SERVER_URL=https://server.smithery.ai/@mem0ai/mem0-memory-mcp/mcp
```

#### Backend
```yaml
backend:
  environment:
    - MCP_MEMORY_SERVICE_URL=http://mcp-memory-server:8001
```

### Configurações do Backend
No arquivo `backend/app/core/config.py`:
```python
MCP_MEMORY_SERVICE_URL: str = "http://mcp-memory-server:8001"
MCP_MEMORY_SERVICE_TIMEOUT: int = 30
```

## Casos de Uso

### 1. Preferências do Usuário
```python
# Armazenar preferência de investimento
await memoria_service.criar_memoria(
    content="Usuário tem perfil conservador, prefere investimentos de baixo risco",
    user_id="user123",
    metadata={"categoria": "perfil_investimento", "contexto": "onboarding"}
)
```

### 2. Histórico de Decisões
```python
# Armazenar decisão financeira
await memoria_service.criar_memoria(
    content="Usuário cancelou cartão de crédito devido a altas taxas",
    user_id="user123",
    metadata={"categoria": "decisao_financeira", "produto": "cartao_credito"}
)
```

### 3. Contextualização IA
```python
# Buscar contexto para recomendações
memorias = await memoria_service.buscar_memorias(
    query="investimentos",
    user_id="user123",
    limit=5
)
```

## Segurança

### Autenticação
- Todas as rotas requerem autenticação JWT
- Verificação de permissões por usuário
- Usuários só podem acessar suas próprias memórias (exceto admins)

### Validação de Dados
- Schemas Pydantic para validação de entrada
- Sanitização de conteúdo
- Limites de tamanho e quantidade

### Error Handling
- Tratamento robusto de erros de rede
- Timeouts configuráveis
- Logs detalhados de auditoria

## Monitoramento

### Health Checks
```bash
# Verificar saúde do serviço MCP
curl http://localhost:8001/health

# Verificar saúde via backend
curl http://localhost:3000/api/v1/memoria/health
```

### Logs
- Logs estruturados com contexto
- Auditoria de operações CRUD
- Métricas de performance

## Desenvolvimento

### Executar Localmente
```bash
# Subir todos os serviços
docker-compose up -d

# Verificar logs do serviço MCP
docker-compose logs -f mcp-memory-server

# Testar endpoints
curl http://localhost:3000/api/v1/memoria/health
```

### Testes
```bash
# Executar testes do backend
cd backend
pytest tests/test_memoria.py -v

# Testar integração
pytest tests/integration/test_mcp_integration.py -v
```

## Roadmap

### Próximas Funcionalidades
1. **Cache Local**: Implementar cache Redis para memórias frequentemente acessadas
2. **Batch Operations**: Operações em lote para melhor performance
3. **Embeddings**: Busca semântica usando embeddings
4. **Analytics**: Métricas e insights sobre uso de memórias
5. **Backup**: Sistema de backup e recuperação de memórias

### Melhorias de Performance
1. **Connection Pooling**: Pool de conexões HTTP reutilizáveis
2. **Async Processing**: Processamento assíncrono para operações pesadas
3. **Rate Limiting**: Controle de taxa específico para MCP
4. **Compression**: Compressão de payloads grandes

## Troubleshooting

### Problemas Comuns

#### Serviço MCP Indisponível
```bash
# Verificar status do container
docker-compose ps mcp-memory-server

# Restart do serviço
docker-compose restart mcp-memory-server
```

#### Problemas de Conectividade
```bash
# Testar conectividade direta
curl http://mcp-memory-server:8001/health

# Verificar logs de rede
docker-compose logs backend | grep -i mcp
```

#### Timeout de Requisições
- Aumentar `MCP_MEMORY_SERVICE_TIMEOUT` no backend
- Verificar latência da rede
- Monitorar recursos do container MCP

## Conclusão

A integração MCP Memory adiciona capacidades avançadas de memória contextual ao sistema BIUAI, permitindo experiências mais personalizadas e inteligentes para os usuários. A arquitetura modular facilita manutenção e extensão das funcionalidades.

Para mais informações, consulte:
- [Documentação Mem0 AI](https://docs.mem0.ai/)
- [Especificação MCP](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) 