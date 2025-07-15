# 📊 Módulo MyFIIs - BIUAI

## Visão Geral
Módulo de análise e gestão de Fundos de Investimento Imobiliário (FIIs) integrado ao BIUAI.

## Funcionalidades
- 📈 Dashboard de FIIs com análise técnica
- 🤖 IA para análise e recomendações
- 📊 Comparativo entre FIIs
- 📱 Interface responsiva integrada
- 🔒 Controle de acesso granular

## Estrutura
```bash
modules/myfiis/
├── backend/               # API FastAPI
│   ├── routes/           # Endpoints REST
│   ├── models/           # Modelos SQLAlchemy
│   ├── schemas/          # Schemas Pydantic
│   └── services/         # Lógica de negócio
├── frontend/             # Vue.js Components
│   ├── components/       # Componentes Vue
│   ├── composables/      # Hooks reutilizáveis
│   ├── pages/           # Páginas do módulo
│   └── store/           # Estado Pinia
├── ai/                   # Serviços de IA
│   ├── embeddings/       # Vetorização de dados
│   ├── rag/             # Retrieval Augmented Generation
│   └── models/          # Modelos treinados
└── config/              # Configurações
    ├── permissions.json  # Controle de acesso
    └── settings.json    # Configurações gerais
```

## Tecnologias
- **Backend**: FastAPI + SQLAlchemy + Redis
- **Frontend**: Vue.js 3 + Vuetify + Pinia
- **IA**: sentence-transformers + LangChain
- **Dados**: PostgreSQL + Redis Cache

## Instalação
1. Habilite o módulo no painel admin
2. Configure permissões de acesso
3. Importe dados iniciais de FIIs

## Uso
```python
# Backend
from modules.myfiis.backend.services import FIIService
fiis = await FIIService.get_recommended_fiis(user_id)

# Frontend
import { useFIIs } from '@/modules/myfiis/composables'
const { fiis, loading } = useFIIs()
```

## Segurança
- Autenticação via JWT
- Rate limiting por usuário
- Validação de permissões
- Auditoria de ações

## Métricas
- Uso da IA por usuário
- Performance das recomendações
- Tempo de resposta da API
- Satisfação do usuário

## Documentação
- [API Reference](./backend/README.md)
- [Frontend Guide](./frontend/README.md)
- [AI Models](./ai/README.md) 