#!/bin/bash

# 🤖 Script de Correção Ollama - BIUAI
# Corrige problemas do container Ollama e configura modelo llama3.2:3b

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Header
echo -e "${PURPLE}"
echo "🤖 BIUAI - CORREÇÃO OLLAMA"
echo "=========================="
echo -e "${NC}"
echo ""

log "Iniciando correção do container Ollama..."

# Verificar se Docker está rodando
if ! docker ps > /dev/null 2>&1; then
    error "Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar status atual do Ollama
log "Verificando status atual do Ollama..."
OLLAMA_STATUS=$(docker-compose ps ollama 2>/dev/null | grep -E "(unhealthy|healthy|running)" || echo "not found")
info "Status atual: $OLLAMA_STATUS"

# Parar container Ollama se estiver rodando
if docker-compose ps ollama | grep -q "Up"; then
    warning "Parando container Ollama para reconfiguração..."
    docker-compose stop ollama
fi

# Remover container e volume para fresh start
log "Removendo container e dados corrompidos..."
docker-compose rm -f ollama 2>/dev/null || true
docker volume rm biuai_ollama_data 2>/dev/null || true

# Verificar recursos disponíveis
log "Verificando recursos disponíveis..."
TOTAL_RAM=$(free -g | grep "Mem:" | awk '{print $2}')
AVAILABLE_RAM=$(free -g | grep "Mem:" | awk '{print $7}')

info "RAM Total: ${TOTAL_RAM}GB"
info "RAM Disponível: ${AVAILABLE_RAM}GB"

if [ "$AVAILABLE_RAM" -lt 3 ]; then
    warning "RAM disponível (${AVAILABLE_RAM}GB) pode ser insuficiente para Ollama"
    warning "Recomendado: pelo menos 4GB de RAM livre"
fi

# Iniciar apenas o container Ollama
log "Iniciando container Ollama..."
docker-compose up -d ollama

# Aguardar container inicializar
log "Aguardando container inicializar (60 segundos)..."
sleep 60

# Verificar se container está rodando
if ! docker-compose ps ollama | grep -q "Up"; then
    error "Container Ollama não iniciou corretamente"
    echo ""
    echo "🔍 Logs do container:"
    docker-compose logs ollama --tail=20
    exit 1
fi

log "✅ Container Ollama iniciado"

# Testar conectividade básica
log "Testando conectividade com Ollama..."
for i in {1..10}; do
    if curl -s -f http://localhost:11434/api/tags >/dev/null 2>&1; then
        log "✅ Ollama respondendo na porta 11434"
        OLLAMA_RESPONDING=true
        break
    else
        info "Tentativa $i/10 - Aguardando Ollama responder..."
        sleep 10
    fi
done

if [ "$OLLAMA_RESPONDING" != "true" ]; then
    error "Ollama não está respondendo após 100 segundos"
    echo ""
    echo "🔍 Logs recentes:"
    docker-compose logs ollama --tail=30
    echo ""
    echo "💡 Possíveis soluções:"
    echo "1. Reiniciar Docker: sudo systemctl restart docker"
    echo "2. Liberar mais RAM fechando aplicações"
    echo "3. Verificar se porta 11434 não está em uso: netstat -tlnp | grep 11434"
    exit 1
fi

# Baixar modelo llama3.2:3b
log "Baixando modelo llama3.2:3b (pode demorar alguns minutos)..."
docker-compose exec ollama ollama pull llama3.2:3b

if [ $? -eq 0 ]; then
    log "✅ Modelo llama3.2:3b baixado com sucesso"
else
    warning "Erro ao baixar modelo. Tentando modelo menor..."
    docker-compose exec ollama ollama pull llama3.2:1b
    
    if [ $? -eq 0 ]; then
        log "✅ Modelo llama3.2:1b baixado como alternativa"
    else
        error "Falha ao baixar qualquer modelo"
        exit 1
    fi
fi

# Listar modelos disponíveis
log "Listando modelos disponíveis..."
docker-compose exec ollama ollama list

# Testar o modelo
log "Testando modelo com pergunta simples..."
TEST_RESPONSE=$(docker-compose exec ollama ollama run llama3.2:3b "Olá, você está funcionando?" 2>/dev/null)

if [ -n "$TEST_RESPONSE" ]; then
    log "✅ Modelo respondeu corretamente"
    info "Resposta: ${TEST_RESPONSE:0:100}..."
else
    warning "Modelo não respondeu, mas container está rodando"
fi

# Verificar health check final
log "Verificando health check final..."
sleep 30
FINAL_STATUS=$(docker-compose ps ollama | grep -E "(healthy|unhealthy)" || echo "unknown")
info "Status final: $FINAL_STATUS"

echo ""
if echo "$FINAL_STATUS" | grep -q "healthy"; then
    echo -e "${GREEN}🎉 CORREÇÃO OLLAMA CONCLUÍDA COM SUCESSO!${NC}"
    echo ""
    echo -e "${GREEN}✅ Status: HEALTHY${NC}"
    echo -e "${GREEN}✅ Modelo: llama3.2:3b disponível${NC}"
    echo -e "${GREEN}✅ API: Respondendo na porta 11434${NC}"
    echo ""
    echo -e "${BLUE}🔗 URLs de Teste:${NC}"
    echo "- API Status: http://localhost:11434/api/tags"
    echo "- Modelo: docker-compose exec ollama ollama run llama3.2:3b 'Oi'"
    echo ""
    echo -e "${BLUE}📋 Próximos Passos:${NC}"
    echo "1. Testar chatbot no frontend: http://localhost:8080"
    echo "2. Verificar funcionalidades de IA no dashboard"
    echo "3. Monitorar uso de recursos: docker stats"
else
    echo -e "${RED}❌ OLLAMA AINDA COM PROBLEMAS${NC}"
    echo ""
    echo -e "${YELLOW}🔍 Diagnóstico:${NC}"
    echo "- Container Status: $(docker-compose ps ollama | tail -1)"
    echo "- Health Check: $FINAL_STATUS"
    echo ""
    echo -e "${YELLOW}💡 Soluções Adicionais:${NC}"
    echo "1. Reiniciar sistema completo:"
    echo "   docker-compose down && docker-compose up -d"
    echo ""
    echo "2. Verificar logs detalhados:"
    echo "   docker-compose logs ollama -f"
    echo ""
    echo "3. Reduzir uso de memória:"
    echo "   # No docker-compose.yml, reduzir memory de 2G para 1G"
    echo ""
    echo "4. Usar modelo menor (apenas para teste):"
    echo "   docker-compose exec ollama ollama pull phi3:mini"
fi

echo ""
log "Script de correção Ollama finalizado" 