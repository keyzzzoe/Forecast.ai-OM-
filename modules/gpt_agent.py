import os

class GPTAgent:
    def __init__(self, use_api=False):
        self.use_api = use_api
        self.api_key = os.getenv("OPENAI_API_KEY", "")

    def explain_model_selection(self, context):
        if self.use_api and self.api_key:
            return self._call_openai_model_explanation(context)
        return self._mock_model_explanation(context)

    def generate_business_insights(self, context):
        if self.use_api and self.api_key:
            return self._call_openai_business_insights(context)
        return self._mock_business_insights(context)

    def _mock_model_explanation(self, context):
        best_model = context.get('best_model', 'Unknown')
        mape = context.get('mape', 0)
        industry = context.get('industry', 'general')
        has_seasonality = context.get('has_seasonality', False)

        quality = "优秀" if mape < 10 else "良好" if mape < 20 else "可接受"

        explanation = f"""### 🎯 模型选择分析

**{best_model}** 在测试集上表现最佳，MAPE为 **{mape:.2f}%**，预测质量评级为 **{quality}**。

#### 为什么选择这个模型？

"""
        if 'ARIMA' in best_model:
            explanation += f"- **ARIMA模型** 擅长捕捉时间序列的趋势和自相关性\n- 适合{industry}行业的需求预测，能够处理非平稳数据\n"
            if has_seasonality:
                explanation += "- 通过差分和季节性参数有效处理周期性波动\n"
        elif 'Exponential Smoothing' in best_model or 'Holt' in best_model:
            explanation += f"- **指数平滑模型** 对近期数据赋予更高权重，响应迅速\n- 在{industry}行业中表现稳定，计算效率高\n"
            if has_seasonality:
                explanation += "- Holt-Winters方法能够同时处理趋势和季节性\n"
        elif 'Moving Average' in best_model:
            explanation += f"- **移动平均模型** 简单直观，适合平稳的需求模式\n- 在{industry}行业的短期预测中表现良好\n- 对异常值有一定的平滑作用\n"
        else:
            explanation += f"- 该模型在测试数据上展现出最低的预测误差\n- 适合{industry}行业的数据特征\n"

        explanation += f"""
#### 性能指标解读

- **MAPE (平均绝对百分比误差)**: {mape:.2f}% - 预测值与实际值的平均偏差
- 数值越低表示预测越准确，当前模型达到 **{quality}** 水平

#### 建议

"""
        if mape < 10:
            explanation += "- ✅ 模型预测精度优秀，可以直接用于业务决策\n- 建议定期监控预测误差，确保模型持续有效\n"
        elif mape < 20:
            explanation += "- ✅ 模型预测精度良好，适合大多数业务场景\n- 可以考虑结合业务经验进行微调\n"
        else:
            explanation += "- ⚠️ 模型预测精度可接受，但建议谨慎使用\n- 考虑收集更多历史数据或添加外部特征以提升精度\n"

        return explanation

    def _mock_business_insights(self, context):
        industry = context.get('industry', 'general')
        forecast_target = context.get('forecast_target', '需求')
        mape = context.get('mape', 0)
        forecast_mean = context.get('forecast_mean', 0)
        forecast_trend = context.get('forecast_trend', 'stable')

        insights = f"### 📊 趋势分析\n\n"

        if forecast_trend == 'upward':
            insights += f"未来{forecast_target}呈现 **上升趋势**，平均预测值为 **{forecast_mean:.2f}**。\n\n#### 关键发现\n\n- 📈 需求增长信号明显，建议提前做好资源准备\n"
            if industry == 'retail':
                insights += "- 🛒 零售业需求上升可能与促销活动、季节性因素或市场扩张有关\n- 建议增加库存储备，优化供应链响应速度\n"
            elif industry == 'healthcare':
                insights += "- 🏥 医疗需求上升可能反映季节性疾病高发或人口老龄化趋势\n- 建议合理调配医护资源，优化排班计划\n"
            elif industry == 'ecommerce':
                insights += "- 📦 电商订单增长可能与营销活动、节假日或用户增长有关\n- 建议提前备货，加强物流配送能力\n"
            elif industry == 'aviation':
                insights += "- ✈️ 航班预订增长可能与旅游旺季、商务出行增加有关\n- 建议优化航班排班，提升客舱利用率\n"
        elif forecast_trend == 'downward':
            insights += f"未来{forecast_target}呈现 **下降趋势**，平均预测值为 **{forecast_mean:.2f}**。\n\n#### 关键发现\n\n- 📉 需求下降信号，建议优化成本控制\n"
            if industry == 'retail':
                insights += "- 🛒 零售需求下降可能与市场竞争、消费习惯变化有关\n- 建议调整库存策略，避免积压\n"
            elif industry == 'healthcare':
                insights += "- 🏥 医疗需求下降可能反映季节性因素或预防措施见效\n- 建议灵活调整资源配置，控制运营成本\n"
            elif industry == 'ecommerce':
                insights += "- 📦 电商订单下降可能与市场饱和、竞争加剧有关\n- 建议优化营销策略，提升用户留存\n"
            elif industry == 'aviation':
                insights += "- ✈️ 航班预订下降可能与淡季、经济因素有关\n- 建议调整航班频次，优化成本结构\n"
        else:
            insights += f"未来{forecast_target}保持 **相对稳定**，平均预测值为 **{forecast_mean:.2f}**。\n\n#### 关键发现\n\n- ➡️ 需求波动较小，业务运营可保持当前节奏\n"

        insights += "\n### 💡 业务建议\n\n"
        if mape < 10:
            insights += f"1. **高精度预测优势**: 当前模型MAPE为{mape:.2f}%，可作为核心决策依据\n2. **资源优化**: 基于预测结果精准配置资源，降低浪费\n"
        else:
            insights += f"1. **谨慎决策**: 当前模型MAPE为{mape:.2f}%，建议结合业务经验综合判断\n2. **持续优化**: 收集更多数据，定期重新训练模型以提升精度\n"
        insights += "3. **监控反馈**: 定期对比预测值与实际值，及时调整策略\n4. **场景规划**: 参考95%置信区间，为最好和最坏情况制定应对方案\n"

        return insights

    def chat_response(self, user_message, session_state):
        """Generate a chat response for the sidebar AI assistant"""
        industry = getattr(session_state, 'industry', None) or 'general'
        msg = user_message.lower()

        if any(w in msg for w in ['mape', '误差', '精度', '准确']):
            return "MAPE（平均绝对百分比误差）越低越好，10%以下为优秀，20%以下为良好。"
        elif any(w in msg for w in ['模型', 'model', 'arima', '预测']):
            return f"系统支持ARIMA、指数平滑、移动平均等多种模型，会自动选择在{industry}行业数据上表现最好的模型。"
        elif any(w in msg for w in ['数据', '上传', 'csv', 'excel']):
            return "支持CSV和Excel格式，需要包含日期列和目标值列。建议至少提供1年以上的历史数据。"
        elif any(w in msg for w in ['报告', 'pdf', '下载']):
            return "完成预测后可在第四步生成PDF报告，包含模型对比、预测结果和业务建议。"
        elif any(w in msg for w in ['行业', '零售', '医疗', '电商', '航空']):
            return f"当前选择的行业是{industry}。系统针对不同行业优化了预测策略和业务建议。"
        else:
            return "您好！我是ForecastAI助手。我可以帮您解答关于需求预测、模型选择、数据准备等问题。请问有什么需要帮助的？"

    def _call_openai_model_explanation(self, context):
        pass

    def _call_openai_business_insights(self, context):
        pass
