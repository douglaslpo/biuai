#!/bin/bash

# Script para configurar e inicializar o Ollama
# Este script deve ser executado após o docker-compose up

echo "🤖 Configurando Ollama para o Bi UAI Bot Administrador..."

# Aguardar o serviço ollama estar disponível
echo "⏳ Aguardando Ollama estar online..."
max_attempts=30
attempts=0

while [ $attempts -lt $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama está online!"
        break
    fi
    
    attempts=$((attempts + 1))
    echo "   Tentativa $attempts/$max_attempts..."
    sleep 5
done

if [ $attempts -eq $max_attempts ]; then
    echo "❌ Ollama não ficou disponível após 150 segundos"
    echo "   Verifique se o serviço está rodando: docker-compose ps ollama"
    exit 1
fi

# Verificar modelos disponíveis
echo "📋 Verificando modelos disponíveis..."
available_models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | cut -d'"' -f4)

if echo "$available_models" | grep -q "llama3.2:3b"; then
    echo "✅ Modelo llama3.2:3b já está disponível"
else
    echo "📥 Baixando modelo llama3.2:3b (isso pode demorar alguns minutos)..."
    
    # Baixar o modelo
    curl -X POST http://localhost:11434/api/pull \
         -H "Content-Type: application/json" \
         -d '{"name": "llama3.2:3b"}' \
         --progress-bar
    
    if [ $? -eq 0 ]; then
        echo "✅ Modelo llama3.2:3b baixado com sucesso!"
    else
        echo "❌ Erro ao baixar o modelo llama3.2:3b"
        exit 1
    fi
fi

# Testar o modelo
echo "🧪 Testando o modelo..."
test_response=$(curl -s -X POST http://localhost:11434/api/generate \
                -H "Content-Type: application/json" \
                -d '{
                    "model": "llama3.2:3b",
                    "prompt": "Olá, responda apenas: Teste OK",
                    "stream": false,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 10
                    }
                }')

if echo "$test_response" | grep -q "response"; then
    echo "✅ Modelo testado com sucesso!"
    echo "   Resposta de teste: $(echo "$test_response" | grep -o '"response":"[^"]*"' | cut -d'"' -f4)"
else
    echo "❌ Erro ao testar o modelo"
    echo "   Resposta: $test_response"
    exit 1
fi

# Verificar espaço em disco
echo "💾 Verificando espaço em disco..."
disk_usage=$(df -h | grep -E "/$|/var" | head -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -gt 90 ]; then
    echo "⚠️  Atenção: Uso de disco acima de 90% ($disk_usage%)"
    echo "   Considere liberar espaço para melhor performance"
else
    echo "✅ Espaço em disco OK ($disk_usage% usado)"
fi

# Verificar memória
echo "🧠 Verificando memória disponível..."
total_mem=$(free -h | grep "^Mem:" | awk '{print $2}')
available_mem=$(free -h | grep "^Mem:" | awk '{print $7}')
echo "   Memória total: $total_mem"
echo "   Memória disponível: $available_mem"

# Status final
echo ""
echo "🎉 Configuração do Ollama concluída!"
echo ""
echo "📊 Status dos Serviços:"
echo "   • Ollama: ✅ Online (http://localhost:11434)"
echo "   • Modelo: ✅ llama3.2:3b disponível"
echo "   • MCP Chatbot: 🔄 Verificando..."

# Verificar se o serviço MCP Chatbot está rodando
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   • MCP Chatbot: ✅ Online (http://localhost:8002)"
else
    echo "   • MCP Chatbot: ⏳ Aguardando inicialização..."
fi

echo ""
echo "🚀 Bi UAI Bot Administrador está pronto para uso!"
echo ""
echo "💡 Dicas:"
echo "   • Acesse o sistema BIUAI e clique no ícone do bot no canto inferior direito"
echo "   • Admins podem gerenciar o bot em: /admin/chatbot"
echo "   • Para logs do chatbot: docker-compose logs -f mcp-chatbot-service"
echo "   • Para logs do Ollama: docker-compose logs -f ollama"
echo "" 