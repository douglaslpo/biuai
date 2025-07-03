# 🚀 GUIA DE DESENVOLVIMENTO BIUAI - MCPs & Boas Práticas

## 📋 Índice
1. [MCPs Disponíveis](#mcps-disponíveis)
2. [Estrutura do Projeto](#estrutura-do-projeto)
3. [Fluxo de Desenvolvimento](#fluxo-de-desenvolvimento)
4. [Padrões de Código](#padrões-de-código)
5. [Debugging e Troubleshooting](#debugging-e-troubleshooting)
6. [Deploy e Monitoramento](#deploy-e-monitoramento)

---

## 🔧 MCPs Disponíveis

### 1. **Deepwiki-MCP** - Documentação de Repositórios
```bash
# Comandos úteis:
mcp_Deepwiki-MCP_read_wiki_structure repoName="org/repo"
mcp_Deepwiki-MCP_read_wiki_contents repoName="org/repo"  
mcp_Deepwiki-MCP_ask_question repoName="org/repo" question="Como implementar X?"
```

**Uso Recomendado:**
- Consultar documentação de bibliotecas/frameworks antes de implementar
- Verificar best practices de projetos similares
- Entender padrões arquiteturais estabelecidos

### 2. **Supabase-MCP** - Gerenciamento de Banco de Dados
```bash
# Comandos essenciais:
mcp_Supabase-MCP_list_tables schemas=["public"]
mcp_Supabase-MCP_execute_sql query="SELECT * FROM users LIMIT 10"
mcp_Supabase-MCP_apply_migration name="add_new_feature" query="ALTER TABLE..."
mcp_Supabase-MCP_get_advisors type="security"
```

**Uso Recomendado:**
- ✅ Sempre verificar advisories de segurança antes de deploy
- ✅ Usar migrations para mudanças estruturais do banco
- ✅ Testar queries em ambiente de desenvolvimento primeiro
- ❌ NUNCA executar DDL diretamente em produção sem migration

### 3. **Figma-MCP** - Design e Prototipagem
```bash
# Comandos principais:
mcp_Figma-MCP_get_figma_data fileKey="abc123" nodeId="1:234"
mcp_Figma-MCP_download_figma_images fileKey="abc123" localPath="/path/to/assets"
```

**Uso Recomendado:**
- Manter assets de design sincronizados com Figma
- Automatizar download de ícones e imagens
- Verificar especificações de design antes de implementar

### 4. **Agentql-MCP** - Extração de Dados Web
```bash
mcp_Agentql-MCP_extract-web-data url="https://site.com" prompt="Extract pricing data"
```

**Uso Recomendado:**
- Pesquisa de mercado automatizada
- Monitoramento de competidores
- Coleta de dados para análises

### 5. **Sequential Thinking MCP** - Solução de Problemas
```bash
mcp_server-sequential-thinking_sequentialthinking thought="Analisar problema X" nextThoughtNeeded=true
```

**Uso Recomendado:**
- Quebrar problemas complexos em etapas
- Documentar processo de tomada de decisão
- Revisar e iterar soluções

---

## 🏗️ Estrutura do Projeto

### Backend (FastAPI)
```
backend/
├── app/
│   ├── api/v1/           # Endpoints da API v1
│   ├── core/             # Configurações centrais
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   ├── services/         # Lógica de negócio
│   └── middleware.py     # Middlewares customizados
├── data/                 # Dados e migrations
└── requirements.txt      # Dependências Python
```

### Frontend (Vue.js 3 + Quasar)
```
frontend/
├── src/
│   ├── components/       # Componentes reutilizáveis
│   │   ├── base/         # Componentes base (PageHeader, MetricCard)
│   │   ├── forms/        # Formulários especializados
│   │   └── modals/       # Modais de interação
│   ├── composables/      # Lógica reutilizável
│   ├── pages/            # Páginas da aplicação
│   ├── services/         # Comunicação com API
│   └── stores/           # Gerenciamento de estado (Pinia)
```

---

## 🔄 Fluxo de Desenvolvimento

### 1. **Planejamento e Research**
```bash
# 1. Consultar documentação relevante
mcp_Deepwiki-MCP_ask_question repoName="vuejs/core" question="Como implementar reactive refs?"

# 2. Verificar exemplos de implementação
mcp_Agentql-MCP_extract-web-data url="https://examples.com" prompt="Vue 3 best practices"

# 3. Usar sequential thinking para quebrar o problema
mcp_server-sequential-thinking_sequentialthinking thought="Definir arquitetura do componente"
```

### 2. **Implementação Backend**
```bash
# 1. Verificar estado atual do banco
mcp_Supabase-MCP_list_tables

# 2. Criar migration se necessário
mcp_Supabase-MCP_apply_migration name="add_feature_x" query="CREATE TABLE..."

# 3. Verificar advisories de segurança
mcp_Supabase-MCP_get_advisors type="security"
```

### 3. **Implementação Frontend**
```bash
# 1. Baixar assets do Figma se necessário
mcp_Figma-MCP_download_figma_images fileKey="design123" localPath="./src/assets"

# 2. Implementar componentes seguindo padrões estabelecidos
# 3. Usar composables existentes (usePageData, useNotifications, etc.)
```

### 4. **Testing e Debugging**
```bash
# 1. Testar endpoints da API
curl -X POST "http://localhost:3000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@biuai.com&password=admin123"

# 2. Verificar logs estruturados
docker-compose logs backend | grep ERROR

# 3. Monitorar métricas
curl "http://localhost:3000/metrics"
```

---

## 💻 Padrões de Código

### Backend - FastAPI

#### ✅ **Estrutura de Endpoint Padrão**
```python
@router.post("/items", response_model=ItemResponse)
async def create_item(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    item_in: ItemCreate,
) -> Any:
    """
    Criar novo item
    """
    # Validações
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    # Lógica de negócio
    item = await ItemService.create(db, item_in, user_id=current_user.id)
    
    # Auditoria
    await SecurityAudit.log_action("item_created", current_user.id, {"item_id": item.id})
    
    return ItemResponse.from_orm(item)
```

#### ✅ **Middleware Personalizado**
```python
class CustomMiddleware(BaseHTTPMiddleware):
    """Middleware seguindo padrão estabelecido"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Lógica antes da requisição
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Lógica após a requisição
            duration = time.time() - start_time
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as error:
            # Log estruturado de erro
            logger.error("Middleware error", extra={"error": str(error)})
            raise
```

### Frontend - Vue.js 3

#### ✅ **Componente Base Padrão**
```vue
<template>
  <base-card :variant="variant" :elevation="elevation">
    <page-header
      :title="title"
      :subtitle="subtitle"
      :breadcrumbs="breadcrumbs"
    >
      <template #actions>
        <slot name="actions" />
      </template>
      
      <template #metrics>
        <metric-card
          v-for="metric in metrics"
          :key="metric.key"
          v-bind="metric"
        />
      </template>
    </page-header>
    
    <div class="q-pa-md">
      <slot />
    </div>
  </base-card>
</template>

<script setup>
import { computed } from 'vue'
import { useLoading, useNotifications } from '@/composables'
import BaseCard from '@/components/base/BaseCard.vue'
import PageHeader from '@/components/base/PageHeader.vue'
import MetricCard from '@/components/base/MetricCard.vue'

// Props com validação
const props = defineProps({
  title: { type: String, required: true },
  subtitle: String,
  variant: { type: String, default: 'outlined' },
  elevation: { type: Number, default: 1 }
})

// Composables
const { isLoading } = useLoading()
const { showSuccess } = useNotifications()

// Computed properties
const breadcrumbs = computed(() => [
  { label: 'Dashboard', to: '/dashboard' },
  { label: props.title }
])
</script>
```

#### ✅ **Composable Padrão**
```javascript
// useEntityManager.js
import { ref, computed } from 'vue'
import { useNotifications, useLoading } from '@/composables'

export function useEntityManager(service, entityName) {
  // Estado reativo
  const items = ref([])
  const selectedItem = ref(null)
  const filters = ref({})
  const pagination = ref({ page: 1, limit: 10, total: 0 })
  
  // Composables
  const { showSuccess, showError } = useNotifications()
  const { startLoading, stopLoading } = useLoading()
  
  // Métodos
  const fetchItems = async () => {
    try {
      startLoading(`${entityName}.list`)
      const response = await service.list(filters.value, pagination.value)
      items.value = response.data
      pagination.value.total = response.total
    } catch (error) {
      showError(`Erro ao carregar ${entityName}`, error.message)
    } finally {
      stopLoading(`${entityName}.list`)
    }
  }
  
  const createItem = async (data) => {
    try {
      startLoading(`${entityName}.create`)
      const newItem = await service.create(data)
      items.value.push(newItem)
      showSuccess(`${entityName} criado com sucesso!`)
      return newItem
    } catch (error) {
      showError(`Erro ao criar ${entityName}`, error.message)
      throw error
    } finally {
      stopLoading(`${entityName}.create`)
    }
  }
  
  // Computed properties
  const filteredItems = computed(() => {
    // Aplicar filtros locais se necessário
    return items.value
  })
  
  return {
    // Estado
    items: filteredItems,
    selectedItem,
    filters,
    pagination,
    
    // Métodos
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    
    // Computed
    hasItems: computed(() => items.value.length > 0),
    isEmpty: computed(() => items.value.length === 0)
  }
}
```

---

## 🐛 Debugging e Troubleshooting

### Problemas Comuns e Soluções

#### 1. **Erro de Middleware "Object is not iterable"**
```bash
# Verificar logs
docker-compose logs backend | grep -i error

# Solução: Verificar se middleware herda corretamente de BaseHTTPMiddleware
# Não usar constructor personalizado que conflite com FastAPI
```

#### 2. **Erro de Autenticação**
```bash
# Verificar tabelas de usuários
mcp_Supabase-MCP_execute_sql query="SELECT * FROM users LIMIT 5"

# Verificar endpoint correto
curl -X POST "http://localhost:3000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=email@example.com&password=password"
```

#### 3. **Build Errors Frontend**
```bash
# Verificar dependências
cd frontend && npm install

# Build de desenvolvimento
npm run dev

# Build de produção
npm run build
```

#### 4. **Inconsistências de Dados**
```bash
# Verificar advisories de segurança
mcp_Supabase-MCP_get_advisors type="security"

# Executar migrations pendentes
mcp_Supabase-MCP_list_migrations
```

### Checklist de Debugging

- [ ] Verificar logs estruturados
- [ ] Testar endpoints com curl
- [ ] Verificar estado do banco de dados
- [ ] Confirmar configurações de environment
- [ ] Verificar dependências atualizadas
- [ ] Testar em ambiente limpo (docker-compose down && up)

---

## 🚀 Deploy e Monitoramento

### Pre-Deploy Checklist

#### Backend
- [ ] Executar `mcp_Supabase-MCP_get_advisors type="security"`
- [ ] Verificar migrations aplicadas
- [ ] Testar todos os endpoints críticos
- [ ] Verificar logs estruturados funcionando
- [ ] Confirmar rate limiting ativo

#### Frontend
- [ ] Build de produção bem-sucedido
- [ ] Assets do Figma atualizados
- [ ] Componentes seguindo padrões estabelecidos
- [ ] Testes de integração passando

### Monitoramento Pós-Deploy

```bash
# Health check
curl "http://localhost:3000/health"

# Métricas de performance
curl "http://localhost:3000/metrics"

# Logs em tempo real
docker-compose logs -f backend

# Verificar advisories continuamente
mcp_Supabase-MCP_get_advisors type="performance"
```

---

## 📚 Recursos e Referências

### Documentação Essencial
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Vue.js 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Quasar Framework](https://quasar.dev/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### MCPs Externos Úteis
- **GitHub MCP**: Para integração com repositórios
- **Slack MCP**: Para notificações automatizadas
- **Docker MCP**: Para gerenciamento de containers

---

## ⚠️ Avisos Importantes

### 🔴 **NUNCA FAÇA**
- Não fazer DDL diretamente no banco sem migration
- Não commitar credenciais ou secrets
- Não ignorar advisories de segurança
- Não implementar sem consultar padrões existentes
- Não fazer deploy sem testar endpoints críticos

### ✅ **SEMPRE FAÇA**
- Use MCPs para consultar documentação
- Siga padrões estabelecidos nos composables
- Implemente logs estruturados
- Execute testes de integração
- Monitore métricas pós-deploy
- Documente decisões arquiteturais

---

## 🔄 Processo de Atualização

Este documento deve ser atualizado sempre que:
- Novos MCPs forem adicionados
- Padrões de código forem alterados
- Problemas recorrentes forem identificados
- Ferramentas ou frameworks forem atualizados

**Última atualização:** 02/07/2025  
**Versão:** 1.0  
**Próxima revisão:** 02/08/2025 