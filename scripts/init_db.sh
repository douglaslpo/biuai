#!/bin/bash

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Iniciando setup do banco de dados...${NC}"

# Verificar se o container do banco está rodando
if ! docker-compose ps | grep -q "db.*running"; then
    echo -e "${RED}Container do banco não está rodando. Iniciando...${NC}"
    docker-compose up -d db
    
    # Aguardar banco ficar disponível
    echo -e "${YELLOW}Aguardando banco ficar disponível...${NC}"
    sleep 10
fi

# Executar migrações
echo -e "${YELLOW}Executando migrações...${NC}"
docker-compose exec -T backend alembic upgrade head

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Migrações executadas com sucesso${NC}"
else
    echo -e "${RED}✗ Erro ao executar migrações${NC}"
    exit 1
fi

# Gerar dados de teste
echo -e "${YELLOW}Gerando dados de teste...${NC}"
docker-compose exec -T backend python scripts/generate_test_data.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dados de teste gerados com sucesso${NC}"
else
    echo -e "${RED}✗ Erro ao gerar dados de teste${NC}"
    exit 1
fi

echo -e "${GREEN}Setup do banco concluído com sucesso!${NC}"
echo -e "${YELLOW}Credenciais de acesso:${NC}"
echo -e "Admin: admin@biuai.com / admin123"
echo -e "Demo: demo@demo.biuai.com / demo123" 