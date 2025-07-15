"""
Serviço de análise de FIIs usando IA.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Dict, Any
import json
import requests
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import ta

class FIIAnalyzer:
    def __init__(self):
        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
        self.embeddings = {}
        self.fii_data = {}
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def analyze_fii(self, fii_data: Dict[str, Any], historical_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analisa um FII usando IA para gerar insights e recomendações.
        """
        # Análise básica
        basic_analysis = {
            'recomendacao': self._get_recommendation(fii_data),
            'pontos_fortes': self._get_strengths(fii_data),
            'pontos_atencao': self._get_attention_points(fii_data),
            'analise_ia': self._generate_analysis_text(fii_data),
            'score_confianca': self._calculate_confidence(fii_data)
        }
        
        # Análise técnica se houver dados históricos
        if historical_data:
            df = pd.DataFrame(historical_data)
            df['data'] = pd.to_datetime(df['data'])
            df = df.sort_values('data')
            
            technical = self._analyze_technical_indicators(df)
            basic_analysis.update(technical)
            
            # Previsão de preços
            price_prediction = self._predict_prices(df)
            basic_analysis['previsao_precos'] = price_prediction
            
            # Análise de tendência
            trend_analysis = self._analyze_trend(df)
            basic_analysis['analise_tendencia'] = trend_analysis
            
            # Atualiza recomendação e confiança com dados técnicos
            basic_analysis['recomendacao'] = self._combine_recommendations(
                basic_analysis['recomendacao'],
                technical['recomendacao_tecnica']
            )
            basic_analysis['score_confianca'] = (
                basic_analysis['score_confianca'] + technical['score_confianca_tecnica']
            ) / 2
        
        return basic_analysis
    
    def find_similar_fiis(self, fii_code: str, n: int = 5) -> List[Dict[str, Any]]:
        """
        Encontra FIIs similares usando embeddings e similaridade de cosseno.
        """
        if fii_code not in self.embeddings:
            self._update_embeddings()
            
        target_embedding = self.embeddings[fii_code]
        similarities = {}
        
        for code, embedding in self.embeddings.items():
            if code != fii_code:
                sim = cosine_similarity([target_embedding], [embedding])[0][0]
                similarities[code] = sim
                
        similar_codes = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:n]
        return [self.fii_data[code] for code, _ in similar_codes]
    
    def _get_recommendation(self, fii: Dict[str, Any]) -> str:
        """
        Gera uma recomendação baseada em múltiplos fatores.
        """
        score = 0
        
        # Análise de preço em relação ao valor patrimonial (P/VP)
        pvp = fii['preco_atual'] / fii['valor_patrimonial']
        if pvp < 0.9:
            score += 2  # Subavaliado
        elif pvp > 1.2:
            score -= 1  # Sobreavaliado
            
        # Análise do DY
        if fii['dividend_yield'] > 0.8:  # 8% ao ano
            score += 2
        elif fii['dividend_yield'] < 0.5:  # 5% ao ano
            score -= 1
            
        # Análise da vacância
        if fii['vacancia_media'] < 5:
            score += 1
        elif fii['vacancia_media'] > 15:
            score -= 2
            
        # Retorna recomendação baseada no score
        if score >= 2:
            return 'Compra'
        elif score <= -2:
            return 'Venda'
        return 'Manter'
    
    def _get_strengths(self, fii: Dict[str, Any]) -> List[str]:
        """
        Identifica pontos fortes do FII.
        """
        strengths = []
        
        if fii['dividend_yield'] > 0.8:
            strengths.append(f"Dividend Yield atrativo de {fii['dividend_yield']*100:.1f}% ao ano")
            
        if fii['vacancia_media'] < 5:
            strengths.append(f"Baixa vacância média de {fii['vacancia_media']:.1f}%")
            
        pvp = fii['preco_atual'] / fii['valor_patrimonial']
        if pvp < 0.9:
            strengths.append(f"Negociado abaixo do valor patrimonial (P/VP: {pvp:.2f})")
            
        if fii['patrimonio_liquido'] > 1_000_000_000:
            strengths.append("Patrimônio líquido robusto acima de R$ 1 bilhão")
            
        return strengths
    
    def _get_attention_points(self, fii: Dict[str, Any]) -> List[str]:
        """
        Identifica pontos de atenção do FII.
        """
        points = []
        
        if fii['dividend_yield'] < 0.5:
            points.append(f"Dividend Yield abaixo da média ({fii['dividend_yield']*100:.1f}% ao ano)")
            
        if fii['vacancia_media'] > 15:
            points.append(f"Alta vacância média de {fii['vacancia_media']:.1f}%")
            
        pvp = fii['preco_atual'] / fii['valor_patrimonial']
        if pvp > 1.2:
            points.append(f"Negociado acima do valor patrimonial (P/VP: {pvp:.2f})")
            
        return points
    
    def _generate_analysis_text(self, fii: Dict[str, Any]) -> str:
        """
        Gera texto de análise detalhada do FII.
        """
        pvp = fii['preco_atual'] / fii['valor_patrimonial']
        
        analysis = f"O {fii['codigo']} é um FII do segmento de {fii['segmento'].lower()} "
        analysis += f"com patrimônio líquido de R$ {fii['patrimonio_liquido']/1_000_000:.1f} milhões. "
        
        if pvp < 0.9:
            analysis += "Está sendo negociado com desconto em relação ao seu valor patrimonial, "
            analysis += "o que pode representar uma oportunidade de entrada. "
        elif pvp > 1.2:
            analysis += "Está sendo negociado com prêmio significativo em relação ao seu valor patrimonial, "
            analysis += "o que exige atenção do investidor. "
            
        analysis += f"O dividend yield atual de {fii['dividend_yield']*100:.1f}% ao ano "
        if fii['dividend_yield'] > 0.8:
            analysis += "está acima da média do mercado. "
        elif fii['dividend_yield'] < 0.5:
            analysis += "está abaixo da média do mercado. "
        else:
            analysis += "está em linha com a média do mercado. "
            
        return analysis
    
    def _calculate_confidence(self, fii: Dict[str, Any]) -> float:
        """
        Calcula o nível de confiança da análise (0-100).
        """
        confidence = 70  # Base confidence
        
        # Ajusta confiança baseado na qualidade dos dados
        if fii['patrimonio_liquido'] > 1_000_000_000:
            confidence += 10  # Mais dados disponíveis para FIIs grandes
            
        # Reduz confiança se houver dados muito voláteis
        if fii['vacancia_media'] > 20:
            confidence -= 15
            
        return min(100, max(0, confidence))
    
    def _update_embeddings(self):
        """
        Atualiza os embeddings dos FIIs para busca de similaridade.
        """
        for code, fii in self.fii_data.items():
            text = f"{fii['codigo']} {fii['nome']} {fii['segmento']} "
            text += f"patrimônio {fii['patrimonio_liquido']} "
            text += f"dy {fii['dividend_yield']} "
            text += f"vacância {fii['vacancia_media']}"
            
            self.embeddings[code] = self.model.encode(text)
            
    def update_fii_data(self, fiis_data: List[Dict[str, Any]]):
        """
        Atualiza os dados dos FIIs no analisador.
        """
        self.fii_data = {fii['codigo']: fii for fii in fiis_data}
        self._update_embeddings()
        
    async def get_market_sentiment(self, fii_code: str) -> Dict[str, Any]:
        """
        Analisa o sentimento do mercado usando o Ollama.
        """
        prompt = f"""
        Analise o FII {fii_code} considerando:
        1. Tendência de mercado
        2. Perspectivas do segmento
        3. Riscos principais
        4. Oportunidades
        
        Responda em formato JSON com os campos:
        - sentiment: "positivo", "neutro" ou "negativo"
        - confidence: número de 0 a 100
        - analysis: texto explicativo
        """
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': prompt,
                    'format': 'json'
                }
            )
            return json.loads(response.text)
        except:
            return {
                'sentiment': 'neutro',
                'confidence': 50,
                'analysis': 'Não foi possível analisar o sentimento do mercado.'
            }
            
    async def predict_dividend_yield(self, fii_code: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prevê o Dividend Yield futuro usando dados históricos.
        """
        if len(historical_data) < 12:
            return {
                'prediction': None,
                'confidence': 0,
                'explanation': 'Dados históricos insuficientes para previsão'
            }
            
        # Converte dados históricos para DataFrame
        df = pd.DataFrame(historical_data)
        df['data'] = pd.to_datetime(df['data'])
        df = df.sort_values('data')
        
        # Calcula média móvel e tendência
        df['ma_3m'] = df['dividend_yield'].rolling(3).mean()
        df['ma_6m'] = df['dividend_yield'].rolling(6).mean()
        
        last_dy = df['dividend_yield'].iloc[-1]
        trend_3m = df['ma_3m'].iloc[-1] - df['ma_3m'].iloc[-3]
        trend_6m = df['ma_6m'].iloc[-1] - df['ma_6m'].iloc[-6]
        
        # Prevê próximo DY
        if trend_3m > 0 and trend_6m > 0:
            prediction = last_dy * 1.05  # Tendência de alta
            confidence = 80
        elif trend_3m < 0 and trend_6m < 0:
            prediction = last_dy * 0.95  # Tendência de baixa
            confidence = 80
        else:
            prediction = last_dy  # Tendência lateral
            confidence = 60
            
        return {
            'prediction': prediction,
            'confidence': confidence,
            'explanation': self._generate_dy_prediction_explanation(trend_3m, trend_6m)
        }
        
    def _generate_dy_prediction_explanation(self, trend_3m: float, trend_6m: float) -> str:
        """
        Gera explicação para a previsão de DY.
        """
        if trend_3m > 0 and trend_6m > 0:
            return "Tendência de alta nos dividendos, sustentada tanto no curto quanto no médio prazo"
        elif trend_3m < 0 and trend_6m < 0:
            return "Tendência de queda nos dividendos, observada em ambos horizontes temporais"
        elif trend_3m > 0:
            return "Tendência de alta no curto prazo, mas instável no médio prazo"
        elif trend_6m > 0:
            return "Tendência de alta no médio prazo, mas com oscilações recentes"
        else:
            return "Cenário incerto, sem tendência clara de dividendos"
    
    def _analyze_technical_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calcula e analisa indicadores técnicos.
        """
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(df['preco_fechamento']).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['preco_fechamento'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['preco_fechamento'])
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_low'] = bollinger.bollinger_lband()
        
        # Análise dos indicadores
        last_rsi = df['rsi'].iloc[-1]
        last_macd = df['macd'].iloc[-1]
        last_signal = df['macd_signal'].iloc[-1]
        last_price = df['preco_fechamento'].iloc[-1]
        last_bb_high = df['bb_high'].iloc[-1]
        last_bb_low = df['bb_low'].iloc[-1]
        
        # Pontuação técnica
        score = 0
        signals = []
        
        # RSI
        if last_rsi < 30:
            score += 2
            signals.append("RSI indica sobrevendido")
        elif last_rsi > 70:
            score -= 2
            signals.append("RSI indica sobrecomprado")
            
        # MACD
        if last_macd > last_signal:
            score += 1
            signals.append("MACD indica tendência de alta")
        else:
            score -= 1
            signals.append("MACD indica tendência de baixa")
            
        # Bollinger Bands
        if last_price < last_bb_low:
            score += 2
            signals.append("Preço abaixo da banda inferior de Bollinger")
        elif last_price > last_bb_high:
            score -= 2
            signals.append("Preço acima da banda superior de Bollinger")
            
        # Determina recomendação técnica
        if score >= 2:
            rec_tecnica = "COMPRA"
        elif score <= -2:
            rec_tecnica = "VENDA"
        else:
            rec_tecnica = "NEUTRO"
            
        return {
            'rsi': last_rsi,
            'macd': last_macd,
            'bb_superior': last_bb_high,
            'bb_inferior': last_bb_low,
            'sinais_tecnicos': signals,
            'recomendacao_tecnica': rec_tecnica,
            'score_confianca_tecnica': 70 + (abs(score) * 5)  # 70-100
        }
        
    def _predict_prices(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Prevê preços futuros usando machine learning.
        """
        # Prepara features
        df['returns'] = df['preco_fechamento'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['ma_20'] = df['preco_fechamento'].rolling(window=20).mean()
        df['ma_50'] = df['preco_fechamento'].rolling(window=50).mean()
        
        # Features para o modelo
        features = ['returns', 'volatility', 'ma_20', 'ma_50', 'volume']
        target = 'preco_fechamento'
        
        # Remove NaN
        df = df.dropna()
        
        # Prepara dados de treino
        X = df[features].values
        y = df[target].values
        
        # Normaliza dados
        X_scaled = self.scaler.fit_transform(X)
        
        # Treina modelo
        self.rf_model.fit(X_scaled, y)
        
        # Prepara dados para previsão
        last_data = X_scaled[-1:]
        
        # Faz previsões para próximos 30 dias
        predictions = []
        current_data = last_data.copy()
        last_price = y[-1]
        
        for i in range(30):
            pred_price = self.rf_model.predict(current_data)[0]
            predictions.append(pred_price)
            
            # Atualiza features para próxima previsão
            returns = (pred_price - last_price) / last_price
            volatility = np.std(predictions[-20:]) if i >= 19 else df['volatility'].iloc[-1]
            ma_20 = np.mean(predictions[-20:]) if i >= 19 else df['ma_20'].iloc[-1]
            ma_50 = np.mean(predictions[-50:]) if i >= 49 else df['ma_50'].iloc[-1]
            volume = df['volume'].mean()
            
            current_data = self.scaler.transform([[returns, volatility, ma_20, ma_50, volume]])
            last_price = pred_price
            
        return {
            'precos_30d': predictions,
            'variacao_prevista': ((predictions[-1] - last_price) / last_price) * 100,
            'confianca_previsao': self._calculate_prediction_confidence(df, predictions)
        }
        
    def _analyze_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analisa tendência de preços e volumes.
        """
        # Calcula médias móveis
        df['ma_20'] = df['preco_fechamento'].rolling(window=20).mean()
        df['ma_50'] = df['preco_fechamento'].rolling(window=50).mean()
        df['ma_200'] = df['preco_fechamento'].rolling(window=200).mean()
        
        # Últimos valores
        last_price = df['preco_fechamento'].iloc[-1]
        last_ma20 = df['ma_20'].iloc[-1]
        last_ma50 = df['ma_50'].iloc[-1]
        last_ma200 = df['ma_200'].iloc[-1]
        
        # Analisa tendências
        tendencias = []
        
        # Tendência de curto prazo (MA20)
        if last_price > last_ma20:
            tendencias.append("Alta no curto prazo")
        else:
            tendencias.append("Baixa no curto prazo")
            
        # Tendência de médio prazo (MA50)
        if last_price > last_ma50:
            tendencias.append("Alta no médio prazo")
        else:
            tendencias.append("Baixa no médio prazo")
            
        # Tendência de longo prazo (MA200)
        if last_price > last_ma200:
            tendencias.append("Alta no longo prazo")
        else:
            tendencias.append("Baixa no longo prazo")
            
        # Analisa força da tendência
        preco_var_20d = ((last_price - df['preco_fechamento'].iloc[-20]) / df['preco_fechamento'].iloc[-20]) * 100
        volume_var_20d = ((df['volume'].iloc[-1] - df['volume'].iloc[-20]) / df['volume'].iloc[-20]) * 100
        
        return {
            'tendencias': tendencias,
            'forca_tendencia': self._calculate_trend_strength(preco_var_20d, volume_var_20d),
            'variacao_20d': preco_var_20d,
            'variacao_volume_20d': volume_var_20d
        }
        
    def _calculate_prediction_confidence(self, df: pd.DataFrame, predictions: List[float]) -> float:
        """
        Calcula confiança da previsão baseado na volatilidade e qualidade dos dados.
        """
        # Base confidence
        confidence = 70
        
        # Ajusta baseado na volatilidade
        volatility = df['preco_fechamento'].pct_change().std() * 100
        if volatility > 5:
            confidence -= 20
        elif volatility > 3:
            confidence -= 10
            
        # Ajusta baseado no volume de dados
        if len(df) > 200:
            confidence += 10
        elif len(df) < 50:
            confidence -= 20
            
        # Ajusta baseado na consistência das previsões
        pred_volatility = np.std(predictions) / np.mean(predictions) * 100
        if pred_volatility > 10:
            confidence -= 15
            
        return min(100, max(0, confidence))
        
    def _calculate_trend_strength(self, price_var: float, volume_var: float) -> str:
        """
        Calcula força da tendência baseado na variação de preço e volume.
        """
        # Pontuação base
        score = 0
        
        # Analisa variação de preço
        if abs(price_var) > 10:
            score += 2
        elif abs(price_var) > 5:
            score += 1
            
        # Analisa variação de volume
        if volume_var > 50:
            score += 2
        elif volume_var > 20:
            score += 1
            
        # Determina força
        if score >= 3:
            return "FORTE"
        elif score >= 1:
            return "MODERADA"
        else:
            return "FRACA"
            
    def _combine_recommendations(self, fund_rec: str, tech_rec: str) -> str:
        """
        Combina recomendações fundamentalista e técnica.
        """
        # Mapeia recomendações para scores
        rec_scores = {
            'COMPRA': 1,
            'MANTER': 0,
            'VENDA': -1,
            'NEUTRO': 0
        }
        
        # Calcula score combinado
        combined_score = rec_scores[fund_rec] + rec_scores[tech_rec]
        
        # Determina recomendação final
        if combined_score >= 1:
            return 'COMPRA'
        elif combined_score <= -1:
            return 'VENDA'
        return 'MANTER' 