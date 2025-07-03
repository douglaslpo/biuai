#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Header
echo -e "${PURPLE}"
echo "██████╗ ██╗██╗   ██╗ █████╗ ██╗    ███████╗████████╗ ██████╗ ██████╗ "
echo "██╔══██╗██║██║   ██║██╔══██╗██║    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗"
echo "██████╔╝██║██║   ██║███████║██║    ███████╗   ██║   ██║   ██║██████╔╝"
echo "██╔══██╗██║██║   ██║██╔══██║██║    ╚════██║   ██║   ██║   ██║██╔═══╝ "
echo "██████╔╝██║╚██████╔╝██║  ██║██║    ███████║   ██║   ╚██████╔╝██║     "
echo "╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     "
echo -e "${NC}"
echo ""

log "Parando Sistema BIUAI v2.0..."

# Verifica se o Docker Compose está rodando
if ! docker-compose ps > /dev/null 2>&1; then
    warning "Nenhum container do projeto encontrado ou Docker Compose não está disponível."
    exit 0
fi

# Lista containers ativos antes de parar
info "Containers ativos encontrados:"
docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}" | head -10

echo ""
log "Parando todos os serviços..."

# Para todos os containers
if docker-compose down --remove-orphans > /dev/null 2>&1; then
    log "✓ Todos os containers foram parados com sucesso"
else
    warning "❌ Alguns containers podem não ter parado corretamente"
fi

# Opção para limpar volumes (comentada por segurança)
read -p "$(echo -e ${YELLOW}Deseja remover volumes de dados? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    warning "Removendo volumes de dados..."
    docker-compose down --volumes > /dev/null 2>&1
    log "✓ Volumes removidos"
else
    info "Volumes de dados preservados"
fi

# Limpeza opcional de imagens órfãs
read -p "$(echo -e ${YELLOW}Deseja limpar imagens órfãs do Docker? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Limpando imagens órfãs..."
    docker image prune -f > /dev/null 2>&1
    log "✓ Imagens órfãs removidas"
fi

echo ""
log "🛑 Sistema BIUAI parado com sucesso!"
echo ""
echo -e "${CYAN}📝 Para reiniciar o sistema:${NC}"
echo -e "  ${GREEN}./scripts/start.sh${NC}"
echo ""
echo -e "${CYAN}📋 Outros comandos úteis:${NC}"
echo -e "  ${GREEN}Ver containers parados:${NC} docker-compose ps -a"
echo -e "  ${GREEN}Limpar tudo:${NC} docker system prune"
echo -e "  ${GREEN}Reiniciar Docker:${NC} sudo systemctl restart docker"
echo "" 