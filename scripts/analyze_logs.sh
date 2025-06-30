#!/bin/bash

# Configurações
LOGS_DIR="./logs"
REPORTS_DIR="./reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORTS_DIR/analysis_${TIMESTAMP}.md"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Criar diretórios necessários
mkdir -p "$REPORTS_DIR"

# Função para logging
log() {
    local level=$1
    local message=$2
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} [${level}] ${message}"
}

# Função para analisar erros
analyze_errors() {
    local error_files=("$LOGS_DIR"/error_*.log)
    local total_errors=0
    local error_patterns=()
    local error_counts=()

    echo "## Análise de Erros" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    for file in "${error_files[@]}"; do
        if [ -f "$file" ]; then
            echo "### Analisando $(basename "$file")" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            echo "\`\`\`" >> "$REPORT_FILE"
            
            # Contar erros únicos
            while IFS= read -r line; do
                ((total_errors++))
                local pattern=$(echo "$line" | grep -oP '\[ERROR\]\s+\K.*' || echo "$line")
                local found=0
                
                for i in "${!error_patterns[@]}"; do
                    if [[ "${error_patterns[$i]}" == "$pattern" ]]; then
                        ((error_counts[$i]++))
                        found=1
                        break
                    fi
                done
                
                if [[ $found -eq 0 ]]; then
                    error_patterns+=("$pattern")
                    error_counts+=(1)
                fi
            done < "$file"
            
            echo "\`\`\`" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
    done

    echo "### Resumo de Erros" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Total de erros encontrados: $total_errors" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "#### Padrões de Erro Mais Comuns" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Ordenar e mostrar os erros mais comuns
    for i in "${!error_patterns[@]}"; do
        echo "- ${error_patterns[$i]}: ${error_counts[$i]} ocorrências" >> "$REPORT_FILE"
    done
}

# Função para analisar performance
analyze_performance() {
    echo "## Análise de Performance" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Analisar tempos de resposta da API
    if [ -f "$LOGS_DIR/api_"*".log" ]; then
        echo "### Tempos de Resposta da API" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "\`\`\`" >> "$REPORT_FILE"
        grep "Request completed" "$LOGS_DIR/api_"*".log" | \
            awk '{print $NF}' | \
            sort -n | \
            awk '
                BEGIN {
                    count=0
                    sum=0
                }
                {
                    count++
                    sum+=$1
                    values[count]=$1
                }
                END {
                    if(count > 0) {
                        avg=sum/count
                        if(count%2==0)
                            median=(values[count/2]+values[count/2+1])/2
                        else
                            median=values[int(count/2)+1]
                        print "Total requests: " count
                        print "Average response time: " avg " ms"
                        print "Median response time: " median " ms"
                        print "Min response time: " values[1] " ms"
                        print "Max response time: " values[count] " ms"
                    }
                }' >> "$REPORT_FILE"
        echo "\`\`\`" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
}

# Função para analisar uso de recursos
analyze_resources() {
    echo "## Análise de Recursos" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Analisar uso de memória e CPU dos containers
    echo "### Uso de Recursos por Container" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" >> "$REPORT_FILE"
    echo "\`\`\`" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Função para gerar sugestões de melhoria
generate_suggestions() {
    echo "## Sugestões de Melhoria" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Analisar padrões e gerar sugestões
    if grep -q "timeout" "$LOGS_DIR"/*.log; then
        echo "- Considerar aumentar timeouts de conexão" >> "$REPORT_FILE"
    fi
    
    if grep -q "memory" "$LOGS_DIR"/*.log; then
        echo "- Otimizar uso de memória nos containers" >> "$REPORT_FILE"
    fi
    
    if grep -q "connection refused" "$LOGS_DIR"/*.log; then
        echo "- Verificar configurações de rede entre containers" >> "$REPORT_FILE"
    fi
}

# Função principal
main() {
    log "INFO" "Iniciando análise de logs..."
    
    # Cabeçalho do relatório
    echo "# Relatório de Análise de Logs" >> "$REPORT_FILE"
    echo "Data: $(date '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # Executar análises
    analyze_errors
    analyze_performance
    analyze_resources
    generate_suggestions
    
    # Compactar logs antigos
    find "$LOGS_DIR" -name "*.log" -mtime +7 -exec gzip {} \;
    
    log "INFO" "Análise concluída. Relatório gerado em: $REPORT_FILE"
    echo -e "${GREEN}Análise concluída com sucesso!${NC}"
    echo -e "${YELLOW}Relatório disponível em: $REPORT_FILE${NC}"
}

# Executar função principal
main

exit 0 