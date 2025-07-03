# Credenciais dos Serviços

## Banco de Dados (PostgreSQL)
- **Host**: localhost:5432
- **Banco**: financeiro
- **Usuário**: admin
- **Senha**: secret

## pgAdmin (Interface Web PostgreSQL)
- **URL**: http://localhost:5050
- **Email**: admin@biuai.com
- **Senha**: biuai123

## Redis
- **Host**: localhost:6379
- Não requer autenticação no ambiente de desenvolvimento

## Jupyter Lab
- **URL**: http://localhost:8888
- **Nota**: A autenticação por token está desabilitada na configuração atual
- Para habilitar a autenticação por token, edite o arquivo de configuração do Jupyter

## Backend (FastAPI)
- **URL API**: http://localhost:3000
- **Documentação**: http://localhost:3000/docs
- **JWT Secret**: your-secret-key (usado para geração de tokens)

## Model Server (ML)
- **URL API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- Não requer autenticação direta (comunica-se através do backend)

## Frontend
- **URL**: http://localhost:8080
- A autenticação é feita através do backend

## Notas de Segurança
1. Estas são credenciais para ambiente de desenvolvimento
2. Para produção, todas as senhas devem ser alteradas
3. Recomenda-se usar variáveis de ambiente para as credenciais em produção
4. O JWT_SECRET deve ser alterado em produção
5. Em produção, habilite a autenticação do Jupyter Lab

## Como Obter Token de Acesso Jupyter
Para obter o token de acesso do Jupyter Lab, execute:
```bash
docker-compose logs jupyter | grep token
``` 