# BIUAI - Sistema Financeiro Inteligente

Sistema financeiro completo com BI, Machine Learning e Inteligência Artificial.

## Arquitetura

O BIUAI é um sistema SaaS (Software as a Service) modular com suporte a multi-tenancy.

### Multi-tenancy

O sistema suporta múltiplos tenants (empresas/organizações) com:

- Isolamento completo de dados
- Configurações personalizadas
- Domínios customizados
- Features por tenant
- Limites e quotas

### Sistema de Módulos

Módulos disponíveis:

- **CORE** (Gratuito)
  - Autenticação
  - Dashboard básico
  - Gestão de usuários
  
- **FINANCIAL** (Gratuito)
  - Gestão financeira
  - Categorias
  - Relatórios básicos
  
- **INVESTMENTS** (Pago)
  - Análise de investimentos
  - Carteira de FIIs
  - Simulações
  
- **AI_INSIGHTS** (Pago)
  - Análises com IA
  - Detecção de padrões
  - Previsões
  
- **CHATBOT** (Pago)
  - Assistente virtual
  - Consultas em linguagem natural
  - Suporte 24/7
  
- **ANALYTICS** (Pago)
  - Relatórios avançados
  - BI customizado
  - Exportação de dados

### Hierarquia de Usuários

- **SUPER_ADMIN**: Administrador master do sistema
- **TENANT_ADMIN**: Administrador do tenant
- **SUB_ADMIN**: Administrador delegado
- **USER**: Usuário final

## Características Principais

- **Multi-tenancy**: Isolamento completo de dados por empresa
- **Modular**: Módulos independentes e plugáveis
- **Inteligente**: IA e ML integrados em todo sistema
- **Seguro**: RBAC granular e auditoria completa
- **Escalável**: Arquitetura distribuída e containerizada
- **Customizável**: Configurações por tenant e módulo

## Tecnologias

### Backend
- FastAPI (API REST)
- PostgreSQL (Banco de dados)
- Redis (Cache)
- Celery (Tarefas assíncronas)
- Alembic (Migrações)

### Frontend
- Vue.js 3 (Framework)
- Quasar (UI Framework)
- Pinia (Gerenciamento de estado)
- Chart.js (Gráficos)
- TailwindCSS (Estilização)

### Machine Learning
- TensorFlow
- scikit-learn
- pandas
- numpy
- Jupyter

### DevOps
- Docker
- Docker Compose
- GitHub Actions
- Prometheus
- Grafana

## Instalação

### Pré-requisitos

- Docker e Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/biuai.git
cd biuai
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

3. Inicie os containers:
```bash
docker-compose up -d
```

4. Execute as migrações:
```bash
docker-compose exec backend alembic upgrade head
```

5. Crie o primeiro tenant:
```bash
curl -X POST http://localhost:8000/api/v1/tenants/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minha Empresa",
    "slug": "minhaempresa",
    "admin_email": "admin@minhaempresa.com",
    "admin_password": "senha123"
  }'
```

## Desenvolvimento

### Estrutura de Diretórios

```
biuai/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints
│   │   │   ├── core/     # Configurações
│   │   │   ├── models/   # Modelos SQLAlchemy
│   │   │   ├── schemas/  # Schemas Pydantic
│   │   │   └── services/ # Regras de negócio
│   │   └── tests/        # Testes
│   └── frontend/         # Frontend Vue.js
│       ├── src/
│       │   ├── components/
│       │   ├── composables/
│       │   ├── pages/
│       │   └── stores/
│       └── tests/
├── ml_service/       # Serviço de ML
├── etl_service/      # Serviço de ETL
├── jupyter/          # Notebooks
└── modules/         # Módulos
    ├── financial/
    ├── investments/
    ├── ai_insights/
    └── analytics/
```

### Comandos Úteis

```bash
# Criar novo módulo
python scripts/create_module.py nome_modulo

# Gerar migrations
docker-compose exec backend alembic revision --autogenerate -m "descricao"

# Executar testes
docker-compose exec backend pytest
docker-compose exec frontend npm run test

# Lint e formatação
docker-compose exec backend black .
docker-compose exec frontend npm run lint

# Build para produção
docker-compose -f docker-compose.prod.yml build
```

## APIs

### Tenant Management

- `POST /api/v1/tenants/register` - Registra novo tenant
- `GET /api/v1/tenants/me` - Obtém tenant atual
- `PUT /api/v1/tenants/me` - Atualiza tenant atual
- `POST /api/v1/tenants/me/modules/{module}` - Ativa/desativa módulo

### Módulos

- `GET /api/v1/modules` - Lista módulos disponíveis
- `GET /api/v1/modules/{module}` - Detalhes do módulo
- `POST /api/v1/modules/{module}/trial` - Inicia trial

### Usuários

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/users/me` - Usuário atual
- `PUT /api/v1/users/me` - Atualiza usuário

## Documentação

- [Documentação Completa](https://docs.biuai.com)
- [API Reference](https://api.biuai.com/docs)
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [Changelog](CHANGELOG.md)

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nome`)
3. Commit suas mudanças (`git commit -am 'Adiciona feature'`)
4. Push para a branch (`git push origin feature/nome`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
