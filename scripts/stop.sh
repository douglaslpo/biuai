#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
LOG_DIR="logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/stop_${TIMESTAMP}.log"
TIMEOUT=60 # segundos para aguardar parada graciosa

# Força uso exclusivo de docker-compose (standalone)
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}ERROR: docker-compose não está instalado${NC}"
    exit 1
fi
DOCKER_COMPOSE="docker-compose"

# Função para logging
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[${timestamp}] $1"
    echo "[${timestamp}] $1" >> "$LOG_FILE"
}

# Função para logging de erro
log_error() {
    log "${RED}ERROR: $1${NC}"
}

# Função para logging de sucesso
log_success() {
    log "${GREEN}✓ $1${NC}"
}

# Função para logging de aviso
log_warning() {
    log "${YELLOW}WARNING: $1${NC}"
}

# Função para logging de info
log_info() {
    log "${BLUE}INFO: $1${NC}"
}

# Função para salvar logs dos containers
save_container_logs() {
    log "Salvando logs dos containers..."
    local containers=$("$DOCKER_COMPOSE" ps -q 2>/dev/null)
    
    if [ -n "$containers" ]; then
        for container in $containers; do
            local name=$("$DOCKER_COMPOSE" inspect --format='{{.Name}}' "$container" | sed 's/\///')
            "$DOCKER_COMPOSE" logs "$container" &> "${LOG_DIR}/${name}_${TIMESTAMP}.log"
        done
        log_success "Logs dos containers salvos em ${LOG_DIR}"
    else
        log_info "Nenhum container encontrado para salvar logs"
    fi
}

# Função para parar containers
stop_containers() {
    log "Parando containers..."
    
    # Tenta parada graciosa primeiro
    if ! timeout $TIMEOUT "$DOCKER_COMPOSE" down &>> "$LOG_FILE"; then
        log_warning "Timeout ao parar containers graciosamente"
        
        # Força parada se necessário
        log_warning "Forçando parada dos containers..."
        "$DOCKER_COMPOSE" down -v --remove-orphans -t 0 &>> "$LOG_FILE"
    fi
    
    # Verifica se ainda há containers rodando
    local running_containers=$("$DOCKER_COMPOSE" ps --filter "name=biuai" -q)
    if [ -n "$running_containers" ]; then
        log_warning "Alguns containers ainda estão rodando. Forçando parada..."
        "$DOCKER_COMPOSE" stop $running_containers &>> "$LOG_FILE"
    fi
    
    log_success "Containers parados"
}

# Função para limpar recursos
cleanup_resources() {
    log "Limpando recursos..."
    
    # Remove containers parados
    local stopped_containers=$("$DOCKER_COMPOSE" ps -a --filter "name=biuai" -q)
    if [ -n "$stopped_containers" ]; then
        "$DOCKER_COMPOSE" rm $stopped_containers &>> "$LOG_FILE"
        log_success "Containers removidos"
    fi
    
    # Remove redes não utilizadas
    "$DOCKER_COMPOSE" network prune -f &>> "$LOG_FILE"
    log_success "Redes não utilizadas removidas"
    
    # Remove volumes não utilizados (opcional)
    if [ "$1" = "--clean-volumes" ]; then
        log_warning "Removendo volumes não utilizados..."
        "$DOCKER_COMPOSE" volume prune -f &>> "$LOG_FILE"
        log_success "Volumes não utilizados removidos"
    fi
    
    # Remove imagens não utilizadas (opcional)
    if [ "$1" = "--clean-images" ]; then
        log_warning "Removendo imagens não utilizadas..."
        "$DOCKER_COMPOSE" image prune -f &>> "$LOG_FILE"
        log_success "Imagens não utilizadas removidas"
    fi
}

# Função para verificar processos
check_processes() {
    log "Verificando processos relacionados..."
    
    # Verifica processos Python
    local python_processes=$(ps aux | grep -i "python.*biuai" | grep -v grep)
    if [ -n "$python_processes" ]; then
        log_warning "Processos Python encontrados:"
        echo "$python_processes" >> "$LOG_FILE"
        
        # Tenta matar processos graciosamente
        pkill -15 -f "python.*biuai"
        sleep 5
        
        # Força kill se necessário
        if ps aux | grep -i "python.*biuai" | grep -v grep &>/dev/null; then
            log_warning "Forçando kill dos processos Python..."
            pkill -9 -f "python.*biuai"
        fi
    fi
    
    # Verifica processos Node
    local node_processes=$(ps aux | grep -i "node.*biuai" | grep -v grep)
    if [ -n "$node_processes" ]; then
        log_warning "Processos Node encontrados:"
        echo "$node_processes" >> "$LOG_FILE"
        
        # Tenta matar processos graciosamente
        pkill -15 -f "node.*biuai"
        sleep 5
        
        # Força kill se necessário
        if ps aux | grep -i "node.*biuai" | grep -v grep &>/dev/null; then
            log_warning "Forçando kill dos processos Node..."
            pkill -9 -f "node.*biuai"
        fi
    fi
}

# Função para verificar portas
check_ports() {
    log "Verificando portas utilizadas..."
    local ports=(8000 8080 8001 8002 8003 8888 11434)
    
    for port in "${ports[@]}"; do
        local pid=$(lsof -i :$port -t)
        if [ -n "$pid" ]; then
            log_warning "Porta $port em uso pelo processo $pid"
            kill -15 $pid &>> "$LOG_FILE"
            sleep 2
            
            # Verifica se processo ainda existe
            if lsof -i :$port -t &>/dev/null; then
                log_warning "Forçando kill do processo na porta $port"
                kill -9 $pid &>> "$LOG_FILE"
            fi
        fi
    done
}

# Função para limpeza total
cleanup_all() {
    log_warning "Removendo todos os volumes, imagens e redes do projeto..."
    "$DOCKER_COMPOSE" down -v --rmi all --remove-orphans &>> "$LOG_FILE"
    docker system prune -af &>> "$LOG_FILE"
    log_success "Volumes, imagens e redes removidos."
}

# Função principal
main() {
    # Garante diretório de logs
    mkdir -p "$LOG_DIR"
    
    # Parse de flags
    CLEAN_ALL=false
    for arg in "$@"; do
      case $arg in
        --clean-all)
          CLEAN_ALL=true
          ;;
        --timeout=*)
          TIMEOUT="${arg#*=}"
          ;;
      esac
    done
    
    # Registra início no log
    log_info "Iniciando parada do sistema BIUAI..."
    log_info "Log detalhado será salvo em: $LOG_FILE"
    
    # Salva logs dos containers antes de parar
    save_container_logs
    
    # Para containers
    stop_containers
    
    # Verifica e mata processos
    check_processes
    
    # Verifica e libera portas
    check_ports
    
    # Limpa recursos
    if [ "$CLEAN_ALL" = true ]; then
        cleanup_all
    else
        cleanup_resources "$1"
    fi
    
    log_success "Sistema BIUAI parado com sucesso!"
    exit 0
}

# Executa função principal com argumentos
main "$@" 