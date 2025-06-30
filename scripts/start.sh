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
        error "Docker não está rodando. Por favor, inicie o Docker primeiro."
        exit 1
    fi
}

# Função para verificar se um container está rodando
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
        if curl -s "http://localhost:${port}${endpoint}" > /dev/null; then
            log "✓ Serviço $service está respondendo na porta $port"
            return 0
        fi
        warning "Tentativa $attempt/$max_attempts - Aguardando serviço $service iniciar..."
        sleep 2
        ((attempt++))
    done

    error "❌ Serviço $service não está respondendo após $max_attempts tentativas"
    return 1
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

# Inicia os serviços
start_services() {
    log "Iniciando os serviços BIUAI..."
    
    # Remove containers órfãos e volumes não utilizados
    log "Limpando ambiente anterior..."
    docker-compose down --remove-orphans > /dev/null 2>&1
    docker volume prune -f > /dev/null 2>&1
    
    # Construir e iniciar os containers
    log "Construindo e iniciando containers..."
    if ! docker-compose up --build -d >> "$LOG_FILE" 2>&1; then
        error "Erro ao iniciar containers. Verifique o log em $LOG_FILE"
        exit 1
    fi
    
    log "Aguardando serviços iniciarem..."
    sleep 15

    # Verifica banco de dados
    if ! check_container "biuai_db_1"; then
        error "Banco de dados não iniciou corretamente"
        docker-compose logs db >> "$LOG_FILE"
        exit 1
    fi
    log "✓ PostgreSQL está rodando"

    # Verifica Redis
    if ! check_container "biuai_redis_1"; then
        error "Redis não iniciou corretamente"
        docker-compose logs redis >> "$LOG_FILE"
        exit 1
    fi
    log "✓ Redis está rodando"

    # Verifica backend
    if ! check_service_health "backend" "3000" "/health"; then
        error "Backend não iniciou corretamente"
        docker-compose logs backend >> "$LOG_FILE"
        exit 1
    fi

    # Verifica Ollama (pode demorar mais para carregar modelos)
    log "Verificando Ollama (pode demorar para carregar modelos)..."
    local ollama_attempts=60
    local attempt=1
    while [ $attempt -le $ollama_attempts ]; do
        if curl -s "http://localhost:11434/api/version" > /dev/null; then
            log "✓ Ollama está rodando na porta 11434"
            break
        fi
        if [ $attempt -eq $ollama_attempts ]; then
            warning "❌ Ollama pode não estar completamente inicializado, mas continuando..."
        fi
        warning "Tentativa $attempt/$ollama_attempts - Aguardando Ollama inicializar..."
        sleep 3
        ((attempt++))
    done

    # Verifica MCP Chatbot Service
    if ! check_service_health "mcp-chatbot" "8002" "/health"; then
        error "MCP Chatbot Service não iniciou corretamente"
        docker-compose logs mcp-chatbot-service >> "$LOG_FILE"
        exit 1
    fi

    # Verifica MCP Memory Service
    if ! check_service_health "mcp-memory" "8001" "/health"; then
        error "MCP Memory Service não iniciou corretamente"
        docker-compose logs mcp-memory-server >> "$LOG_FILE"
        exit 1
    fi

    # Verifica model-server
    if ! check_service_health "model-server" "8000" "/health"; then
        error "Model Server não iniciou corretamente"
        docker-compose logs model-server >> "$LOG_FILE"
        exit 1
    fi

    # Verifica frontend
    if ! check_service_health "frontend" "8080" "/"; then
        error "Frontend não iniciou corretamente"
        docker-compose logs frontend >> "$LOG_FILE"
        exit 1
    fi

    # Verifica outros serviços opcionais
    services=("jupyter" "pgadmin")
    for service in "${services[@]}"; do
        if check_container "biuai_${service}_1"; then
            log "✓ Serviço $service está rodando"
        else
            warning "❌ Serviço $service não está rodando"
            docker-compose logs "$service" >> "$LOG_FILE"
        fi
    done
}

# Função principal
main() {
    log "Iniciando Sistema BIUAI v2.0..."
    check_docker
    start_services
    
    # Exibe URLs de acesso
    echo ""
    log "🎉 Sistema BIUAI iniciado com sucesso!"
    echo ""
    echo -e "${GREEN}📱 URLs de Acesso:${NC}"
    echo -e "${GREEN}Frontend (UI):${NC} http://localhost:8080"
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
    echo -e "- Verificar logs: ${YELLOW}docker-compose logs <service>${NC}"
    echo -e "- Parar sistema: ${YELLOW}./scripts/stop.sh${NC}"
    echo -e "- Reiniciar: ${YELLOW}./scripts/stop.sh && ./scripts/start.sh${NC}"
    echo ""
    log "Para suporte técnico, acesse: http://localhost:8080/admin/chatbot"
}

main 