# Sistema Financeiro - Frontend

Este é o frontend do Sistema Financeiro, desenvolvido com Vue 3, Quasar Framework e Vite.

## Requisitos

- Node.js >= 16
- npm >= 8

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
npm install
```

## Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
npm run dev
```

O servidor será iniciado em `http://localhost:8080`.

## Build

Para gerar a build de produção:

```bash
npm run build
```

Os arquivos serão gerados na pasta `dist`.

## Linting

Para executar o linting:

```bash
npm run lint
```

## Formatação

Para formatar o código:

```bash
npm run format
```

## Estrutura do Projeto

```
src/
  ├── assets/        # Arquivos estáticos
  ├── boot/          # Configurações de plugins
  ├── components/    # Componentes Vue
  ├── css/          # Estilos globais
  ├── layouts/      # Layouts da aplicação
  ├── pages/        # Páginas da aplicação
  ├── router/       # Configuração de rotas
  ├── services/     # Serviços de API
  ├── stores/       # Stores Pinia
  ├── App.vue       # Componente raiz
  └── main.js       # Ponto de entrada
```

## Funcionalidades

- Autenticação de usuários
- Dashboard com resumo financeiro
- Gerenciamento de lançamentos (receitas e despesas)
- Interface responsiva
- Notificações de ações
- Proteção de rotas
- Gerenciamento de estado com Pinia
- Integração com API REST 