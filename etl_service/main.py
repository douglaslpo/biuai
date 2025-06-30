import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import datetime

# Configuração dos diretórios
DATA_DIR = "/app/data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
TEMP_DIR = os.path.join(DATA_DIR, "temp")
BACKUP_DIR = os.path.join(DATA_DIR, "backup")

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://biuai:biuai123@db:5432/biuai")
engine = create_engine(DATABASE_URL)

def criar_diretorios():
    """Cria os diretórios necessários se não existirem"""
    for dir_path in [RAW_DIR, PROCESSED_DIR, TEMP_DIR, BACKUP_DIR]:
        os.makedirs(dir_path, exist_ok=True)

def backup_arquivo(arquivo):
    """Cria backup do arquivo com timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = os.path.basename(arquivo)
    nome_backup = f"{nome_arquivo}_{timestamp}"
    destino = os.path.join(BACKUP_DIR, nome_backup)
    os.rename(arquivo, destino)
    return destino

def processar_csv():
    """Processa o arquivo CSV e carrega no banco de dados"""
    arquivo_csv = os.path.join(RAW_DIR, "data-set-financeiro-siog.csv")
    
    if not os.path.exists(arquivo_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_csv}")
    
    # Tentar diferentes encodings e delimitadores
    encodings = ['utf-8', 'latin1', 'iso-8859-1']
    delimiters = [',', ';', '\t']
    
    df = None
    error = None
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(arquivo_csv, encoding=encoding, sep=delimiter, on_bad_lines='skip')
                print(f"Arquivo lido com sucesso usando encoding={encoding} e delimiter={delimiter}")
                break
            except Exception as e:
                error = e
                continue
        if df is not None:
            break
    
    if df is None:
        raise Exception(f"Não foi possível ler o arquivo CSV. Último erro: {error}")
    
    # Processar dados
    if 'data_lancamento' in df.columns:
        df['data_lancamento'] = pd.to_datetime(df['data_lancamento'], errors='coerce')
    
    # Remover linhas com valores nulos
    df = df.dropna(how='all')
    
    # Salvar versão processada
    arquivo_processado = os.path.join(PROCESSED_DIR, f"dados_processados_{datetime.now().strftime('%Y%m%d')}.csv")
    df.to_csv(arquivo_processado, index=False)
    
    # Carregar no banco de dados
    df.to_sql('lancamentos_financeiros', engine, if_exists='replace', index=False)
    
    # Fazer backup do arquivo original
    backup_arquivo(arquivo_csv)
    
    return len(df)

def main():
    """Função principal do ETL"""
    try:
        criar_diretorios()
        registros = processar_csv()
        print(f"ETL concluído com sucesso! {registros} registros processados.")
    except Exception as e:
        print(f"Erro durante o ETL: {str(e)}")
        raise

if __name__ == "__main__":
    main() 