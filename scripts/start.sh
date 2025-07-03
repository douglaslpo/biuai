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

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Verifica se o Docker está rodando
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        error "Docker não está rodando. Por favor, inicie o Docker primeiro."
        exit 1
    fi
    log "✓ Docker está rodando"
}

# Verifica espaço em disco
check_disk_space() {
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local min_space=2000000  # 2GB em KB
    
    if [ "$available_space" -lt "$min_space" ]; then
        warning "Espaço em disco baixo ($(($available_space/1024/1024))GB disponível). Recomendado: 2GB+)"
    else
        log "✓ Espaço em disco suficiente ($(($available_space/1024/1024))GB disponível)"
    fi
}

# Verifica se um container está rodando
check_container() {
    if [ "$(docker ps -q -f name=$1)" ]; then
        return 0
    else
        return 1
    fi
}

# Função para verificar a saúde de um serviço
check_service_health() {
    local service=$1
    local port=$2
    local endpoint=$3
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "http://localhost:${port}${endpoint}" > /dev/null 2>&1; then
            log "✓ Serviço $service está respondendo na porta $port"
            return 0
        fi
        info "Tentativa $attempt/$max_attempts - Aguardando serviço $service inicializar..."
        sleep 2
        ((attempt++))
    done

    error "❌ Serviço $service não está respondendo após $max_attempts tentativas"
    return 1
}

# Limpa environment anterior
cleanup_environment() {
    log "Limpando ambiente anterior..."
    
    # Para todos os containers do projeto
    docker-compose down --remove-orphans --volumes > /dev/null 2>&1
    
    # Remove imagens órfãs do projeto
    docker images --filter "dangling=true" -q | head -10 | xargs -r docker rmi > /dev/null 2>&1
    
    # Limpa volumes não utilizados (cuidado com volumes importantes)
    docker volume prune -f > /dev/null 2>&1
    
    # Limpa cache do build se necessário
    docker builder prune -f > /dev/null 2>&1
    
    log "✓ Ambiente limpo"
}

# Verifica dependências do frontend
check_frontend_dependencies() {
    log "Verificando dependências do frontend..."
    
    if [ ! -f "frontend/package.json" ]; then
        error "package.json não encontrado no frontend"
        return 1
    fi
    
    # Verifica se vue-countup-v3 está no package.json
    if ! grep -q "vue-countup-v3" frontend/package.json; then
        warning "Dependência vue-countup-v3 não encontrada. Pode causar erro de build."
        return 1
    fi
    
    log "✓ Dependências do frontend verificadas"
    return 0
}

# Força rebuild do frontend se necessário
force_frontend_rebuild() {
    log "Forçando rebuild do frontend..."
    
    # Remove node_modules se existir no container
    docker-compose run --rm frontend sh -c "rm -rf node_modules package-lock.json" > /dev/null 2>&1
    
    # Rebuild sem cache
    docker-compose build --no-cache frontend
    
    if [ $? -eq 0 ]; then
        log "✓ Frontend reconstruído com sucesso"
        return 0
    else
        error "❌ Falha na reconstrução do frontend"
        return 1
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
LOG_FILE="logs/startup_$(date +'%Y%m%d_%H%M%S').log"

# Função para capturar e analisar erros
analyze_build_error() {
    local service=$1
    local log_file=$2
    
    if grep -q "vue-countup-v3" "$log_file"; then
        error "Erro de dependência: vue-countup-v3 não encontrada"
        error "Solução: Execute 'cd frontend && npm install vue-countup-v3'"
        return 1
    fi
    
    if grep -q "ENOSPC" "$log_file"; then
        error "Erro de espaço em disco insuficiente"
        error "Solução: Libere espaço em disco ou limpe cache do Docker"
        return 1
    fi
    
    if grep -q "network" "$log_file"; then
        error "Erro de rede durante build"
        error "Solução: Verifique sua conexão com a internet"
        return 1
    fi
    
    return 0
}

# Inicia os serviços
start_services() {
    log "Iniciando os serviços BIUAI..."
    
    # Verifica dependências primeiro
    if ! check_frontend_dependencies; then
        warning "Problemas nas dependências detectados. Tentando corrigir..."
        if ! force_frontend_rebuild; then
            error "Não foi possível corrigir as dependências. Verifique manualmente."
            exit 1
        fi
    fi
    
    cleanup_environment
    
    # Construir e iniciar os containers
    log "Construindo e iniciando containers..."
    
    # Tenta build normal primeiro
    if ! timeout 300 docker-compose up --build -d >> "$LOG_FILE" 2>&1; then
        error "Erro ao iniciar containers na primeira tentativa"
        
        # Analisa o erro
        analyze_build_error "frontend" "$LOG_FILE"
        
        # Tenta rebuild forçado do frontend
        warning "Tentando rebuild forçado do frontend..."
        if force_frontend_rebuild; then
            log "Tentando iniciar novamente após rebuild..."
            if ! timeout 300 docker-compose up -d >> "$LOG_FILE" 2>&1; then
                error "Erro persistente ao iniciar containers. Verifique o log em $LOG_FILE"
                exit 1
            fi
        else
            error "Falha no rebuild. Verifique o log em $LOG_FILE"
            exit 1
        fi
    fi
    
    log "Aguardando serviços iniciarem..."
    sleep 20

    # Verifica banco de dados
    info "Verificando PostgreSQL..."
    if ! check_container "biuai-db-1" && ! check_container "biuai_db_1"; then
        error "Banco de dados não iniciou corretamente"
        docker-compose logs db >> "$LOG_FILE"
        exit 1
    fi
    log "✓ PostgreSQL está rodando"

    # Verifica Redis
    info "Verificando Redis..."
    if ! check_container "biuai-redis-1" && ! check_container "biuai_redis_1"; then
        error "Redis não iniciou corretamente"
        docker-compose logs redis >> "$LOG_FILE"
        exit 1
    fi
    log "✓ Redis está rodando"

    # Verifica backend
    info "Verificando Backend..."
    if ! check_service_health "backend" "3000" "/health"; then
        error "Backend não iniciou corretamente"
        docker-compose logs backend >> "$LOG_FILE"
        exit 1
    fi

    # Verifica model-server
    info "Verificando Model Server..."
    if ! check_service_health "model-server" "8000" "/health"; then
        error "Model Server não iniciou corretamente"
        docker-compose logs model-server >> "$LOG_FILE"
        exit 1
    fi

    # Verifica frontend
    info "Verificando Frontend..."
    if ! check_service_health "frontend" "8080" "/"; then
        error "Frontend não iniciou corretamente"
        docker-compose logs frontend >> "$LOG_FILE"
        exit 1
    fi

    # Verifica Ollama (pode demorar mais para carregar modelos)
    info "Verificando Ollama (pode demorar para carregar modelos)..."
    local ollama_attempts=60
    local attempt=1
    while [ $attempt -le $ollama_attempts ]; do
        if curl -s --max-time 10 "http://localhost:11434/api/version" > /dev/null 2>&1; then
            log "✓ Ollama está rodando na porta 11434"
            break
        fi
        if [ $attempt -eq $ollama_attempts ]; then
            warning "❌ Ollama pode não estar completamente inicializado, mas continuando..."
        fi
        info "Tentativa $attempt/$ollama_attempts - Aguardando Ollama inicializar..."
        sleep 5
        ((attempt++))
    done

    # Verifica MCP Services
    info "Verificando MCP Memory Service..."
    if ! check_service_health "mcp-memory" "8001" "/health"; then
        warning "❌ MCP Memory Service não iniciou corretamente (não crítico)"
        docker-compose logs mcp-memory-server >> "$LOG_FILE"
    fi

    info "Verificando MCP Chatbot Service..."
    if ! check_service_health "mcp-chatbot" "8002" "/health"; then
        warning "❌ MCP Chatbot Service não iniciou corretamente (não crítico)"
        docker-compose logs mcp-chatbot-service >> "$LOG_FILE"
    fi

    # Verifica outros serviços opcionais
    info "Verificando serviços opcionais..."
    optional_services=("jupyter" "pgadmin")
    for service in "${optional_services[@]}"; do
        if check_container "biuai-${service}-1" || check_container "biuai_${service}_1"; then
            log "✓ Serviço $service está rodando"
        else
            warning "❌ Serviço $service não está rodando (opcional)"
        fi
    done
}

# Função para mostrar status dos serviços
show_service_status() {
    echo ""
    echo -e "${CYAN}📊 Status dos Serviços:${NC}"
    echo ""
    
    services=("frontend:8080" "backend:3000" "db:5432" "redis:6379" "model-server:8000" "ollama:11434" "mcp-memory-server:8001" "mcp-chatbot-service:8002")
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        if check_container "biuai-${service}-1" || check_container "biuai_${service}_1"; then
            echo -e "${GREEN}✓${NC} $service (porta $port)"
        else
            echo -e "${RED}✗${NC} $service (porta $port)"
        fi
    done
}

# Função principal
main() {
    echo -e "${PURPLE}"
    echo "██████╗ ██╗██╗   ██╗ █████╗ ██╗    ██╗   ██╗██████╗    ██████╗  "
    echo "██╔══██╗██║██║   ██║██╔══██╗██║    ██║   ██║╚════██╗  ██╔═████╗ "
    echo "██████╔╝██║██║   ██║███████║██║    ██║   ██║ █████╔╝  ██║██╔██║ "
    echo "██╔══██╗██║██║   ██║██╔══██║██║    ╚██╗ ██╔╝██╔═══╝   ████╔╝██║ "
    echo "██████╔╝██║╚██████╔╝██║  ██║██║     ╚████╔╝ ███████╗██╗╚██████╔╝ "
    echo "╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝      ╚═══╝  ╚══════╝╚═╝ ╚═════╝  "
    echo -e "${NC}"
    echo ""
    
    log "Iniciando Sistema BIUAI v2.0..."
    info "Log detalhado será salvo em: $LOG_FILE"
    
    check_docker
    check_disk_space
    start_services
    
    # Exibe URLs de acesso
    echo ""
    log "🎉 Sistema BIUAI iniciado com sucesso!"
    echo ""
    echo -e "${GREEN}📱 URLs de Acesso:${NC}"
    echo -e "${GREEN}Frontend (Dashboard):${NC} http://localhost:8080"
    echo -e "${GREEN}Backend API:${NC} http://localhost:3000"
    echo -e "${GREEN}API Docs (Swagger):${NC} http://localhost:3000/docs"
    echo -e "${GREEN}API Docs (Redoc):${NC} http://localhost:3000/redoc"
    echo -e "${GREEN}Model Server:${NC} http://localhost:8000"
    echo -e "${GREEN}Jupyter Lab:${NC} http://localhost:8888"
    echo -e "${GREEN}PgAdmin:${NC} http://localhost:5050"
    echo ""
    echo -e "${GREEN}🤖 Serviços MCP:${NC}"
    echo -e "${GREEN}Ollama API:${NC} http://localhost:11434"
    echo -e "${GREEN}MCP Chatbot:${NC} http://localhost:8002"
    echo -e "${GREEN}MCP Memory:${NC} http://localhost:8001"
    echo ""
    echo -e "${GREEN}🔧 Comandos Úteis:${NC}"
    echo -e "  ${CYAN}Ver logs:${NC} docker-compose logs -f [serviço]"
    echo -e "  ${CYAN}Parar sistema:${NC} docker-compose down"
    echo -e "  ${CYAN}Restart serviço:${NC} docker-compose restart [serviço]"
    echo -e "  ${CYAN}Status completo:${NC} docker-compose ps"
    echo ""
    
    show_service_status
    
    echo ""
    log "Sistema pronto para uso! 🚀"
    echo -e "${YELLOW}💡 Dica: Se algum serviço falhar, verifique os logs com 'docker-compose logs [serviço]'${NC}"
}

# Captura sinais para cleanup
trap 'echo -e "\n${YELLOW}Encerrando...${NC}"; exit 0' INT TERM

# Executa função principal
main "$@" 