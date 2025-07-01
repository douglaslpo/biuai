# Guia do Serviço de Machine Learning

## Finalidade do ML
O serviço de Machine Learning (ML) tem como objetivo principal realizar previsões financeiras baseadas nos dados históricos dos usuários. Especificamente, ele:

1. **Previsão de Gastos**: Prevê gastos futuros por categoria
2. **Análise de Padrões**: Identifica padrões de gastos temporais
3. **Importância de Features**: Analisa quais fatores mais influenciam os gastos

## Tecnologias Utilizadas
- **XGBoost**: Algoritmo principal de Machine Learning
- **SHAP**: Para análise de importância de features
- **Pandas**: Para manipulação de dados
- **Scikit-learn**: Para pré-processamento de dados

## Como Usar o Serviço

### 1. Endpoint de Predição
```bash
curl -X POST "http://localhost:8000/api/v1/predictions/" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "start_date": "2024-01-01",
       "end_date": "2024-01-31",
       "categories": ["alimentação", "transporte", "lazer"]
     }'
```

### 2. Dados de Entrada Necessários
- **user_id**: ID do usuário
- **start_date**: Data inicial para previsão
- **end_date**: Data final para previsão
- **categories**: Lista de categorias para previsão (opcional)

### 3. Resposta do Serviço
```json
{
    "predictions": {
        "alimentação": 500.0,
        "transporte": 300.0,
        "lazer": 200.0
    },
    "confidence": {
        "alimentação": 0.85,
        "transporte": 0.90,
        "lazer": 0.75
    },
    "feature_importance": {
        "month": 0.3,
        "day_of_week": 0.2,
        "categoria": 0.5
    },
    "model_version": "model_20240101_120000.joblib"
}
```

## Features do Modelo

### 1. Features Temporais
- Mês
- Dia da semana
- Dia do mês

### 2. Features Categóricas
- Categoria da despesa
- Tipo de lançamento

## Treinamento do Modelo
O modelo é treinado automaticamente com:
1. Dados históricos dos usuários
2. Padrões temporais
3. Categorias de gastos
4. Tipos de lançamentos

## Métricas e Avaliação
O modelo fornece:
1. Previsões de valores
2. Níveis de confiança
3. Importância das features
4. Métricas de performance

## Notas Importantes
1. O modelo precisa de dados históricos para fazer previsões precisas
2. As previsões são mais precisas para categorias com mais dados
3. O modelo é atualizado automaticamente com novos dados
4. As previsões consideram padrões sazonais (mensais e semanais)

## Exemplos de Uso

### 1. Previsão Mensal
```python
import requests
import json

url = "http://localhost:8000/api/v1/predictions/"
data = {
    "user_id": 1,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "categories": ["alimentação", "transporte"]
}

response = requests.post(url, json=data)
predictions = response.json()
print(json.dumps(predictions, indent=2))
```

### 2. Análise de Importância
```python
# As features mais importantes indicam quais fatores mais influenciam os gastos
feature_importance = predictions["feature_importance"]
for feature, importance in feature_importance.items():
    print(f"{feature}: {importance:.2f}")
```

## Recomendações de Uso
1. Use períodos de previsão de até 3 meses para maior precisão
2. Inclua todas as categorias relevantes na previsão
3. Mantenha os dados históricos atualizados
4. Monitore os níveis de confiança das previsões 