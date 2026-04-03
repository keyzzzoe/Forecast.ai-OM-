import streamlit as st
from modules.session_manager import init_session_state
from modules.visualizer import Visualizer
from modules.ai_assistant import get_progress_html, get_ai_assistant_html
import pandas as pd
import numpy as np

st.set_page_config(page_title="反馈迭代 — ForecastAI", page_icon="🔄", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

if st.session_state.get('future_forecast') is None:
    st.warning("⚠️ 请先完成预测报告")
    if st.button("← 返回预测报告"):
        st.switch_page("pages/4_📈_Forecast_Report.py")
    st.stop()

# ── Enhanced Progress Bar ──
st.markdown(get_progress_html(current_step=5, completed_steps=[1, 2, 3, 4]), unsafe_allow_html=True)

# ── AI Assistant ──
st.markdown(get_ai_assistant_html(step=5), unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h1>🔄 第五步：反馈迭代</h1>
  <p>录入实际发生的数据，系统将对比预测值与实际值，评估模型表现并给出优化建议</p>
</div>
""", unsafe_allow_html=True)

forecast_result = st.session_state.future_forecast
date_col = st.session_state.date_column
target_col = st.session_state.target_column

last_date = pd.to_datetime(st.session_state.test_data[date_col].iloc[-1])
forecast_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=st.session_state.planning_horizon
)

if 'actual_values' not in st.session_state:
    st.session_state.actual_values = {}

# ── Input Section ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 📝 录入实际值")
st.caption("随着时间推移，录入实际发生的需求值，系统将自动计算预测误差")

col1, col2 = st.columns([1, 2])

with col1:
    selected_date = st.selectbox("选择日期", forecast_dates.strftime('%Y-%m-%d'))
    actual_value = st.number_input("实际值", min_value=0.0, step=1.0, format="%.2f")

    if st.button("✅ 提交实际值", type="primary", use_container_width=True):
        st.session_state.actual_values[selected_date] = actual_value
        st.success(f"已记录 {selected_date} 的实际值：{actual_value:.2f}")
        st.rerun()

    if st.session_state.actual_values:
        if st.button("🗑️ 清空所有记录", use_container_width=True):
            st.session_state.actual_values = {}
            st.rerun()

with col2:
    if st.session_state.actual_values:
        actual_df = pd.DataFrame([
            {'日期': k, '实际值': v} for k, v in sorted(st.session_state.actual_values.items())
        ])
        st.dataframe(actual_df, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:#90a4ae">
          <div style="font-size:2.5rem;margin-bottom:0.5rem">📋</div>
          <p>暂无实际值记录<br>在左侧选择日期并输入实际值</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Comparison Section ──
if st.session_state.actual_values:
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    forecast_df = pd.DataFrame({
        '日期': forecast_dates.strftime('%Y-%m-%d'),
        '预测值': [round(v, 2) for v in forecast_result['forecast']]
    })

    actual_df = pd.DataFrame([
        {'日期': k, '实际值': v} for k, v in st.session_state.actual_values.items()
    ])

    comparison_df = forecast_df.merge(actual_df, on='日期', how='left')
    comparison_df['误差'] = comparison_df.apply(
        lambda row: round(abs(row['预测值'] - row['实际值']), 2) if pd.notna(row.get('实际值')) else None,
        axis=1
    )
    comparison_df['误差率 (%)'] = comparison_df.apply(
        lambda row: round(abs(row['预测值'] - row['实际值']) / row['实际值'] * 100, 2)
        if pd.notna(row.get('实际值')) and row['实际值'] != 0 else None,
        axis=1
    )

    valid = comparison_df.dropna(subset=['实际值'])

    if len(valid) > 0:
        mae  = float(valid['误差'].mean())
        mape = float(valid['误差率 (%)'].mean())
        accuracy = max(0, 100 - mape)

        quality_color = "#43a047" if mape < 10 else "#fb8c00" if mape < 20 else "#e53935"
        quality_label = "优秀" if mape < 10 else "良好" if mape < 20 else "需优化"

        st.markdown(f"""
        <div class="metric-row">
          <div class="metric-card blue">
            <div class="m-icon">📉</div>
            <div class="m-value">{mae:.2f}</div>
            <div class="m-label">平均绝对误差 MAE</div>
          </div>
          <div class="metric-card orange">
            <div class="m-icon">📊</div>
            <div class="m-value">{mape:.2f}%</div>
            <div class="m-label">平均误差率 MAPE</div>
          </div>
          <div class="metric-card green">
            <div class="m-icon">🎯</div>
            <div class="m-value">{accuracy:.2f}%</div>
            <div class="m-label">预测准确度</div>
          </div>
          <div class="metric-card purple">
            <div class="m-icon">⭐</div>
            <div class="m-value" style="color:{quality_color}">{quality_label}</div>
            <div class="m-label">综合评级</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 预测 vs 实际对比")
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Recommendation ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 💡 迭代建议")

    if len(valid) > 0:
        if mape < 10:
            st.markdown("""
            <div class="ai-box">
              <div class="ai-tag">✅ 模型表现优秀</div>
              <p>当前模型预测精度高，误差率低于 10%，可继续使用。建议定期（每月）补充新数据重新训练，保持模型的时效性。</p>
            </div>
            """, unsafe_allow_html=True)
        elif mape < 20:
            st.markdown("""
            <div class="ai-box">
              <div class="ai-tag">🟡 模型表现良好</div>
              <p>误差率在 10%–20% 之间，属于可接受范围。建议持续监控误差变化趋势，若误差持续上升则考虑重新训练。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ai-box" style="border-left-color:#e53935;background:linear-gradient(135deg,#ffebee,#fff3f3)">
              <div class="ai-tag" style="background:#e53935;color:white">⚠️ 建议重新训练</div>
              <p>误差率超过 20%，模型预测偏差较大。建议：</p>
              <ul>
                <li>收集更多历史数据后重新训练</li>
                <li>检查数据中是否存在异常值或趋势突变</li>
                <li>尝试切换到更复杂的模型（如 XGBoost 或 LSTM）</li>
                <li>考虑引入外部特征（促销活动、节假日等）</li>
              </ul>
            </div>
            """, unsafe_allow_html=True)

        if mape >= 20:
            if st.button("🔄 重新训练模型", type="primary", use_container_width=True):
                for k in ['model_results', 'model_engine', 'future_forecast']:
                    st.session_state.pop(k, None)
                st.switch_page("pages/3_🤖_Model_Training.py")

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("← 返回预测报告", use_container_width=True):
        st.switch_page("pages/4_📈_Forecast_Report.py")
with col2:
    if st.button("🏠 重新开始", use_container_width=True):
        st.switch_page("pages/1_🏢_Industry_Setup.py")
