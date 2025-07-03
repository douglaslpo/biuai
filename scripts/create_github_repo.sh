#!/bin/bash

# Script para criar repositório no GitHub para o projeto BIUAI
# Execute após criar o repositório manualmente no GitHub

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] $1${NC}"
}

# Diretório do projeto
cd "$(dirname "$0")/.."

echo "🏦 BIUAI - Configuração do GitHub Repository"
echo "============================================"
echo ""

# Verificar se é um repositório git
if [ ! -d ".git" ]; then
    error "Este não é um repositório git. Execute 'git init' primeiro."
    exit 1
fi

# Solicitar URL do repositório
echo "📝 Por favor, siga os seguintes passos:"
echo ""
echo "1. Acesse https://github.com/new"
echo "2. Crie um novo repositório com o nome: BIUAI"
echo "3. Deixe como público ou privado conforme sua preferência"
echo "4. NÃO adicione README, .gitignore ou license (já temos aqui)"
echo ""

read -p "Digite a URL do seu repositório GitHub (ex: https://github.com/usuario/BIUAI.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    error "URL do repositório é obrigatória!"
    exit 1
fi

# Adicionar remote origin
log "Configurando remote origin..."
if git remote get-url origin > /dev/null 2>&1; then
    warning "Remote origin já existe. Removendo e reconfigurando..."
    git remote remove origin
fi

git remote add origin "$REPO_URL"
log "✓ Remote origin adicionado: $REPO_URL"

# Verificar se há mudanças para commit
if ! git diff-index --quiet HEAD --; then
    warning "Há mudanças não commitadas. Fazendo commit..."
    git add .
    git commit -m "Update: Ajustes finais e configuração do projeto"
fi

# Push para GitHub
log "Fazendo push para GitHub..."
if git push -u origin master; then
    log "✅ Projeto enviado para GitHub com sucesso!"
else
    error "❌ Erro ao fazer push. Verifique suas credenciais e URL."
    exit 1
fi

echo ""
echo "🎉 Configuração Concluída!"
echo ""
echo "📋 Próximos Passos:"
echo "1. Acesse seu repositório: $REPO_URL"
echo "2. Configure branch protection rules se necessário"
echo "3. Adicione colaboradores se for um projeto em equipe"
echo "4. Configure GitHub Pages se quiser hospedar a documentação"
echo ""
echo "🔧 Comandos Git Úteis:"
echo "- Ver status: git status"
echo "- Fazer commit: git add . && git commit -m 'sua mensagem'"
echo "- Enviar mudanças: git push"
echo "- Ver logs: git log --oneline"
echo ""
echo "📁 Estrutura do Projeto:"
echo "- Frontend: Vue.js + Vuetify (porta 8080)"
echo "- Backend: FastAPI (porta 3000)"
echo "- Chatbot: MCP + Ollama (portas 8001, 8002, 11434)"
echo "- Docs: Swagger em /docs e Redoc em /redoc"
echo ""

log "Projeto BIUAI configurado no GitHub! 🚀" 