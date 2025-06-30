import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
from typing import Dict, List, Tuple
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import shap

from app.core.config import settings

class PredictionService:
    def __init__(self):
        self.model_path = settings.MODEL_PATH
        self.model = None
        self.label_encoders = {}
        self.feature_names = None
        self.load_model()

    def load_model(self) -> None:
        """Load the latest model and encoders from disk."""
        try:
            model_files = [f for f in os.listdir(self.model_path) if f.endswith('.joblib')]
            if not model_files:
                return
            
            latest_model = sorted(model_files)[-1]
            model_data = joblib.load(os.path.join(self.model_path, latest_model))
            
            self.model = model_data['model']
            self.label_encoders = model_data.get('label_encoders', {})
            self.feature_names = model_data.get('feature_names', None)
        except Exception as e:
            print(f"Error loading model: {e}")

    def save_model(self, model_data: Dict) -> str:
        """Save model and related data to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_{timestamp}.joblib"
        filepath = os.path.join(self.model_path, filename)
        
        joblib.dump(model_data, filepath)
        return filename

    def preprocess_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, LabelEncoder]]:
        """Preprocess the input data for training or prediction."""
        # Create temporal features
        df['month'] = df['data'].dt.month
        df['day_of_week'] = df['data'].dt.dayofweek
        df['day_of_month'] = df['data'].dt.day
        
        # Encode categorical variables
        categorical_columns = ['categoria', 'tipo']
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[col] = self.label_encoders[col].transform(df[col])
        
        return df

    async def train_model(
        self,
        df: pd.DataFrame,
        model_params: Dict = None
    ) -> Dict:
        """Train a new model on the provided data."""
        start_time = datetime.now()
        
        # Preprocess data
        df = self.preprocess_data(df)
        
        # Prepare features and target
        features = ['month', 'day_of_week', 'day_of_month', 'categoria', 'tipo']
        X = df[features]
        y = df['valor']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        if model_params is None:
            model_params = {
                'objective': 'reg:squarederror',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100
            }
        
        model = xgb.XGBRegressor(**model_params)
        model.fit(X_train, y_train)
        
        # Calculate metrics
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        # Calculate feature importance
        feature_importance = dict(zip(features, model.feature_importances_))
        
        # Save model
        model_data = {
            'model': model,
            'label_encoders': self.label_encoders,
            'feature_names': features,
            'training_date': datetime.now().isoformat()
        }
        model_version = self.save_model(model_data)
        
        # Update current model
        self.model = model
        self.feature_names = features
        
        training_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'model_version': model_version,
            'metrics': {
                'train_score': train_score,
                'test_score': test_score
            },
            'training_time': training_time,
            'feature_importance': feature_importance
        }

    async def predict(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        categories: List[str] = None
    ) -> Dict:
        """Make predictions using the trained model."""
        if self.model is None:
            raise ValueError("No model loaded. Please train a model first.")
        
        # Generate sample data for prediction
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        sample_data = []
        
        for date in dates:
            if categories:
                for cat in categories:
                    sample_data.append({
                        'data': date,
                        'categoria': cat,
                        'tipo': 'despesa',  # Default type
                        'valor': 0  # Will be predicted
                    })
            else:
                sample_data.append({
                    'data': date,
                    'categoria': 'outros',  # Default category
                    'tipo': 'despesa',  # Default type
                    'valor': 0  # Will be predicted
                })
        
        df = pd.DataFrame(sample_data)
        
        # Preprocess data
        df = self.preprocess_data(df)
        
        # Make predictions
        predictions = self.model.predict(df[self.feature_names])
        
        # Calculate confidence scores (using prediction std as proxy)
        if hasattr(self.model, 'predict_proba'):
            confidence = self.model.predict_proba(df[self.feature_names])
        else:
            confidence = np.ones_like(predictions)  # Default confidence of 1
        
        # Calculate feature importance using SHAP
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(df[self.feature_names])
        feature_importance = dict(zip(self.feature_names, np.abs(shap_values).mean(0)))
        
        # Group predictions by category
        results = {}
        confidence_by_category = {}
        for cat in df['categoria'].unique():
            mask = df['categoria'] == cat
            results[cat] = float(predictions[mask].mean())  # Convert to float for JSON serialization
            confidence_by_category[cat] = float(confidence[mask].mean())  # Convert to float for JSON serialization
        
        return {
            'predictions': results,
            'confidence': confidence_by_category,
            'feature_importance': feature_importance,
            'model_version': os.path.basename(self.model_path)
        } 