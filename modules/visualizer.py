import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    def __init__(self):
        self.color_scheme = {
            'primary': '#1E88E5',
            'secondary': '#FFC107',
            'success': '#4CAF50',
            'danger': '#F44336',
            'actual': '#1E88E5',
            'predicted': '#FFC107',
            'confidence': 'rgba(30, 136, 229, 0.2)'
        }

    def plot_forecast(self, train_df, test_df, test_predictions, forecast, lower_bound, upper_bound, date_col, target_col):
        """Create interactive forecast plot with Plotly"""
        fig = go.Figure()

        # Training data
        fig.add_trace(go.Scatter(
            x=train_df[date_col],
            y=train_df[target_col],
            mode='lines',
            name='历史数据',
            line=dict(color=self.color_scheme['actual'], width=2)
        ))

        # Test data (actual)
        fig.add_trace(go.Scatter(
            x=test_df[date_col],
            y=test_df[target_col],
            mode='lines',
            name='实际值',
            line=dict(color=self.color_scheme['success'], width=2)
        ))

        # Test predictions
        fig.add_trace(go.Scatter(
            x=test_df[date_col],
            y=test_predictions,
            mode='lines',
            name='测试预测',
            line=dict(color=self.color_scheme['predicted'], width=2, dash='dash')
        ))

        # Future forecast dates
        last_date = test_df[date_col].iloc[-1]
        import pandas as pd
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=len(forecast))

        # Future forecast
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=forecast,
            mode='lines',
            name='未来预测',
            line=dict(color=self.color_scheme['secondary'], width=3)
        ))

        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=upper_bound,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=forecast_dates,
            y=lower_bound,
            mode='lines',
            fill='tonexty',
            fillcolor=self.color_scheme['confidence'],
            line=dict(width=0),
            name='95%置信区间',
            hoverinfo='skip'
        ))

        fig.update_layout(
            title='预测结果对比',
            xaxis_title='日期',
            yaxis_title='需求量',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )

        return fig

    def plot_future_forecast(self, historical_data, forecast_data, date_col, target_col):
        """Plot future forecast with confidence intervals"""
        fig = go.Figure()

        # Historical data
        fig.add_trace(go.Scatter(
            x=historical_data[date_col],
            y=historical_data[target_col],
            mode='lines',
            name='历史数据',
            line=dict(color=self.color_scheme['actual'], width=2)
        ))

        # Future forecast
        future_dates = forecast_data['dates']
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['forecast'],
            mode='lines',
            name='预测值',
            line=dict(color=self.color_scheme['predicted'], width=3)
        ))

        # Confidence interval
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['upper_bound'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['lower_bound'],
            mode='lines',
            fill='tonexty',
            fillcolor=self.color_scheme['confidence'],
            line=dict(width=0),
            name='95%置信区间',
            hoverinfo='skip'
        ))

        fig.update_layout(
            title='未来需求预测',
            xaxis_title='日期',
            yaxis_title='预测需求量',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )

        return fig

    def plot_model_comparison(self, results):
        """Create model comparison bar chart"""
        models = [r['model_name'] for r in results]
        mapes = [r['metrics']['MAPE'] for r in results]

        colors = [self.color_scheme['success'] if i == 0 else self.color_scheme['primary']
                  for i in range(len(models))]

        fig = go.Figure(data=[
            go.Bar(
                x=models,
                y=mapes,
                marker_color=colors,
                text=[f"{m:.2f}%" for m in mapes],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='模型性能对比 (MAPE越低越好)',
            xaxis_title='模型',
            yaxis_title='MAPE (%)',
            template='plotly_white',
            height=400
        )

        return fig

    def plot_residuals(self, actual, predicted):
        """Plot residual analysis"""
        residuals = actual - predicted

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(range(len(residuals))),
            y=residuals,
            mode='markers',
            marker=dict(color=self.color_scheme['primary'], size=8),
            name='残差'
        ))

        fig.add_hline(y=0, line_dash="dash", line_color="red")

        fig.update_layout(
            title='残差分析',
            xaxis_title='样本序号',
            yaxis_title='残差 (实际值 - 预测值)',
            template='plotly_white',
            height=400
        )

        return fig

    def create_metrics_table(self, results):
        """Create metrics comparison table"""
        data = []
        for r in results:
            data.append({
                '模型': r['model_name'],
                'MAE': r['metrics']['MAE'],
                'RMSE': r['metrics']['RMSE'],
                'MAPE (%)': r['metrics']['MAPE'],
                'R²': r['metrics']['R²']
            })
        return data
