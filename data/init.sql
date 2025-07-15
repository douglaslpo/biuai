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

-- Dados de teste para FIIs
INSERT INTO fiis (codigo, nome, segmento, preco_atual, dividend_yield, patrimonio_liquido, valor_patrimonial, quantidade_cotas, vacancia_media, score) VALUES
('HGLG11', 'CGHG Logística', 'Logística', 160.50, 0.72, 2500000000, 105.30, 15000000, 2.5, 85),
('KNRI11', 'Kinea Renda', 'Escritórios', 142.75, 0.68, 3800000000, 98.45, 25000000, 5.8, 82),
('MXRF11', 'Maxi Renda', 'Híbrido', 10.45, 0.85, 1200000000, 9.85, 120000000, 3.2, 78),
('XPLG11', 'XP Log', 'Logística', 115.80, 0.65, 1800000000, 95.20, 18000000, 1.8, 88),
('VISC11', 'Vinci Shopping', 'Shoppings', 108.90, 0.70, 2200000000, 89.75, 22000000, 4.5, 80),
('RECT11', 'UBS Realty', 'Escritórios', 72.35, 0.75, 950000000, 68.90, 12000000, 6.2, 75),
('HSML11', 'HSI Mall', 'Shoppings', 89.60, 0.69, 1600000000, 82.15, 18000000, 3.9, 81),
('VILG11', 'Vinci Logística', 'Logística', 112.40, 0.71, 1400000000, 96.80, 14000000, 2.1, 86),
('RBRR11', 'RBR Rendimento', 'Recebíveis', 95.75, 0.82, 850000000, 92.30, 9000000, 0.0, 83),
('BTLG11', 'BTG Logística', 'Logística', 108.25, 0.67, 1900000000, 94.60, 19000000, 2.8, 84);

-- Dados históricos de preços
INSERT INTO fii_historico (fii_id, data, preco_fechamento, volume_negociado, dividend_yield) 
SELECT f.id, 
       generate_series(
           current_date - interval '365 days',
           current_date,
           interval '1 day'
       ),
       f.preco_atual * (1 + (random() * 0.1 - 0.05)),
       floor(random() * 1000000 + 50000),
       f.dividend_yield * (1 + (random() * 0.2 - 0.1))
FROM fiis f;

-- Análises de IA
INSERT INTO fii_analises (fii_id, data_analise, tipo_analise, resultado, score_confianca) 
SELECT f.id,
       generate_series(
           current_date - interval '30 days',
           current_date,
           interval '1 day'
       ),
       unnest(ARRAY['tendencia', 'risco', 'oportunidade']),
       unnest(ARRAY['alta', 'moderado', 'compra']),
       random() * 100
FROM fiis f;

-- Métricas de desempenho
INSERT INTO fii_metricas (fii_id, periodo, rentabilidade_periodo, volatilidade, sharpe_ratio, correlacao_ibov)
SELECT f.id,
       generate_series(
           current_date - interval '12 months',
           current_date,
           interval '1 month'
       ),
       random() * 0.15 - 0.05,
       random() * 0.2 + 0.1,
       random() * 2 - 0.5,
       random() * 0.6 - 0.3
FROM fiis f; 