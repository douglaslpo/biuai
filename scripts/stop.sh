#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Verifica se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando."
        exit 1
    fi
}

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verifica se o arquivo docker-compose.yml existe
if [ ! -f "docker-compose.yml" ]; then
    error "docker-compose.yml não encontrado em $PROJECT_DIR"
    exit 1
fi

# Cria diretório de logs se não existir
mkdir -p logs

# Nome do arquivo de log
LOG_FILE="logs/shutdown_$(date +'%Y%m%d_%H%M%S').log"

# Função para backup dos logs
backup_logs() {
    log "Fazendo backup dos logs antes de parar..."
    
    # Backup dos logs do sistema
    if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
        tar -czf "scripts/logs_$(date +'%Y%m%d_%H%M%S').tar.gz" logs/ >> "$LOG_FILE" 2>&1
        log "✓ Backup dos logs criado em scripts/"
    fi
    
    # Backup dos logs dos containers
    services=("backend" "frontend" "db" "redis" "model-server" "jupyter" "pgadmin" "ollama" "mcp-chatbot-service" "mcp-memory-server")
    for service in "${services[@]}"; do
        if [ "$(docker ps -q -f name=biuai_${service}_1)" ]; then
            docker logs "biuai_${service}_1" > "logs/${service}_shutdown_$(date +'%Y%m%d_%H%M%S').log" 2>&1
        fi
    done
}

# Função para parar os serviços
stop_services() {
    log "🛑 Parando Sistema BIUAI..."
    
    # Lista containers ativos
    active_containers=$(docker ps --filter "name=biuai_" --format "table {{.Names}}\t{{.Status}}" | wc -l)
    if [ $active_containers -gt 1 ]; then
        log "Encontrados $((active_containers-1)) containers ativos"
    else
        warning "Nenhum container BIUAI ativo encontrado"
    fi
    
    # Para os containers gracefully
    log "Parando containers (graceful shutdown)..."
    if docker-compose down --timeout 30 >> "$LOG_FILE" 2>&1; then
        log "✓ Containers parados graciosamente"
    else
        warning "Erro no graceful shutdown, forçando parada..."
        docker-compose down --timeout 5 >> "$LOG_FILE" 2>&1
    fi
    
    # Remove containers órfãos
    log "Removendo containers órfãos..."
    docker-compose down --remove-orphans >> "$LOG_FILE" 2>&1
    
    # Limpa volumes não utilizados (opcional, apenas volumes anônimos)
    log "Limpando volumes não utilizados..."
    docker volume prune -f >> "$LOG_FILE" 2>&1
    
    # Remove redes não utilizadas
    log "Limpando redes não utilizadas..."
    docker network prune -f >> "$LOG_FILE" 2>&1
    
    # Limpa imagens dangling (opcional)
    log "Limpando imagens temporárias..."
    docker image prune -f >> "$LOG_FILE" 2>&1
}

# Função para verificar se tudo parou
verify_shutdown() {
    local remaining_containers=$(docker ps --filter "name=biuai_" -q | wc -l)
    
    if [ $remaining_containers -eq 0 ]; then
        log "✅ Todos os containers BIUAI foram parados com sucesso"
    else
        warning "⚠️ Ainda existem $remaining_containers containers ativos:"
        docker ps --filter "name=biuai_" --format "table {{.Names}}\t{{.Status}}"
        
        # Opção para forçar remoção
        echo ""
        read -p "Deseja forçar a remoção dos containers restantes? (y/N): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Forçando remoção dos containers restantes..."
            docker ps --filter "name=biuai_" -q | xargs -r docker rm -f
        fi
    fi
}

# Função principal
main() {
    log "Iniciando processo de parada do Sistema BIUAI..."
    check_docker
    
    backup_logs
    stop_services
    verify_shutdown
    
    echo ""
    log "🎉 Sistema BIUAI parado com sucesso!"
    echo ""
    echo -e "${GREEN}📋 Resumo:${NC}"
    echo -e "- Logs salvos em: ${YELLOW}$LOG_FILE${NC}"
    echo -e "- Backup criado em: ${YELLOW}scripts/logs_$(date +'%Y%m%d_%H%M%S').tar.gz${NC}"
    echo ""
    echo -e "${GREEN}🔧 Próximos Passos:${NC}"
    echo -e "- Para reiniciar: ${YELLOW}./scripts/start.sh${NC}"
    echo -e "- Para ver logs: ${YELLOW}cat $LOG_FILE${NC}"
    echo -e "- Para limpar tudo: ${YELLOW}docker system prune -a${NC}"
    echo ""
}

main 