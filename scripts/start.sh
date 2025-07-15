#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/startup_${TIMESTAMP}.log"
MIN_DISK_SPACE=10 # GB
RETRY_LIMIT=3
HEALTHCHECK_TIMEOUT=300 # segundos

# Adicionar parsing de flags para PgAdmin e Signoz
START_PGADMIN=false
START_SIGNOZ=false

for arg in "$@"; do
  case $arg in
    --pgadmin)
      START_PGADMIN=true
      ;;
    --signoz)
      START_SIGNOZ=true
      ;;
  esac
done

# Força uso exclusivo de docker-compose (standalone)
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}ERROR: docker-compose não está instalado${NC}"
    exit 1
fi
DOCKER_COMPOSE="docker-compose"

# Garante diretórios essenciais
mkdir -p "$LOG_DIR"
mkdir -p "${PROJECT_ROOT}/data"

# Parse de flags adicionais
REBUILD=false
for arg in "$@"; do
  case $arg in
    --rebuild)
      REBUILD=true
      ;;
    --pgadmin)
      START_PGADMIN=true
      ;;
    --signoz)
      START_SIGNOZ=true
      ;;
  esac
done

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

# Função para exibir banner
show_banner() {
    echo -e "
██████╗ ██╗██╗   ██╗ █████╗ ██╗    ██╗   ██╗██████╗    ██████╗  
██╔══██╗██║██║   ██║██╔══██╗██║    ██║   ██║╚════██╗  ██╔═████╗ 
██████╔╝██║██║   ██║███████║██║    ██║   ██║ █████╔╝  ██║██╔██║ 
██╔══██╗██║██║   ██║██╔══██║██║    ╚██╗ ██╔╝██╔═══╝   ████╔╝██║ 
██████╔╝██║╚██████╔╝██║  ██║██║     ╚████╔╝ ███████╗██╗╚██████╔╝ 
╚═════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝      ╚═══╝  ╚══════╝╚═╝ ╚═════╝  
"
    log "Iniciando Sistema BIUAI v2.1..."
}

# Função para verificar requisitos
check_requirements() {
    # Verifica se Docker está instalado e rodando
    if ! command -v docker &> /dev/null || ! docker info &> /dev/null; then
        log_error "Docker não está instalado ou não está rodando"
        return 1
    fi
    log_success "Docker está rodando"

    # Verifica espaço em disco
    local available_space=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt "$MIN_DISK_SPACE" ]; then
        log_error "Espaço em disco insuficiente (${available_space}GB disponível, mínimo ${MIN_DISK_SPACE}GB)"
        return 1
    fi
    log_success "Espaço em disco suficiente (${available_space}GB disponível)"

    return 0
}

# Função para verificar arquivos necessários
check_required_files() {
    log "Verificando arquivos necessários..."
    
    # Lista de arquivos requeridos
    local required_files=(
        "docker-compose.yml"
        "frontend/package.json"
        "frontend/vite.config.js"
        "frontend/nginx.conf"
        "backend/requirements.txt"
        "backend/app/main.py"
        "backend/alembic.ini"
        "ml_service/requirements.txt"
        "ml_service/app.py"
        "mcp-memory-service/requirements.txt"
        "mcp-memory-service/main.py"
        "mcp-chatbot-service/requirements.txt"
        "mcp-chatbot-service/main.py"
        "jupyter/requirements.txt"
        "etl_service/requirements.txt"
        "etl_service/main.py"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/${file}" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -ne 0 ]; then
        log_error "Arquivos necessários não encontrados:"
        for file in "${missing_files[@]}"; do
            log_error "- $file"
        done
        return 1
    fi
    
    log_success "Todos os arquivos necessários encontrados"
    return 0
}

# Função para verificar configurações do Docker
check_docker_config() {
    log "Verificando configurações do Docker..."
    
    # Verifica se docker-compose.yml existe
    if [ ! -f "${PROJECT_ROOT}/docker-compose.yml" ]; then
        log_error "Arquivo docker-compose.yml não encontrado"
        return 1
    fi
    
    # Verifica se os Dockerfiles existem
    local dockerfiles=(
        "frontend/Dockerfile"
        "backend/Dockerfile"
        "jupyter/Dockerfile"
        "mcp-memory-service/Dockerfile"
        "mcp-chatbot-service/Dockerfile"
        "ml_service/Dockerfile"
        "etl_service/Dockerfile"
    )
    
    local missing_dockerfiles=()
    for dockerfile in "${dockerfiles[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/${dockerfile}" ]; then
            missing_dockerfiles+=("$dockerfile")
        fi
    done
    
    if [ ${#missing_dockerfiles[@]} -ne 0 ]; then
        log_error "Dockerfiles não encontrados:"
        for dockerfile in "${missing_dockerfiles[@]}"; do
            log_error "- $dockerfile"
        done
        return 1
    fi
    
    # Verifica configurações do NVIDIA Docker
    if ! command -v nvidia-smi &> /dev/null; then
        log_warning "NVIDIA Driver não encontrado. GPU não estará disponível para Ollama"
    else
        if ! docker info | grep -i "nvidia" &> /dev/null; then
            log_warning "NVIDIA Docker Runtime não configurado. GPU não estará disponível"
        else
            log_success "Suporte a GPU detectado e configurado"
        fi
    fi
    
    log_success "Configurações do Docker verificadas"
    return 0
}

# Função para verificar dependências do frontend
check_frontend_deps() {
    log "Verificando dependências do frontend..."
    
    # Verifica se o diretório frontend existe
    if [ ! -d "${PROJECT_ROOT}/frontend" ]; then
        log_warning "Diretório frontend não encontrado. Criando estrutura básica..."
        
        # Cria estrutura básica do frontend
        mkdir -p "${PROJECT_ROOT}/frontend/src/{components,views,store,assets}"
        
        # Cria package.json básico
        cat > "${PROJECT_ROOT}/frontend/package.json" << EOF
{
  "name": "biuai-frontend",
  "version": "2.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "serve": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.6",
    "axios": "^1.4.0",
    "vue-countup-v3": "^1.3.0",
    "chart.js": "^4.3.3",
    "quasar": "^2.12.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.3",
    "vite": "^4.4.9"
  }
}
EOF
        
        # Cria arquivo de configuração do Vite
        cat > "${PROJECT_ROOT}/frontend/vite.config.js" << EOF
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF
        
        # Cria arquivo index.html básico
        cat > "${PROJECT_ROOT}/frontend/index.html" << EOF
<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIUAI v2.1</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
EOF
        
        # Cria arquivo main.js básico
        cat > "${PROJECT_ROOT}/frontend/src/main.js" << EOF
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { Quasar } from 'quasar'
import '@quasar/extras/material-icons/material-icons.css'
import 'quasar/dist/quasar.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(Quasar, {
  plugins: {},
  config: {
    brand: {
      primary: '#1976D2',
      secondary: '#26A69A',
      accent: '#9C27B0',
      dark: '#1D1D1D'
    }
  }
})

app.mount('#app')
EOF
        
        # Cria arquivo App.vue básico
        cat > "${PROJECT_ROOT}/frontend/src/App.vue" << EOF
<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>BIUAI v2.1</q-toolbar-title>
      </q-toolbar>
    </q-header>
    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
// Componente principal
</script>
EOF
        
        # Cria arquivo de rotas básico
        mkdir -p "${PROJECT_ROOT}/frontend/src/router"
        cat > "${PROJECT_ROOT}/frontend/src/router/index.js" << EOF
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue')
    }
  ]
})

export default router
EOF
        
        # Cria view Home básica
        mkdir -p "${PROJECT_ROOT}/frontend/src/views"
        cat > "${PROJECT_ROOT}/frontend/src/views/Home.vue" << EOF
<template>
  <div class="q-pa-md">
    <h1>Bem-vindo ao BIUAI</h1>
    <p>Sistema de Análise de FIIs com IA</p>
  </div>
</template>

<script setup>
// Home view
</script>
EOF
        
        log_success "Estrutura básica do frontend criada"
    fi
    
    cd "${PROJECT_ROOT}/frontend" || return 1
    
    # Lista de dependências críticas
    local deps=(
        "vue"
        "vue-router"
        "pinia"
        "axios"
        "vue-countup-v3"
        "chart.js"
        "quasar"
    )
    
    local missing_deps=()
    
    # Verifica package.json
    for dep in "${deps[@]}"; do
        if ! grep -q "\"$dep\":" package.json; then
            missing_deps+=("$dep")
        fi
    done
    
    # Instala dependências faltantes
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_warning "Dependências faltantes: ${missing_deps[*]}"
        log "Instalando dependências faltantes..."
        npm install "${missing_deps[@]}" --save
        if [ $? -ne 0 ]; then
            log_error "Falha ao instalar dependências"
            return 1
        fi
    fi
    
    cd "${PROJECT_ROOT}" || return 1
    log_success "Dependências do frontend verificadas"
    return 0
}

# Função para limpar ambiente
clean_environment() {
    log "Limpando ambiente anterior..."
    
    cd "${PROJECT_ROOT}" || return 1
    
    # Para todos os containers
    "$DOCKER_COMPOSE" down --remove-orphans &>> "$LOG_FILE"
    
    # Remove containers parados
    docker container prune -f &>> "$LOG_FILE"
    
    # Limpa volumes não utilizados
    docker volume prune -f &>> "$LOG_FILE"
    
    # Remove imagens antigas
    docker image prune -f &>> "$LOG_FILE"
    
    log_success "Ambiente limpo"
}

# Função para verificar e baixar modelo do Ollama
check_ollama_model() {
    log "Verificando modelo do Ollama..."
    
    # Aguarda o Ollama inicializar
    log "Aguardando Ollama inicializar..."
    local timeout=120
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -s --max-time 5 "http://localhost:11434/api/health" &> /dev/null; then
            log_success "Ollama inicializado"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
        log_info "Aguardando Ollama... (${elapsed}s de ${timeout}s)"
    done
    
    if [ $elapsed -ge $timeout ]; then
        log_error "Timeout aguardando Ollama inicializar"
        log_error "Logs do container:"
        docker logs biuai-ollama
        return 1
    fi
    
    # Verifica se o modelo está disponível
    log "Verificando modelo llama2..."
    if ! curl -s --max-time 5 "http://localhost:11434/api/tags" | grep -q "llama2"; then
        log_warning "Modelo llama2 não encontrado. Baixando..."
        
        # Inicia download do modelo
        curl -s -X POST "http://localhost:11434/api/pull" \
             -H "Content-Type: application/json" \
             -d '{"name": "llama2"}' &>> "$LOG_FILE" &
        
        # Aguarda download completar
        local timeout=600
        local elapsed=0
        while [ $elapsed -lt $timeout ]; do
            if curl -s --max-time 5 "http://localhost:11434/api/tags" | grep -q "llama2"; then
                log_success "Modelo llama2 baixado com sucesso"
                return 0
            fi
            sleep 10
            elapsed=$((elapsed + 10))
            log_info "Aguardando download do modelo... (${elapsed}s de ${timeout}s)"
        done
        
        log_error "Timeout aguardando download do modelo"
        log_error "Logs do container:"
        docker logs biuai-ollama
        return 1
    fi
    
    log_success "Modelo llama2 está disponível"
    return 0
}

# Função para iniciar serviços
start_services() {
    local retry_count=0
    
    cd "${PROJECT_ROOT}" || return 1
    
    # Primeiro, verifica os arquivos e configurações
    if ! check_required_files || ! check_docker_config; then
        log_error "Falha na verificação dos requisitos"
        return 1
    fi
    
    # Inicia serviços base primeiro
    log "Iniciando serviços base (PostgreSQL e Redis)..."
    if ! "$DOCKER_COMPOSE" up -d db redis &>> "$LOG_FILE"; then
        log_error "Falha ao iniciar serviços base"
        "$DOCKER_COMPOSE" logs db redis
        return 1
    fi
    
    # Aguarda serviços base estarem saudáveis
    log "Aguardando serviços base inicializarem..."
    local timeout=60
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if "$DOCKER_COMPOSE" ps | grep -q "db.*healthy" && \
           "$DOCKER_COMPOSE" ps | grep -q "redis.*healthy"; then
            log_success "Serviços base inicializados"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    if [ $elapsed -ge $timeout ]; then
        log_error "Timeout aguardando serviços base"
        "$DOCKER_COMPOSE" logs db redis
        return 1
    fi
    
    # Inicia Ollama primeiro e verifica
    log "Iniciando Ollama..."
    if ! "$DOCKER_COMPOSE" up -d --force-recreate ollama &>> "$LOG_FILE"; then
        log_error "Falha ao iniciar Ollama"
        "$DOCKER_COMPOSE" logs ollama
        return 1
    fi
    
    # Verifica e baixa modelo do Ollama
    if ! check_ollama_model; then
        log_error "Falha ao verificar/baixar modelo do Ollama"
        return 1
    fi
    
    while [ $retry_count -lt $RETRY_LIMIT ]; do
        # Garante arquivo de dados do ETL ANTES de cada tentativa
        if [ ! -f "${PROJECT_ROOT}/data/raw/data-set-financeiro-siog.csv" ]; then
            if [ -f "${PROJECT_ROOT}/etl_service/data/raw/data-set-financeiro-siog.csv" ]; then
                cp "${PROJECT_ROOT}/etl_service/data/raw/data-set-financeiro-siog.csv" "${PROJECT_ROOT}/data/raw/"
                log_success "Arquivo de dados do ETL copiado para data/raw/ (tentativa $((retry_count+1)))"
            else
                log_error "Arquivo de dados do ETL não encontrado em etl_service/data/raw/ nem em data/raw/!"
                exit 1
            fi
        fi
        
        log "Tentativa $((retry_count + 1)) de $RETRY_LIMIT de iniciar serviços..."
        
        # Inicia serviços em ordem (ignorando MCPs por enquanto)
        local services=(
            "backend"
            "frontend"
            "jupyter"
            "ml-service"
            "etl-service"
            "mcp-memory-service"
            "mcp-chatbot-service"
            "model-server"
        )
        
        # Adicionar PgAdmin e Signoz se flags estiverem ativas
        if [ "$START_PGADMIN" = true ]; then
            services+=("pgadmin")
        fi
        if [ "$START_SIGNOZ" = true ]; then
            services+=("signoz")
        fi
        
        local failed_services=()
        for service in "${services[@]}"; do
            log "Iniciando $service..."
            if ! "$DOCKER_COMPOSE" up -d --build "$service" &>> "$LOG_FILE"; then
                log_error "Falha ao iniciar $service"
                "$DOCKER_COMPOSE" logs "$service" | tail -n 50
                failed_services+=("$service")
                break
            fi
            
            # Aguarda um pouco para o serviço inicializar
            sleep 5
            
            # Verifica se o serviço está rodando e saudável
            local health_status
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "biuai-${service}" 2>/dev/null)
            
            if [ "$?" -eq 0 ] && [ "$health_status" = "healthy" ]; then
                log_success "$service iniciado e saudável"
            else
                # Para alguns serviços, apenas verifica se está rodando
                if "$DOCKER_COMPOSE" ps "$service" | grep -q "Up"; then
                    log_success "$service iniciado"
                else
                    log_error "$service não está rodando"
                    "$DOCKER_COMPOSE" logs "$service" | tail -n 50
                    failed_services+=("$service")
                    break
                fi
            fi
        done
        
        # Se algum serviço falhou, tenta novamente
        if [ ${#failed_services[@]} -ne 0 ]; then
            log_error "Serviços que falharam: ${failed_services[*]}"
            
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $RETRY_LIMIT ]; then
                log_warning "Parando todos os serviços para nova tentativa..."
                "$DOCKER_COMPOSE" down --remove-orphans &>> "$LOG_FILE"
                sleep 10
                continue
            fi
        else
            log_success "Todos os serviços principais iniciados com sucesso"
            return 0
        fi
    done
    
    log_error "Falha ao iniciar serviços após $RETRY_LIMIT tentativas"
    log_error "Últimas linhas dos logs:"
    "$DOCKER_COMPOSE" logs --tail=50
    return 1
}

# Função para verificar saúde dos serviços
check_services_health() {
    log "Verificando saúde dos serviços..."
    local start_time=$(date +%s)
    local backend_port=8000
    if grep -q '"3000:3000"' "$PROJECT_ROOT/docker-compose.prod.yml" 2>/dev/null; then
        backend_port=3000
    fi
    local services_health=(
        "backend:${backend_port}/api/v1/health"
        "frontend:8080"
        "mcp-memory-service:8001/health"
        "mcp-chatbot-service:8002/health"
        "ml_service:8003/health"
        "jupyter:8888"
    )
    if [ "$START_PGADMIN" = true ]; then
        services_health+=("pgadmin:5050")
    fi
    if [ "$START_SIGNOZ" = true ]; then
        services_health+=("signoz:8081")
    fi
    
    while true; do
        local all_healthy=true
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $HEALTHCHECK_TIMEOUT ]; then
            log_error "Timeout ao verificar saúde dos serviços"
            return 1
        fi
        
        for service in "${services_health[@]}"; do
            IFS=':' read -r name port_path <<< "$service"
            if ! curl -s "http://localhost:${port_path}" &> /dev/null; then
                all_healthy=false
                break
            fi
        done
        
        if $all_healthy; then
            log_success "Todos os serviços estão saudáveis"
            return 0
        fi
        
        sleep 5
    done
}

# Função para inicializar banco de dados
init_database() {
    log "Inicializando banco de dados..."
    
    # Executa migrações
    "$DOCKER_COMPOSE" exec backend alembic upgrade head &>> "$LOG_FILE"
    if [ $? -ne 0 ]; then
        log_error "Falha ao executar migrações"
        return 1
    fi
    log_success "Migrações executadas com sucesso"
    
    # Cria usuário admin se não existir
    "$DOCKER_COMPOSE" exec backend python scripts/create_admin_user.py &>> "$LOG_FILE"
    if [ $? -ne 0 ]; then
        log_error "Falha ao criar usuário admin"
        return 1
    fi
    log_success "Usuário admin verificado/criado"
    
    # Gera dados de teste se necessário
    if [ "$ENVIRONMENT" = "development" ]; then
        "$DOCKER_COMPOSE" exec backend python scripts/generate_test_data.py &>> "$LOG_FILE"
        if [ $? -ne 0 ]; then
            log_warning "Falha ao gerar dados de teste"
        else
            log_success "Dados de teste gerados"
        fi
    fi
    
    return 0
}

# Healthcheck de containers principais
healthcheck_services() {
    local services=(backend frontend db redis jupyter mcp-memory-service mcp-chatbot-service ml-service etl-service)
    local all_healthy=true
    local failed_services=()
    for service in "${services[@]}"; do
        if [ "$service" = "etl-service" ]; then
            # Healthcheck especial para ETL (batch)
            local etl_cid=$($DOCKER_COMPOSE ps -q etl-service)
            if [ -n "$etl_cid" ]; then
                local etl_status=$(docker inspect -f '{{.State.Status}}' "$etl_cid" 2>/dev/null)
                local etl_exit_code=$(docker inspect -f '{{.State.ExitCode}}' "$etl_cid" 2>/dev/null)
                if [[ "$etl_status" == "exited" && "$etl_exit_code" == "0" ]]; then
                    log_success "etl-service finalizou com sucesso!"
                    continue  # NÃO adiciona à lista de falhas!
                elif [[ "$etl_status" == "exited" ]]; then
                    log_error "etl-service falhou (exit code $etl_exit_code)"
                    all_healthy=false
                    failed_services+=(etl-service)
                    continue
                fi
            else
                log_error "etl-service não encontrado"
                all_healthy=false
                failed_services+=(etl-service)
                continue
            fi
        fi
        # Healthcheck padrão para os demais serviços
        local status=$($DOCKER_COMPOSE ps --services --filter "status=running" | grep -w "$service")
        if [ -z "$status" ]; then
            log_error "$service não está rodando"
            all_healthy=false
            failed_services+=($service)
        else
            log_success "$service iniciado"
        fi
    done
    if [ "$all_healthy" = false ]; then
        log_error "Serviços que falharam: ${failed_services[*]}"
        return 1
    fi
    return 0
}

# Função principal
main() {
    # Cria diretório de logs se não existir
    mkdir -p "$LOG_DIR"
    
    # Exibe banner
    show_banner
    
    # Registra início no log
    log_info "Log detalhado será salvo em: $LOG_FILE"
    
    # Verifica requisitos
    if ! check_requirements; then
        log_error "Requisitos não atendidos"
        exit 1
    fi
    
    # Verifica dependências do frontend
    if ! check_frontend_deps; then
        log_error "Falha na verificação de dependências do frontend"
        exit 1
    fi
    
    # Limpa ambiente
    clean_environment
    
    # Inicia serviços
    if ! start_services; then
        log_error "Falha ao iniciar serviços após $RETRY_LIMIT tentativas"
        exit 1
    fi
    
    # Verifica saúde dos serviços
    if ! check_services_health; then
        log_error "Serviços não estão saudáveis"
        exit 1
    fi
    
    # Inicializa banco de dados
    if ! init_database; then
        log_error "Falha ao inicializar banco de dados"
        exit 1
    fi
    
    # Exibe informações de acesso
    log_success "Sistema BIUAI iniciado com sucesso!"
    log_info "Frontend: http://localhost:8080"
    log_info "Backend: http://localhost:${backend_port}"
    log_info "Jupyter: http://localhost:8888"
    log_info "MCP Memory Service: http://localhost:8001"
    log_info "MCP Chatbot Service: http://localhost:8002"
    log_info "Model Server: http://localhost:8000"
    if [ "$START_PGADMIN" = true ]; then
        log_info "PgAdmin: http://localhost:5050"
    fi
    if [ "$START_SIGNOZ" = true ]; then
        log_info "Signoz: http://localhost:8081"
    fi
    log_info "Documentação API: http://localhost:${backend_port}/docs"
    
    exit 0
}

# Executa função principal
main 

# Documentação de uso das flags
if [[ $1 == "--help" ]]; then
    echo -e "\nUso: ./scripts/start.sh [--pgadmin] [--signoz]"
    echo -e "\n  --pgadmin   Inicia o serviço PgAdmin (administração do banco)"
    echo -e "  --signoz    Inicia o serviço Signoz (monitoramento)"
    echo -e "\nExemplo: ./scripts/start.sh --pgadmin --signoz\n"
    exit 0
fi 