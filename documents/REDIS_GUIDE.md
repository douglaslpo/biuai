# Guia de Acesso ao Redis

## Método 1: Acessar via Docker
```bash
# Entrar no Redis CLI
docker-compose exec redis redis-cli

# Testar conexão
ping
# Deve responder com "PONG"
```

## Método 2: Acessar via Host
Se você tiver o redis-cli instalado localmente:
```bash
redis-cli -h localhost -p 6379
```

## Comandos Básicos do Redis

### Testar Conexão
```bash
ping
```

### Operações com Strings
```bash
# Definir um valor
SET chave valor

# Obter um valor
GET chave

# Verificar se existe
EXISTS chave
```

### Operações com Listas
```bash
# Adicionar elementos
LPUSH lista valor
RPUSH lista valor

# Obter elementos
LRANGE lista 0 -1
```

### Operações com Sets
```bash
# Adicionar elementos
SADD set valor

# Listar elementos
SMEMBERS set
```

### Operações com Hashes
```bash
# Definir campo
HSET hash campo valor

# Obter campo
HGET hash campo

# Obter todos os campos
HGETALL hash
```

### Comandos de Administração
```bash
# Listar todas as chaves
KEYS *

# Limpar todas as chaves
FLUSHALL

# Informações do servidor
INFO

# Estatísticas de memória
INFO memory
```

### Sair do Redis CLI
```bash
exit
```

## Notas Importantes
1. O Redis está configurado sem senha no ambiente de desenvolvimento
2. A porta padrão é 6379
3. Os dados são persistidos no volume docker `redis_data`
4. Para produção, recomenda-se configurar senha e outras medidas de segurança 