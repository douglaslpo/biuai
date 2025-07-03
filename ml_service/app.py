from flask import Flask, request, jsonify
from prophet import Prophet
from sklearn.ensemble import IsolationForest
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import joblib
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Configuração dos diretórios
DATA_DIR = "/app/data"
MODELS_DIR = "/app/models"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://biuai:biuai123@db:5432/biuai")
engine = create_engine(DATABASE_URL)

# Criar diretório de modelos se não existir
os.makedirs(MODELS_DIR, exist_ok=True)

class MLService:
    def __init__(self):
        self.prophet_model = None
        self.anomaly_detector = None
        self.prophet_path = os.path.join(MODELS_DIR, "prophet_model.json")
        self.anomaly_path = os.path.join(MODELS_DIR, "anomaly_detector.joblib")
        
    def treinar_prophet(self, dados):
        """Treina modelo Prophet para previsão de séries temporais"""
        df = pd.DataFrame({
            'ds': dados['data_lancamento'],
            'y': dados['valor']
        })
        
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        self.prophet_model.fit(df)
        
        # Salvar modelo
        self.prophet_model.save(self.prophet_path)
        
    def prever_valores(self, periodos=30):
        """Realiza previsões com o modelo Prophet"""
        if self.prophet_model is None:
            if os.path.exists(self.prophet_path):
                self.prophet_model = Prophet.load(self.prophet_path)
            else:
                raise Exception("Modelo Prophet não encontrado. Execute o treinamento primeiro.")
                
        future = self.prophet_model.make_future_dataframe(periods=periodos)
        forecast = self.prophet_model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    
    def treinar_anomaly_detector(self, dados):
        """Treina detector de anomalias"""
        X = dados[['valor']].values
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.anomaly_detector.fit(X)
        
        # Salvar modelo
        joblib.dump(self.anomaly_detector, self.anomaly_path)
    
    def detectar_anomalias(self, dados):
        """Detecta anomalias nos dados"""
        if self.anomaly_detector is None:
            if os.path.exists(self.anomaly_path):
                self.anomaly_detector = joblib.load(self.anomaly_path)
            else:
                raise Exception("Modelo de detecção de anomalias não encontrado. Execute o treinamento primeiro.")
                
        X = dados[['valor']].values
        predictions = self.anomaly_detector.predict(X)
        return predictions

ml_service = MLService()

@app.route('/')
def root():
    return jsonify({"message": "ML Service v1.0.0"}), 200

@app.route('/treinar', methods=['POST'])
def treinar():
    try:
        # Carregar dados do banco
        query = "SELECT data_lancamento, valor FROM lancamentos_financeiros"
        dados = pd.read_sql(query, engine)
        
        # Treinar modelos
        ml_service.treinar_prophet(dados)
        ml_service.treinar_anomaly_detector(dados)
        
        # Salvar dados processados
        arquivo_processado = os.path.join(PROCESSED_DIR, f"dados_ml_{datetime.now().strftime('%Y%m%d')}.csv")
        dados.to_csv(arquivo_processado, index=False)
        
        return jsonify({"message": "Modelos treinados com sucesso!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/prever', methods=['GET'])
def prever():
    try:
        periodos = request.args.get('periodos', default=30, type=int)
        previsoes = ml_service.prever_valores(periodos)
        return jsonify(previsoes.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/anomalias', methods=['POST'])
def detectar_anomalias():
    try:
        dados = pd.DataFrame(request.json)
        anomalias = ml_service.detectar_anomalias(dados)
        return jsonify({"anomalias": anomalias.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        # Aqui você implementará a lógica de predição
        # Por enquanto, vamos retornar uma resposta simulada
        prediction = {
            "previsao_receitas": 5000.00,
            "previsao_despesas": 3000.00,
            "tendencia": "crescimento",
            "confianca": 0.85
        }
        
        return jsonify(prediction), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 