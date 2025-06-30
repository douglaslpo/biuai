#!/bin/bash

# Script para configurar repositório GitHub para BIUAI
# Usuario: douglaslpo

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

echo ""
echo "🏦 BIUAI - Configuração Automática do GitHub"
echo "=============================================="
echo ""

# Verificar se é um repositório git
if [ ! -d ".git" ]; then
    log "Inicializando repositório Git..."
    git init
    git config user.name "Douglas LPO"
    git config user.email "douglaslpo@gmail.com"
else
    log "Repositório Git já inicializado"
fi

# Verificar se há arquivos para commit
if [ -z "$(git status --porcelain)" ]; then
    warning "Todos os arquivos já estão commitados"
else
    log "Adicionando arquivos ao Git..."
    git add .
    
    log "Fazendo commit das alterações..."
    git commit -m "🚀 BIUAI v2.0 - Sistema Completo com Chatbot MCP

✅ Implementação completa do sistema BIUAI v2.0
✅ Backend FastAPI 0.115.14 com APIs documentadas  
✅ Frontend Vue.js 3 + Vuetify 3 responsivo
✅ Chatbot MCP 'Bi UAI Bot Administrador' integrado
✅ Ollama local com modelo llama3.2:3b gratuito
✅ PostgreSQL + Redis para dados e cache
✅ Docker Compose com 9 serviços orquestrados
✅ Scripts automatizados de start/stop
✅ Jupyter Lab para análise de dados
✅ Sistema de autenticação JWT completo
✅ Base de conhecimento especializada BIUAI
✅ Documentação técnica detalhada
✅ Conflitos de dependências resolvidos

Principais funcionalidades:
- Dashboard financeiro interativo com métricas em tempo real
- Gestão completa de lançamentos (receitas/despesas)
- Categorização automática inteligente com IA
- Relatórios e analytics avançados
- Chatbot especializado para suporte 24/7
- APIs REST documentadas com Swagger/ReDoc
- Interface responsiva e moderna
- Deploy containerizado completo

Tecnologias: FastAPI, Vue.js, Ollama, PostgreSQL, Redis, Docker"
fi

# Nome do repositório
REPO_NAME="BIUAI"
GITHUB_USER="douglaslpo"

info "📦 Configurando repositório para usuário: ${GITHUB_USER}"
info "📦 Nome do repositório: ${REPO_NAME}"

# Verificar se o remote já existe
if git remote get-url origin >/dev/null 2>&1; then
    CURRENT_REMOTE=$(git remote get-url origin)
    warning "Remote origin já configurado: ${CURRENT_REMOTE}"
    
    echo ""
    info "🔄 Deseja reconfigurar o remote? (s/n)"
    read -r response
    if [[ "$response" =~ ^[Ss]$ ]]; then
        git remote remove origin
        log "Remote origin removido"
    else
        info "Mantendo configuração atual do remote"
        echo ""
        info "✅ Para fazer push: git push -u origin main"
        exit 0
    fi
fi

# Configurar o remote
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
log "Configurando remote origin: ${REPO_URL}"
git remote add origin "$REPO_URL"

# Verificar se estamos na branch main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log "Renomeando branch para 'main'"
    git branch -M main
fi

echo ""
echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================="
echo ""
info "📋 PRÓXIMOS PASSOS:"
echo ""
echo "1. 🌐 Acesse: https://github.com/new"
echo "2. 📝 Repository name: ${REPO_NAME}"
echo "3. 📝 Description: 'Sistema completo de gestão financeira com IA - BIUAI v2.0'"
echo "4. 🔓 Visibilidade: Public (recomendado para portfolio)"
echo "5. ❌ NÃO marque 'Add a README file' (já temos)"
echo "6. ❌ NÃO adicione .gitignore (já temos)"
echo "7. ❌ NÃO escolha licença (já temos MIT)"
echo "8. ✅ Clique em 'Create repository'"
echo ""
echo "9. 🚀 Execute o comando:"
echo "   git push -u origin main"
echo ""
warning "⚠️  Se o repositório já existir, use:"
echo "   git push origin main --force"
echo ""
info "🔗 URL do repositório: ${REPO_URL}"
echo ""
log "✅ Repositório local configurado e pronto para push!"

# Mostrar status final
echo ""
echo "📊 STATUS ATUAL:"
echo "==============="
git status --short | head -10
echo ""
git log --oneline -3
echo ""
info "🎯 Total de arquivos no projeto: $(find . -type f -not -path './.git/*' | wc -l)"
info "🎯 Linhas de código: $(find . -name '*.py' -o -name '*.vue' -o -name '*.js' -o -name '*.ts' | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}' || echo 'N/A')" 