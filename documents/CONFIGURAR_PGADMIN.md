# 🐘 Configurar Servidor PostgreSQL no PgAdmin

## 📋 Informações de Conexão

### 🔑 Credenciais do Banco BIUAI:
- **Host**: `db` (nome do container dentro da rede Docker)
- **Porta**: `5432`
- **Database**: `biuai`
- **Usuário**: `biuai`
- **Senha**: `biuai123`

### 🌐 Acesso ao PgAdmin:
- **URL**: http://localhost:5050
- **Email**: admin@biuai.com
- **Senha**: biuai123

## 📝 Passo a Passo para Adicionar Servidor

### 1. **Acessar PgAdmin**
   - Abra http://localhost:5050 no navegador
   - Faça login com: `admin@biuai.com` / `biuai123`

### 2. **Adicionar Novo Servidor**
   - Clique no botão **"Adicionar Novo Servidor"** (ícone de servidor com +)
   - Ou clique com botão direito em "Servers" → "Register" → "Server..."

### 3. **Aba General**
   ```
   Name: BIUAI PostgreSQL
   Server group: Servers
   Comments: Banco de dados do sistema BIUAI
   ```

### 4. **Aba Connection**
   ```
   Host name/address: db
   Port: 5432
   Maintenance database: biuai
   Username: biuai
   Password: biuai123
   ```

### 5. **Configurações Avançadas (Opcional)**
   - **Aba Advanced**:
     ```
     DB restriction: biuai
     ```

### 6. **Salvar Configuração**
   - Clique em **"Save"**
   - O servidor deve aparecer na lista à esquerda

## ✅ Verificação da Conexão

### 📊 Tabelas que Devem Aparecer:
Após conectar, você deve ver no banco `biuai`:

#### **Tabelas Principais:**
1. **`users`** - 1 registro (admin)
2. **`lancamentos`** - 1.008 registros 
3. **`fin_lancamentos`** - 19.768 registros (dados SIOG)
4. **`categorias`** - 6 registros
5. **`metas_financeiras`** - Vazia

#### **Tabelas de Apoio:**
6. **`glb_loja`** - 1 registro
7. **`glb_pessoa`** - Vazia
8. **`fin_banco`** - 5 registros (bancos padrão)
9. **`fin_conta`** - 1 registro
10. **`fin_naturezafinanceira`** - 9 registros
11. **`usuarios`** - Vazia

## 🔍 Consultas de Teste

### **Verificar Dados Importados:**
```sql
-- Total de lançamentos
SELECT COUNT(*) as total_lancamentos FROM lancamentos;

-- Total de dados SIOG
SELECT COUNT(*) as total_siog FROM fin_lancamentos;

-- Resumo por tipo
SELECT tipo, COUNT(*) as quantidade, SUM(ABS(valor)) as total
FROM lancamentos 
GROUP BY tipo;

-- Usuários cadastrados
SELECT id, full_name, email, is_superuser 
FROM users;
```

### **Explorar Dados SIOG:**
```sql
-- Amostra dos dados SIOG
SELECT id_lan, tp_lancamento, vl_original, dt_documento, complemento
FROM fin_lancamentos 
LIMIT 10;

-- Totais por tipo de lançamento
SELECT tp_lancamento, COUNT(*) as quantidade, SUM(vl_original) as total
FROM fin_lancamentos 
GROUP BY tp_lancamento;
```

## ❌ Solução de Problemas

### **Erro de Conexão "could not connect to server":**
1. Verifique se o container `biuai_db_1` está rodando:
   ```bash
   docker-compose ps db
   ```

2. Use `db` como hostname (não `localhost` ou `127.0.0.1`)

### **Erro de Autenticação:**
- Confirme as credenciais:
  - Usuário: `biuai`
  - Senha: `biuai123`
  - Database: `biuai`

### **Servidor não aparece:**
- Recarregue a página do PgAdmin
- Verifique se salvou corretamente as configurações

## 🚀 Comandos Docker Úteis

### **Verificar Status dos Containers:**
```bash
docker-compose ps
```

### **Ver Logs do PostgreSQL:**
```bash
docker-compose logs db
```

### **Conectar diretamente ao PostgreSQL:**
```bash
docker exec -it biuai_db_1 psql -U biuai -d biuai
```

### **Reiniciar Serviços se Necessário:**
```bash
docker-compose restart db pgadmin
```

---

**📌 Importante**: Use sempre `db` como hostname no PgAdmin, pois é o nome do container PostgreSQL dentro da rede Docker `biuai_app-network`. 