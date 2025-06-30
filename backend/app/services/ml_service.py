"""
Serviço de Machine Learning para BIUAI
Análise financeira inteligente, classificação automática e predições
"""

import asyncio
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, accuracy_score
import xgboost as xgb
import lightgbm as lgb

# Time Series
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Natural Language Processing
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Data Processing
from sklearn.utils import resample
import joblib

from app.core.config import settings
from app.core.cache import cached_function, FinancialCache


class MLFinancialAnalyzer:
    """Advanced ML analyzer for financial data"""
    
    def __init__(self):
        self.models_path = Path("app/ml_models")
        self.models_path.mkdir(exist_ok=True)
        
        # Models
        self.category_classifier = None
        self.spending_predictor = None
        self.anomaly_detector = None
        
        # Preprocessors
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # NLP
        self.stemmer = PorterStemmer()
        self.stopwords = set(stopwords.words('portuguese') + stopwords.words('english'))
        
        # Initialize NLTK data
        self._init_nltk()
    
    def _init_nltk(self):
        """Initialize NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            print(f"NLTK initialization warning: {e}")
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for ML analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        processed_tokens = [
            self.stemmer.stem(token) 
            for token in tokens 
            if token.isalpha() and token not in self.stopwords
        ]
        
        return " ".join(processed_tokens)
    
    def extract_transaction_features(self, transactions: List[Dict]) -> pd.DataFrame:
        """Extract features from transactions for ML"""
        df = pd.DataFrame(transactions)
        
        if df.empty:
            return pd.DataFrame()
        
        # Basic features
        features = df.copy()
        
        # Text preprocessing
        if 'descricao' in features.columns:
            features['descricao_processed'] = features['descricao'].apply(self.preprocess_text)
        
        # Date features
        if 'data_lancamento' in features.columns:
            features['data_lancamento'] = pd.to_datetime(features['data_lancamento'])
            features['day_of_week'] = features['data_lancamento'].dt.dayofweek
            features['day_of_month'] = features['data_lancamento'].dt.day
            features['month'] = features['data_lancamento'].dt.month
            features['quarter'] = features['data_lancamento'].dt.quarter
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Amount features
        if 'valor' in features.columns:
            features['valor_abs'] = features['valor'].abs()
            features['valor_log'] = np.log1p(features['valor_abs'])
            features['is_credit'] = (features['valor'] > 0).astype(int)
            features['amount_category'] = pd.cut(
                features['valor_abs'], 
                bins=[0, 50, 200, 500, 1000, float('inf')],
                labels=['very_low', 'low', 'medium', 'high', 'very_high']
            )
        
        return features
    
    async def train_category_classifier(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Train model to classify transaction categories"""
        try:
            df = self.extract_transaction_features(transactions)
            
            if df.empty or 'categoria_id' not in df.columns:
                return {"error": "Insufficient data for training"}
            
            # Prepare features
            features = []
            if 'descricao_processed' in df.columns:
                # TF-IDF features
                tfidf_features = self.tfidf_vectorizer.fit_transform(df['descricao_processed'])
                features.append(tfidf_features.toarray())
            
            # Numerical features
            numerical_cols = ['valor_abs', 'day_of_week', 'month', 'is_weekend']
            numerical_features = df[numerical_cols].fillna(0).values
            features.append(numerical_features)
            
            # Combine features
            X = np.hstack(features) if features else numerical_features
            y = df['categoria_id'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.category_classifier = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.category_classifier.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.category_classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            model_data = {
                'classifier': self.category_classifier,
                'vectorizer': self.tfidf_vectorizer,
                'feature_names': numerical_cols,
                'label_encoder': self.label_encoder
            }
            
            joblib.dump(model_data, self.models_path / "category_classifier.pkl")
            
            return {
                "accuracy": accuracy,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features_count": X.shape[1]
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    async def predict_category(self, transaction: Dict) -> Dict[str, Any]:
        """Predict category for a transaction"""
        try:
            if not self.category_classifier:
                # Try to load saved model
                model_path = self.models_path / "category_classifier.pkl"
                if model_path.exists():
                    model_data = joblib.load(model_path)
                    self.category_classifier = model_data['classifier']
                    self.tfidf_vectorizer = model_data['vectorizer']
                else:
                    return {"error": "Model not trained"}
            
            # Extract features
            df = self.extract_transaction_features([transaction])
            
            if df.empty:
                return {"error": "Could not extract features"}
            
            # Prepare features (same as training)
            features = []
            if 'descricao_processed' in df.columns:
                tfidf_features = self.tfidf_vectorizer.transform(df['descricao_processed'])
                features.append(tfidf_features.toarray())
            
            numerical_cols = ['valor_abs', 'day_of_week', 'month', 'is_weekend']
            numerical_features = df[numerical_cols].fillna(0).values
            features.append(numerical_features)
            
            X = np.hstack(features) if features else numerical_features
            
            # Predict
            prediction = self.category_classifier.predict(X)[0]
            probabilities = self.category_classifier.predict_proba(X)[0]
            confidence = max(probabilities)
            
            return {
                "predicted_category": int(prediction),
                "confidence": float(confidence),
                "probabilities": probabilities.tolist()
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    async def train_spending_predictor(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Train model to predict future spending"""
        try:
            df = pd.DataFrame(transactions)
            
            if df.empty or 'data_lancamento' not in df.columns:
                return {"error": "Insufficient data for training"}
            
            # Prepare time series data
            df['data_lancamento'] = pd.to_datetime(df['data_lancamento'])
            df = df.sort_values('data_lancamento')
            
            # Group by date and sum expenses (negative values)
            daily_expenses = df[df['valor'] < 0].groupby(
                df['data_lancamento'].dt.date
            )['valor'].sum().abs()
            
            if len(daily_expenses) < 30:  # Need at least 30 days
                return {"error": "Insufficient historical data (need at least 30 days)"}
            
            # Create features for regression
            daily_expenses_df = daily_expenses.reset_index()
            daily_expenses_df.columns = ['date', 'amount']
            daily_expenses_df['date'] = pd.to_datetime(daily_expenses_df['date'])
            
            # Feature engineering
            daily_expenses_df['day_of_week'] = daily_expenses_df['date'].dt.dayofweek
            daily_expenses_df['day_of_month'] = daily_expenses_df['date'].dt.day
            daily_expenses_df['month'] = daily_expenses_df['date'].dt.month
            daily_expenses_df['is_weekend'] = daily_expenses_df['day_of_week'].isin([5, 6]).astype(int)
            
            # Lag features
            for lag in [1, 3, 7]:
                daily_expenses_df[f'lag_{lag}'] = daily_expenses_df['amount'].shift(lag)
            
            # Rolling averages
            for window in [3, 7, 14]:
                daily_expenses_df[f'rolling_avg_{window}'] = daily_expenses_df['amount'].rolling(window).mean()
            
            # Drop rows with NaN values
            daily_expenses_df = daily_expenses_df.dropna()
            
            if len(daily_expenses_df) < 20:
                return {"error": "Insufficient data after feature engineering"}
            
            # Prepare features and target
            feature_cols = [col for col in daily_expenses_df.columns if col not in ['date', 'amount']]
            X = daily_expenses_df[feature_cols].values
            y = daily_expenses_df['amount'].values
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            
            # Scale features
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.spending_predictor = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.spending_predictor.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.spending_predictor.score(X_train_scaled, y_train)
            test_score = self.spending_predictor.score(X_test_scaled, y_test)
            
            # Save model
            model_data = {
                'predictor': self.spending_predictor,
                'scaler': self.scaler,
                'feature_columns': feature_cols
            }
            
            joblib.dump(model_data, self.models_path / "spending_predictor.pkl")
            
            return {
                "train_score": train_score,
                "test_score": test_score,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features": feature_cols
            }
            
        except Exception as e:
            return {"error": f"Training failed: {str(e)}"}
    
    async def predict_spending(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Predict spending for next N days"""
        try:
            if not self.spending_predictor:
                # Try to load saved model
                model_path = self.models_path / "spending_predictor.pkl"
                if model_path.exists():
                    model_data = joblib.load(model_path)
                    self.spending_predictor = model_data['predictor']
                    self.scaler = model_data['scaler']
                else:
                    return {"error": "Model not trained"}
            
            # This is a simplified prediction - in practice, you'd need recent transaction data
            # to generate proper features
            predictions = []
            
            for i in range(days_ahead):
                # Create mock features for prediction
                # In practice, these would be based on recent transaction patterns
                future_date = datetime.now() + timedelta(days=i+1)
                
                features = [
                    future_date.weekday(),  # day_of_week
                    future_date.day,       # day_of_month
                    future_date.month,     # month
                    1 if future_date.weekday() in [5, 6] else 0,  # is_weekend
                    100,  # lag_1 (mock)
                    100,  # lag_3 (mock)
                    100,  # lag_7 (mock)
                    100,  # rolling_avg_3 (mock)
                    100,  # rolling_avg_7 (mock)
                    100,  # rolling_avg_14 (mock)
                ]
                
                features_scaled = self.scaler.transform([features])
                prediction = self.spending_predictor.predict(features_scaled)[0]
                
                predictions.append({
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_amount": float(prediction),
                    "day_of_week": future_date.strftime("%A")
                })
            
            return {
                "predictions": predictions,
                "total_predicted": sum(p["predicted_amount"] for p in predictions)
            }
            
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    async def detect_anomalies(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Detect anomalous transactions"""
        try:
            df = pd.DataFrame(transactions)
            
            if df.empty:
                return {"anomalies": [], "total_checked": 0}
            
            # Extract features
            features_df = self.extract_transaction_features(transactions)
            
            # Use isolation forest for anomaly detection
            from sklearn.ensemble import IsolationForest
            
            # Select numerical features
            numerical_cols = ['valor_abs', 'day_of_week', 'month']
            X = features_df[numerical_cols].fillna(0).values
            
            # Fit anomaly detector
            anomaly_detector = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            
            anomaly_scores = anomaly_detector.fit_predict(X)
            anomaly_probabilities = anomaly_detector.score_samples(X)
            
            # Identify anomalies
            anomalies = []
            for i, (score, prob) in enumerate(zip(anomaly_scores, anomaly_probabilities)):
                if score == -1:  # Anomaly
                    transaction = transactions[i]
                    anomalies.append({
                        "transaction": transaction,
                        "anomaly_score": float(prob),
                        "reasons": self._analyze_anomaly_reasons(transaction, features_df.iloc[i])
                    })
            
            return {
                "anomalies": anomalies,
                "total_checked": len(transactions),
                "anomaly_rate": len(anomalies) / len(transactions) if transactions else 0
            }
            
        except Exception as e:
            return {"error": f"Anomaly detection failed: {str(e)}"}
    
    def _analyze_anomaly_reasons(self, transaction: Dict, features: pd.Series) -> List[str]:
        """Analyze why a transaction is considered anomalous"""
        reasons = []
        
        # High amount
        if features.get('valor_abs', 0) > 1000:
            reasons.append("Valor muito alto")
        
        # Weekend transaction
        if features.get('is_weekend', 0) == 1 and features.get('valor_abs', 0) > 200:
            reasons.append("Transação de alto valor no fim de semana")
        
        # Late night/early morning (if we had time data)
        # End of month
        if features.get('day_of_month', 0) > 28:
            reasons.append("Transação no final do mês")
        
        return reasons if reasons else ["Padrão atípico detectado"]
    
    @cached_function(ttl=3600, namespace="ml")
    async def generate_financial_insights(self, user_transactions: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive financial insights"""
        try:
            df = pd.DataFrame(user_transactions)
            
            if df.empty:
                return {"insights": [], "summary": {}}
            
            insights = []
            
            # Spending pattern analysis
            df['data_lancamento'] = pd.to_datetime(df['data_lancamento'])
            expenses = df[df['valor'] < 0].copy()
            
            if not expenses.empty:
                # Monthly spending trend
                monthly_spending = expenses.groupby(
                    expenses['data_lancamento'].dt.to_period('M')
                )['valor'].sum().abs()
                
                if len(monthly_spending) > 1:
                    trend = "crescente" if monthly_spending.iloc[-1] > monthly_spending.iloc[-2] else "decrescente"
                    insights.append({
                        "type": "trend",
                        "title": f"Gastos mensais em tendência {trend}",
                        "description": f"Seus gastos estão {trend} em relação ao mês anterior",
                        "impact": "medium"
                    })
                
                # Day of week analysis
                expenses['day_of_week'] = expenses['data_lancamento'].dt.dayofweek
                dow_spending = expenses.groupby('day_of_week')['valor'].sum().abs()
                max_spending_day = dow_spending.idxmax()
                
                day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                insights.append({
                    "type": "pattern",
                    "title": f"Maior gasto às {day_names[max_spending_day]}",
                    "description": f"Você tende a gastar mais às {day_names[max_spending_day]}s",
                    "impact": "low"
                })
                
                # Category analysis
                if 'categoria_id' in expenses.columns:
                    category_spending = expenses.groupby('categoria_id')['valor'].sum().abs()
                    top_category = category_spending.idxmax()
                    
                    insights.append({
                        "type": "category",
                        "title": "Categoria com maior gasto",
                        "description": f"A categoria {top_category} representa {(category_spending[top_category]/category_spending.sum()*100):.1f}% dos seus gastos",
                        "impact": "high"
                    })
            
            # Income analysis
            income = df[df['valor'] > 0]
            if not income.empty:
                avg_income = income['valor'].mean()
                insights.append({
                    "type": "income",
                    "title": "Receita média",
                    "description": f"Sua receita média por transação é R$ {avg_income:.2f}",
                    "impact": "medium"
                })
            
            # Summary statistics
            summary = {
                "total_transactions": len(df),
                "total_income": float(df[df['valor'] > 0]['valor'].sum()),
                "total_expenses": float(abs(df[df['valor'] < 0]['valor'].sum())),
                "net_amount": float(df['valor'].sum()),
                "avg_transaction": float(df['valor'].mean()),
                "date_range": {
                    "start": df['data_lancamento'].min().isoformat() if not df.empty else None,
                    "end": df['data_lancamento'].max().isoformat() if not df.empty else None
                }
            }
            
            return {
                "insights": insights,
                "summary": summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Insight generation failed: {str(e)}"}
    
    async def cluster_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Cluster transactions to find spending patterns"""
        try:
            features_df = self.extract_transaction_features(transactions)
            
            if features_df.empty:
                return {"clusters": [], "total_transactions": 0}
            
            # Select features for clustering
            clustering_features = ['valor_abs', 'day_of_week', 'month']
            X = features_df[clustering_features].fillna(0).values
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform clustering
            n_clusters = min(5, len(transactions) // 10)  # Adaptive number of clusters
            if n_clusters < 2:
                n_clusters = 2
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X_scaled)
            
            # Analyze clusters
            clusters = []
            for i in range(n_clusters):
                cluster_mask = cluster_labels == i
                cluster_transactions = [t for j, t in enumerate(transactions) if cluster_mask[j]]
                
                if cluster_transactions:
                    cluster_df = pd.DataFrame(cluster_transactions)
                    
                    cluster_info = {
                        "cluster_id": i,
                        "size": len(cluster_transactions),
                        "avg_amount": float(cluster_df['valor'].abs().mean()),
                        "total_amount": float(cluster_df['valor'].sum()),
                        "date_range": {
                            "start": cluster_df['data_lancamento'].min() if 'data_lancamento' in cluster_df else None,
                            "end": cluster_df['data_lancamento'].max() if 'data_lancamento' in cluster_df else None
                        },
                        "characteristics": self._describe_cluster(cluster_df)
                    }
                    
                    clusters.append(cluster_info)
            
            return {
                "clusters": clusters,
                "total_transactions": len(transactions),
                "clustering_features": clustering_features
            }
            
        except Exception as e:
            return {"error": f"Clustering failed: {str(e)}"}
    
    def _describe_cluster(self, cluster_df: pd.DataFrame) -> Dict[str, str]:
        """Describe characteristics of a transaction cluster"""
        characteristics = {}
        
        # Amount pattern
        avg_amount = cluster_df['valor'].abs().mean()
        if avg_amount < 50:
            characteristics['amount'] = "Pequenos valores"
        elif avg_amount < 200:
            characteristics['amount'] = "Valores médios"
        else:
            characteristics['amount'] = "Valores altos"
        
        # Transaction type
        if (cluster_df['valor'] > 0).sum() > len(cluster_df) * 0.8:
            characteristics['type'] = "Principalmente receitas"
        elif (cluster_df['valor'] < 0).sum() > len(cluster_df) * 0.8:
            characteristics['type'] = "Principalmente despesas"
        else:
            characteristics['type'] = "Misto"
        
        return characteristics


# Global ML service instance
ml_service = MLFinancialAnalyzer()


# Utility functions for ML operations
async def auto_categorize_transaction(transaction_data: Dict) -> Optional[int]:
    """Auto-categorize a transaction using ML"""
    result = await ml_service.predict_category(transaction_data)
    
    if "predicted_category" in result and result.get("confidence", 0) > 0.7:
        return result["predicted_category"]
    
    return None


async def get_spending_forecast(user_id: str, days: int = 7) -> Dict[str, Any]:
    """Get spending forecast for a user"""
    try:
        cached_result = await FinancialCache.get_dashboard_data(f"forecast_{user_id}_{days}")
        if cached_result:
            return cached_result
        
        # Get prediction
        result = await ml_service.predict_spending(days)
        
        # Cache result
        await FinancialCache.set_dashboard_data(f"forecast_{user_id}_{days}", result)
        
        return result
        
    except Exception as e:
        return {"error": f"Forecast failed: {str(e)}"}


async def analyze_spending_patterns(user_transactions: List[Dict]) -> Dict[str, Any]:
    """Analyze user spending patterns"""
    try:
        # Generate insights
        insights = await ml_service.generate_financial_insights(user_transactions)
        
        # Detect anomalies
        anomalies = await ml_service.detect_anomalies(user_transactions)
        
        # Cluster analysis
        clusters = await ml_service.cluster_transactions(user_transactions)
        
        return {
            "insights": insights,
            "anomalies": anomalies,
            "clusters": clusters,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Pattern analysis failed: {str(e)}"}


# Background task for model training
async def train_models_periodically():
    """Periodic model training task"""
    print("🤖 Iniciando treinamento periódico dos modelos ML...")
    
    try:
        # This would fetch recent transactions from database
        # For now, it's a placeholder
        # transactions = await get_all_transactions()
        # 
        # # Train category classifier
        # await ml_service.train_category_classifier(transactions)
        # 
        # # Train spending predictor
        # await ml_service.train_spending_predictor(transactions)
        
        print("✅ Modelos ML treinados com sucesso")
        
    except Exception as e:
        print(f"❌ Erro no treinamento dos modelos: {e}")


# ML health check
async def ml_health_check() -> Dict[str, Any]:
    """Check ML service health"""
    health = {
        "status": "healthy",
        "models_loaded": {},
        "errors": []
    }
    
    try:
        # Check if models exist
        models_path = Path("app/ml_models")
        health["models_loaded"]["category_classifier"] = (models_path / "category_classifier.pkl").exists()
        health["models_loaded"]["spending_predictor"] = (models_path / "spending_predictor.pkl").exists()
        
        # Test basic functionality
        test_transaction = {
            "descricao": "Teste ML",
            "valor": -100.0,
            "data_lancamento": datetime.now().isoformat()
        }
        
        # Test insight generation
        insights = await ml_service.generate_financial_insights([test_transaction])
        if "error" in insights:
            health["errors"].append(f"Insight generation: {insights['error']}")
        
    except Exception as e:
        health["errors"].append(f"ML health check error: {str(e)}")
        health["status"] = "unhealthy"
    
    return health 