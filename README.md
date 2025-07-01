# 🏦 BIUAI - Business Intelligence Unity with AI

Sistema completo de gestão financeira pessoal e empresarial com inteligência artificial integrada.

![BIUAI Logo](public/images/biuai-logo.svg)

## 🌟 Características Principais

### 💰 Gestão Financeira Completa
- **Dashboard Interativo**: Métricas em tempo real com gráficos modernos
- **Lançamentos**: Controle total de receitas e despesas
- **Categorização Inteligente**: IA para classificação automática
- **Relatórios Avançados**: Analytics e insights financeiros
- **Metas e Objetivos**: Acompanhamento de metas financeiras

### 🤖 Inteligência Artificial
- **Chatbot MCP**: Assistente especializado "Bi UAI Bot Administrador"
- **Base de Conhecimento**: Especializada no sistema BIUAI
- **Suporte 24/7**: Ajuda contextual e inteligente
- **Análise Preditiva**: Insights baseados em machine learning

### 🏗️ Arquitetura Moderna
- **Microserviços**: Arquitetura escalável e modular
- **Containerização**: Docker Compose para deploy simplificado
- **APIs RESTful**: FastAPI com documentação automática
- **Frontend Reativo**: Vue.js 3 + Vuetify 3
- **Cache Inteligente**: Redis para performance otimizada

## 🚀 Tecnologias

### Backend
- **Python 3.11+** - Linguagem principal
- **FastAPI** - Framework web moderno e performático
- **PostgreSQL** - Banco de dados robusto
- **Redis** - Cache e sessões
- **SQLAlchemy** - ORM avançado com async/await
- **Pydantic** - Validação de dados

### Frontend
- **Vue.js 3** - Framework JavaScript reativo
- **Vuetify 3** - Material Design para Vue
- **Vite** - Build tool moderno
- **Chart.js** - Gráficos interativos
- **Axios** - Cliente HTTP

### Inteligência Artificial
- **Ollama** - Modelos de IA locais gratuitos
- **MCP (Model Context Protocol)** - Comunicação com IA
- **llama3.2:3b** - Modelo de linguagem principal
- **Scikit-learn** - Machine Learning
- **NLTK** - Processamento de linguagem natural

### DevOps & Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Nginx** - Proxy reverso e servir arquivos estáticos
- **Jupyter Lab** - Análise de dados
- **PgAdmin** - Administração do banco

## 📦 Instalação Rápida

### Pré-requisitos
- Docker & Docker Compose
- 4GB+ RAM (recomendado 8GB)
- 10GB+ espaço livre em disco

### 1. Clone o Repositório
```bash
git clone https://github.com/douglaslpo/biuai.git
cd biuai
```

### 2. Inicie o Sistema
```bash
# Dar permissão aos scripts
chmod +x scripts/*.sh

# Iniciar todos os serviços
./scripts/start.sh
```

### 3. Acesse a Interface
- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:3000/docs
- **PgAdmin**: http://localhost:5050

## 🔧 Configuração

### Credenciais Padrão

**Aplicação:**
- Admin: `admin@biuai.com` / `admin123`
- Demo: `demo@biuai.com` / `demo123`

**PgAdmin:**
- Email: `admin@biuai.com`
- Senha: `biuai123`

**Banco de Dados:**
- Host: `localhost:5432`
- Database: `biuai`
- User: `biuai`
- Password: `biuai123`

## 📊 Serviços e Portas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Frontend | 8080 | Interface principal |
| Backend API | 3000 | API REST |
| PostgreSQL | 5432 | Banco de dados |
| Redis | 6379 | Cache e sessões |
| Ollama | 11434 | IA Local |
| MCP Chatbot | 8002 | Serviço do chatbot |
| MCP Memory | 8001 | Serviço de memória |
| Model Server | 8000 | Servidor ML |
| Jupyter Lab | 8888 | Análise de dados |
| PgAdmin | 5050 | Admin do banco |

## 🤖 Chatbot "Bi UAI Bot Administrador"

### Funcionalidades
- **Chat em Tempo Real**: WebSocket para comunicação instantânea
- **Base de Conhecimento**: Especializada em funcionalidades BIUAI
- **Sugestões Inteligentes**: Recomendações contextuais
- **Sistema de Feedback**: Avaliação e melhoria contínua
- **Interface Moderna**: Modal flutuante responsivo

### Como Usar
1. Acesse o dashboard principal
2. Clique no ícone do robô (canto inferior direito)
3. Digite suas dúvidas em português natural
4. Use as sugestões rápidas para ações comuns

## 📈 Analytics e Monitoramento

### Dashboard Administrativo
- Acesse: `/admin/chatbot`
- Métricas de uso em tempo real
- Configuração de personalidade
- Gerenciamento da base de conhecimento

### Logs e Debug
```bash
# Ver logs de um serviço
docker-compose logs backend

# Ver todos os logs
docker-compose logs

# Logs em tempo real
docker-compose logs -f backend
```

## 🔧 Comandos Úteis

### Gerenciamento do Sistema
```bash
# Iniciar sistema
./scripts/start.sh

# Parar sistema
./scripts/stop.sh

# Reiniciar
./scripts/stop.sh && ./scripts/start.sh

# Ver status
docker-compose ps
```

### Desenvolvimento
```bash
# Rebuild de um serviço
docker-compose up --build backend

# Executar no modo dev
docker-compose -f docker-compose.dev.yml up

# Acessar container
docker-compose exec backend bash
```

### Banco de Dados
```bash
# Importar dados SIOG
python scripts/import_siog_data.py

# Criar usuário admin
python scripts/create_admin_user.py

# Backup do banco
docker-compose exec db pg_dump -U biuai biuai > backup.sql
```

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │
│   Vue.js 3      │◄──►│   FastAPI       │
│   Vuetify 3     │    │   Python 3.11   │
│   Port: 8080    │    │   Port: 3000    │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis Cache   │
│   Port: 5432    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   MCP Services  │    │   ML Services   │
│   Chatbot: 8002 │    │   Model: 8000   │
│   Memory: 8001  │    │   Jupyter: 8888 │
└─────────────────┘    └─────────────────┘
```

## 📚 Documentação

- **API**: `/docs` - Documentação interativa da API
- **Swagger**: `/redoc` - Documentação alternativa
- **Arquitetura**: `/docs/architecture` - Diagramas e fluxos
- **Deploy**: `/docs/deploy` - Guias de instalação

## 🧪 Testes

```bash
# Executar testes
docker-compose exec backend pytest

# Testes com coverage
docker-compose exec backend pytest --cov=app

# Testes específicos
docker-compose exec backend pytest tests/test_api.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

- **GitHub Issues**: Para bugs e melhorias
- **Discussions**: Para perguntas e ideias
- **Wiki**: Documentação adicional
- **Chatbot**: Suporte integrado no sistema

---

<div align="center">

**BIUAI** - Transformando a gestão financeira com inteligência artificial

[![GitHub stars](https://img.shields.io/github/stars/douglaslpo/biuai.svg)](https://github.com/douglaslpo/biuai/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/douglaslpo/biuai.svg)](https://github.com/douglaslpo/biuai/network)
[![GitHub issues](https://img.shields.io/github/issues/douglaslpo/biuai.svg)](https://github.com/douglaslpo/biuai/issues)

</div>
