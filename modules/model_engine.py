import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
import pmdarima as pm
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False

class ForecastModel:
    def __init__(self, name):
        self.name = name
        self.model = None
        self.predictions = None
        self.metrics = {}

    def calculate_metrics(self, y_true, y_pred):
        """Calculate forecast metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        r2 = r2_score(y_true, y_pred)

        self.metrics = {
            'MAE': round(mae, 2),
            'RMSE': round(rmse, 2),
            'MAPE': round(mape, 2),
            'R²': round(r2, 4)
        }
        return self.metrics

class MovingAverageModel(ForecastModel):
    def __init__(self, window=7):
        super().__init__(f"移动平均 (MA-{window})")
        self.window = window

    def fit(self, train_series):
        self.train_data = train_series
        return self

    def predict(self, steps):
        last_values = self.train_data[-self.window:].values
        forecast = [np.mean(last_values)] * steps
        return np.array(forecast)

class ExponentialSmoothingModel(ForecastModel):
    def __init__(self, seasonal=False, seasonal_periods=None):
        name = "指数平滑 (Holt-Winters)" if seasonal else "指数平滑 (Simple)"
        super().__init__(name)
        self.seasonal = seasonal
        self.seasonal_periods = seasonal_periods

    def fit(self, train_series):
        try:
            if self.seasonal and self.seasonal_periods:
                self.model = ExponentialSmoothing(
                    train_series,
                    seasonal='add',
                    seasonal_periods=self.seasonal_periods
                ).fit()
            else:
                self.model = ExponentialSmoothing(train_series).fit()
            return self
        except:
            # Fallback to simple
            self.model = ExponentialSmoothing(train_series).fit()
            return self

    def predict(self, steps):
        return self.model.forecast(steps)

class ARIMAModel(ForecastModel):
    def __init__(self):
        super().__init__("ARIMA (自动)")

    def fit(self, train_series):
        try:
            self.model = pm.auto_arima(
                train_series,
                seasonal=False,
                stepwise=True,
                suppress_warnings=True,
                error_action='ignore',
                max_order=5,
                trace=False
            )
            return self
        except:
            # Fallback to simple ARIMA(1,1,1)
            self.model = ARIMA(train_series, order=(1,1,1)).fit()
            return self

    def predict(self, steps):
        return self.model.predict(n_periods=steps)

class XGBoostModel(ForecastModel):
    def __init__(self):
        super().__init__("XGBoost")
        self.lookback = 7

    def fit(self, train_series):
        X, y = [], []
        for i in range(self.lookback, len(train_series)):
            X.append(train_series[i-self.lookback:i])
            y.append(train_series[i])

        X, y = np.array(X), np.array(y)
        self.model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
        self.model.fit(X, y)
        self.train_data = train_series
        return self

    def predict(self, steps):
        forecast = []
        current_sequence = list(self.train_data[-self.lookback:])

        for _ in range(steps):
            X_pred = np.array(current_sequence[-self.lookback:]).reshape(1, -1)
            pred = self.model.predict(X_pred)[0]
            forecast.append(pred)
            current_sequence.append(pred)

        return np.array(forecast)

class LSTMModel(ForecastModel):
    def __init__(self):
        super().__init__("LSTM")
        self.lookback = 7

    def fit(self, train_series):
        X, y = [], []
        for i in range(self.lookback, len(train_series)):
            X.append(train_series[i-self.lookback:i])
            y.append(train_series[i])

        X, y = np.array(X), np.array(y)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        self.model = Sequential([
            LSTM(50, activation='relu', input_shape=(self.lookback, 1)),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.model.fit(X, y, epochs=50, batch_size=16, verbose=0)
        self.train_data = train_series
        return self

    def predict(self, steps):
        forecast = []
        current_sequence = list(self.train_data[-self.lookback:])

        for _ in range(steps):
            X_pred = np.array(current_sequence[-self.lookback:]).reshape(1, self.lookback, 1)
            pred = self.model.predict(X_pred, verbose=0)[0][0]
            forecast.append(pred)
            current_sequence.append(pred)

        return np.array(forecast)

class ModelEngine:
    def __init__(self):
        self.models = []
        self.best_model = None
        self.results = []

    def train_all_models(self, train_df, test_df, date_col, target_col, has_seasonality=False):
        """Train all baseline models"""
        train_series = train_df[target_col].values
        test_series = test_df[target_col].values
        test_steps = len(test_series)

        # Detect seasonal period
        seasonal_period = 7 if has_seasonality else None

        # Initialize models
        models_to_train = [
            MovingAverageModel(window=7),
            MovingAverageModel(window=30),
            ExponentialSmoothingModel(seasonal=False),
            ExponentialSmoothingModel(seasonal=has_seasonality, seasonal_periods=seasonal_period),
            ARIMAModel()
        ]

        if XGBOOST_AVAILABLE and len(train_series) > 30:
            models_to_train.append(XGBoostModel())

        if LSTM_AVAILABLE and len(train_series) > 50:
            models_to_train.append(LSTMModel())

        results = []

        for model in models_to_train:
            try:
                # Train
                model.fit(train_series)

                # Predict
                predictions = model.predict(test_steps)

                # Calculate metrics
                metrics = model.calculate_metrics(test_series, predictions)

                results.append({
                    'model_name': model.name,
                    'model': model,
                    'predictions': predictions,
                    'metrics': metrics,
                    'mape': metrics['MAPE']
                })
            except Exception as e:
                print(f"模型 {model.name} 训练失败: {str(e)}")
                continue

        # Sort by MAPE (lower is better)
        results.sort(key=lambda x: x['mape'])

        self.results = results
        self.best_model = results[0] if results else None

        return results

    def get_best_model(self):
        """Get the best performing model"""
        return self.best_model

    def forecast_future(self, steps):
        """Generate future forecast using best model"""
        if not self.best_model:
            raise ValueError("没有训练好的模型")

        model = self.best_model['model']
        forecast = model.predict(steps)

        # Generate confidence intervals (simplified)
        std = np.std(model.train_data[-30:]) if hasattr(model, 'train_data') else np.std(forecast)
        lower_bound = forecast - 1.96 * std
        upper_bound = forecast + 1.96 * std

        return {
            'forecast': forecast,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }
