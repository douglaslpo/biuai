#!/usr/bin/env python3
"""
Script para importar dados do CSV SIOG para o banco PostgreSQL
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os
from datetime import datetime

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'biuai',
    'user': 'biuai',
    'password': 'biuai123'
}

def connect_db():
    """Conecta ao banco PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def clean_decimal_value(value):
    """Limpa e converte valores decimais"""
    if pd.isna(value) or value == '' or value is None:
        return 0.0
    
    # Remove aspas e converte vírgula para ponto
    if isinstance(value, str):
        value = value.replace('"', '').replace(',', '.')
    
    try:
        return float(value)
    except:
        return 0.0

def clean_date_value(value):
    """Limpa e converte valores de data"""
    if pd.isna(value) or value == '' or value is None:
        return None
    
    # Remove aspas
    if isinstance(value, str):
        value = value.replace('"', '').strip()
        if value == '\\b' or value == '':
            return None
    
    try:
        # Tenta converter formato YYYY-MM-DD
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except:
        try:
            # Tenta formato DD/MM/YYYY
            return datetime.strptime(str(value), '%d/%m/%Y').date()
        except:
            return None

def import_siog_data():
    """Importa dados do CSV SIOG"""
    print("🚀 Iniciando importação dos dados SIOG...")
    
    # Caminho do arquivo CSV
    csv_path = '../backend/data/data-set-financeiro-siog.csv'
    
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        return False
    
    # Conecta ao banco
    conn = connect_db()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Lê o CSV
        print("📖 Lendo arquivo CSV...")
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        print(f"📊 Encontrados {len(df)} registros no CSV")
        
        # Limpa a tabela antes de importar
        print("🧹 Limpando dados antigos...")
        cursor.execute("DELETE FROM fin_lancamentos WHERE id_lan > 0")
        
        # Prepara os dados
        imported_count = 0
        error_count = 0
        
        print("💾 Importando dados...")
        
        for index, row in df.iterrows():
            try:
                # Limpa e converte os dados
                id_lan = int(row['id_lan']) if not pd.isna(row['id_lan']) else None
                filial = str(row['filial']).replace('"', '').strip() if not pd.isna(row['filial']) else ''
                conta = str(row['conta']).replace('"', '').strip() if not pd.isna(row['conta']) else ''
                banco = str(row['banco']).replace('"', '').strip() if not pd.isna(row['banco']) else ''
                cliente_fornecedor = str(row['cliente_fornecedor']).replace('"', '').strip() if not pd.isna(row['cliente_fornecedor']) else ''
                tipo_lancamento = 'D' if 'Saída' in str(row['tipo_lancamento']) else 'C'
                vl_original = clean_decimal_value(row['vl_original'])
                vl_baixado = clean_decimal_value(row['vl_baixado'])
                complemento = str(row['complemento']).replace('"', '').strip() if not pd.isna(row['complemento']) else ''
                dt_vencimento = clean_date_value(row['dt_vencimento'])
                dt_baixa = clean_date_value(row['dt_baixa'])
                dt_emissao = clean_date_value(row['dt_emissao'])
                nm_natureza = str(row['nm_natureza']).replace('"', '').strip() if not pd.isna(row['nm_natureza']) else ''
                sub_natureza = str(row['sub_natureza']).replace('"', '').strip() if not pd.isna(row['sub_natureza']) else ''
                status_lan = '1' if 'Baixado' in str(row['status_lan']) else '0'
                
                # Insere no banco
                insert_query = """
                INSERT INTO fin_lancamentos (
                    id_lan, id_loja, id_conta, id_pessoa, id_natureza, id_sub_natureza,
                    tp_lancamento, vl_original, vl_baixado, complemento,
                    dt_vencimento, dt_baixa, dt_documento, status_lan, user_id
                ) VALUES (
                    %s, 1, 1, NULL, NULL, NULL,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, 1
                )
                """
                
                cursor.execute(insert_query, (
                    id_lan, tipo_lancamento, vl_original, vl_baixado, complemento,
                    dt_vencimento, dt_baixa, dt_emissao, status_lan
                ))
                
                imported_count += 1
                
                if imported_count % 1000 == 0:
                    print(f"⏳ Importados {imported_count} registros...")
                    
            except Exception as e:
                error_count += 1
                if error_count <= 10:  # Mostra apenas os primeiros 10 erros
                    print(f"⚠️ Erro na linha {index + 1}: {e}")
        
        # Commit das alterações
        conn.commit()
        
        print(f"✅ Importação concluída!")
        print(f"📊 Total importado: {imported_count} registros")
        print(f"❌ Erros: {error_count} registros")
        
        # Atualiza também a tabela de lançamentos simplificada
        print("🔄 Criando lançamentos simplificados...")
        
        cursor.execute("DELETE FROM lancamentos WHERE id > 8")  # Mantém os dados de exemplo
        
        # Cria lançamentos simplificados baseados nos dados SIOG
        cursor.execute("""
        INSERT INTO lancamentos (descricao, valor, tipo, data_lancamento, user_id, categoria_id)
        SELECT 
            CASE 
                WHEN complemento != '' THEN complemento 
                ELSE 'Lançamento importado SIOG'
            END as descricao,
            CASE 
                WHEN tp_lancamento = 'D' THEN -vl_original
                ELSE vl_original
            END as valor,
            CASE 
                WHEN tp_lancamento = 'D' THEN 'DESPESA'
                ELSE 'RECEITA'
            END as tipo,
            COALESCE(dt_documento, dt_vencimento, NOW()) as data_lancamento,
            1 as user_id,
            CASE 
                WHEN tp_lancamento = 'D' THEN 4  -- Fornecedores
                ELSE 1  -- Vendas
            END as categoria_id
        FROM fin_lancamentos 
        WHERE id_lan IS NOT NULL
        LIMIT 1000  -- Limita para não sobrecarregar
        """)
        
        conn.commit()
        print("✅ Lançamentos simplificados criados!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = import_siog_data()
    sys.exit(0 if success else 1) 