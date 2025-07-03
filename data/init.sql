-- Inicialização do banco BIUAI
-- Baseado no schema de consultaLançamentos.sql

-- Criação das tabelas principais

-- Tabela de usuários (para autenticação)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de lojas/filiais
CREATE TABLE IF NOT EXISTS glb_loja (
    id_loja SERIAL PRIMARY KEY,
    nm_fantasia VARCHAR(255),
    razao_social VARCHAR(255) NOT NULL,
    cnpj VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de pessoas (clientes/fornecedores)
CREATE TABLE IF NOT EXISTS glb_pessoa (
    id_pessoa SERIAL PRIMARY KEY,
    nm_pessoa VARCHAR(255) NOT NULL,
    tipo_pessoa CHAR(1) CHECK (tipo_pessoa IN ('F', 'J')), -- F=Física, J=Jurídica
    cpf_cnpj VARCHAR(20),
    email VARCHAR(255),
    telefone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de bancos
CREATE TABLE IF NOT EXISTS fin_banco (
    id_banco SERIAL PRIMARY KEY,
    nm_banco VARCHAR(255) NOT NULL,
    codigo_banco VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de contas bancárias
CREATE TABLE IF NOT EXISTS fin_conta (
    id_conta SERIAL PRIMARY KEY,
    nm_conta VARCHAR(255) NOT NULL,
    id_banco INTEGER REFERENCES fin_banco(id_banco),
    numero_conta VARCHAR(50),
    agencia VARCHAR(20),
    saldo_atual DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de naturezas financeiras
CREATE TABLE IF NOT EXISTS fin_naturezafinanceira (
    id_natureza SERIAL PRIMARY KEY,
    nm_natureza VARCHAR(255) NOT NULL,
    tipo_natureza CHAR(1) CHECK (tipo_natureza IN ('R', 'D')), -- R=Receita, D=Despesa
    id_natureza_pai INTEGER REFERENCES fin_naturezafinanceira(id_natureza),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de categorias (compatível com o modelo atual)
CREATE TABLE IF NOT EXISTS categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(10) CHECK (tipo IN ('RECEITA', 'DESPESA')),
    descricao TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela principal de lançamentos financeiros
CREATE TABLE IF NOT EXISTS fin_lancamentos (
    id_lan SERIAL PRIMARY KEY,
    id_loja INTEGER REFERENCES glb_loja(id_loja),
    id_conta INTEGER REFERENCES fin_conta(id_conta),
    id_pessoa INTEGER REFERENCES glb_pessoa(id_pessoa),
    id_natureza INTEGER REFERENCES fin_naturezafinanceira(id_natureza),
    id_sub_natureza INTEGER REFERENCES fin_naturezafinanceira(id_natureza),
    tp_lancamento CHAR(1) CHECK (tp_lancamento IN ('D', 'C')), -- D=Débito, C=Crédito
    vl_original DECIMAL(15,2) NOT NULL,
    vl_baixado DECIMAL(15,2) DEFAULT 0,
    complemento TEXT,
    dt_vencimento DATE,
    dt_baixa DATE,
    dt_documento DATE,
    status_lan CHAR(1) DEFAULT '0' CHECK (status_lan IN ('0', '1', '2', '4', '5')),
    -- 0=Em aberto, 1=Baixado, 2=Cancelado, 4=Baixa Parcial, 5=Baixado por Fatura
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de lançamentos (modelo atual do sistema)
CREATE TABLE IF NOT EXISTS lancamentos (
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    valor DECIMAL(15,2) NOT NULL,
    tipo VARCHAR(10) CHECK (tipo IN ('RECEITA', 'DESPESA')),
    data_lancamento TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    categoria_id INTEGER REFERENCES categorias(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de metas financeiras
CREATE TABLE IF NOT EXISTS metas_financeiras (
    id SERIAL PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    valor_meta DECIMAL(15,2) NOT NULL,
    valor_atual DECIMAL(15,2) DEFAULT 0,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    categoria_id INTEGER REFERENCES categorias(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inserção de dados iniciais

-- Usuário administrador padrão
INSERT INTO users (full_name, email, hashed_password, is_superuser) 
VALUES ('Administrador BIUAI', 'admin@biuai.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Bancos padrão
INSERT INTO fin_banco (nm_banco, codigo_banco) VALUES 
('Banco do Brasil', '001'),
('Bradesco', '237'),
('Itaú', '341'),
('Santander', '033'),
('Caixa Econômica Federal', '104')
ON CONFLICT DO NOTHING;

-- Naturezas financeiras padrão
INSERT INTO fin_naturezafinanceira (nm_natureza, tipo_natureza) VALUES 
('Vendas', 'R'),
('Prestação de Serviços', 'R'),
('Receitas Financeiras', 'R'),
('Outras Receitas', 'R'),
('Fornecedores', 'D'),
('Salários', 'D'),
('Impostos', 'D'),
('Despesas Operacionais', 'D'),
('Despesas Financeiras', 'D')
ON CONFLICT DO NOTHING;

-- Categorias padrão
INSERT INTO categorias (nome, tipo, descricao, user_id) VALUES 
('Vendas', 'RECEITA', 'Receitas de vendas de produtos/serviços', 1),
('Investimentos', 'RECEITA', 'Rendimentos de investimentos', 1),
('Salários', 'DESPESA', 'Pagamento de salários e encargos', 1),
('Fornecedores', 'DESPESA', 'Pagamentos a fornecedores', 1),
('Marketing', 'DESPESA', 'Despesas com marketing e publicidade', 1),
('Infraestrutura', 'DESPESA', 'Despesas com infraestrutura e TI', 1)
ON CONFLICT DO NOTHING;

-- Loja padrão
INSERT INTO glb_loja (nm_fantasia, razao_social, cnpj) VALUES 
('BIUAI', 'Business Intelligence Unity with AI LTDA', '00.000.000/0001-00')
ON CONFLICT DO NOTHING;

-- Conta padrão
INSERT INTO fin_conta (nm_conta, id_banco, numero_conta, agencia) VALUES 
('Conta Principal', 1, '12345-6', '1234')
ON CONFLICT DO NOTHING;

-- Criação de índices para performance
CREATE INDEX IF NOT EXISTS idx_lancamentos_user_id ON lancamentos(user_id);
CREATE INDEX IF NOT EXISTS idx_lancamentos_data ON lancamentos(data_lancamento);
CREATE INDEX IF NOT EXISTS idx_lancamentos_tipo ON lancamentos(tipo);
CREATE INDEX IF NOT EXISTS idx_fin_lancamentos_user_id ON fin_lancamentos(user_id);
CREATE INDEX IF NOT EXISTS idx_fin_lancamentos_data ON fin_lancamentos(dt_documento);
CREATE INDEX IF NOT EXISTS idx_fin_lancamentos_status ON fin_lancamentos(status_lan); 