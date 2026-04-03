import streamlit as st
from modules.session_manager import init_session_state
from modules.visualizer import Visualizer
from modules.gpt_agent import GPTAgent
from modules.report_generator import ReportGenerator
from modules.ai_assistant import get_progress_html, get_ai_assistant_html
import pandas as pd

st.set_page_config(page_title="预测报告 — ForecastAI", page_icon="📈", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

if st.session_state.get('model_results') is None:
    st.warning("⚠️ 请先完成模型训练")
    if st.button("← 返回模型训练"):
        st.switch_page("pages/3_🤖_Model_Training.py")
    st.stop()

# ── Enhanced Progress Bar ──
st.markdown(get_progress_html(current_step=4, completed_steps=[1, 2, 3]), unsafe_allow_html=True)

# ── AI Assistant ──
st.markdown(get_ai_assistant_html(step=4), unsafe_allow_html=True)

best_model = st.session_state.model_results[0]
engine = st.session_state.model_engine
mape = best_model['metrics']['MAPE']
quality = "🟢 优秀" if mape < 10 else "🟡 良好" if mape < 20 else "🔴 可接受"

st.markdown(f"""
<div class="page-header">
  <h1>📈 第四步：预测报告</h1>
  <p>最佳模型：{best_model['model_name']} &nbsp;|&nbsp;
     预测目标：{st.session_state.get('forecast_target','—')} &nbsp;|&nbsp;
     预测周期：{st.session_state.get('planning_horizon', 30)} 天</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ──
st.markdown(f"""
<div class="metric-row">
  <div class="metric-card blue">
    <div class="m-icon">🏆</div>
    <div class="m-value" style="font-size:1.1rem">{best_model['model_name']}</div>
    <div class="m-label">最佳模型</div>
  </div>
  <div class="metric-card green">
    <div class="m-icon">🎯</div>
    <div class="m-value">{mape:.2f}%</div>
    <div class="m-label">MAPE 误差率</div>
  </div>
  <div class="metric-card orange">
    <div class="m-icon">📅</div>
    <div class="m-value">{st.session_state.get('planning_horizon', 30)} 天</div>
    <div class="m-label">预测周期</div>
  </div>
  <div class="metric-card purple">
    <div class="m-icon">⭐</div>
    <div class="m-value" style="font-size:1rem">{quality}</div>
    <div class="m-label">模型质量</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Generate Forecast ──
if 'future_forecast' not in st.session_state:
    with st.spinner("生成预测中..."):
        forecast_result = engine.forecast_future(st.session_state.planning_horizon)
        st.session_state.future_forecast = forecast_result

forecast_result = st.session_state.future_forecast

# ── Forecast Chart ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 📊 预测结果可视化")

viz = Visualizer()
train_df = st.session_state.train_data
test_df  = st.session_state.test_data
date_col = st.session_state.date_column
target_col = st.session_state.target_column

fig = viz.plot_forecast(
    train_df, test_df,
    best_model['predictions'],
    forecast_result['forecast'],
    forecast_result['lower_bound'],
    forecast_result['upper_bound'],
    date_col, target_col
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Forecast Table ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 📋 预测数据明细")

last_date = pd.to_datetime(test_df[date_col].iloc[-1])
forecast_dates = pd.date_range(
    start=last_date + pd.Timedelta(days=1),
    periods=st.session_state.planning_horizon
)

forecast_df = pd.DataFrame({
    '日期': forecast_dates.strftime('%Y-%m-%d'),
    '预测值': [round(v, 2) for v in forecast_result['forecast']],
    '下界 (95%)': [round(v, 2) for v in forecast_result['lower_bound']],
    '上界 (95%)': [round(v, 2) for v in forecast_result['upper_bound']],
})

st.dataframe(forecast_df, use_container_width=True, hide_index=True)

csv = forecast_df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 下载预测数据 (CSV)",
    data=csv,
    file_name=f"forecast_{st.session_state.get('forecast_target','result')}.csv",
    mime="text/csv",
    use_container_width=True
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── AI Insights ──
with st.expander("💡 AI 趋势分析与业务建议", expanded=True):
    st.markdown('<div class="ai-box"><div class="ai-tag">🤖 AI 分析</div>', unsafe_allow_html=True)
    gpt = GPTAgent()
    context = {
        'industry': st.session_state.get('industry'),
        'forecast_target': st.session_state.get('forecast_target'),
        'best_model': best_model['model_name'],
        'mape': mape,
        'forecast_mean': float(forecast_result['forecast'].mean()),
        'forecast_trend': 'upward' if forecast_result['forecast'][-1] > forecast_result['forecast'][0] else 'downward',
        'planning_horizon': st.session_state.get('planning_horizon', 30),
    }
    insights = gpt.generate_business_insights(context)
    st.markdown(insights)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Model Details ──
with st.expander("🔍 模型详细参数"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**模型名称：** {best_model['model_name']}")
        st.markdown(f"**训练数据量：** {len(train_df):,} 条")
        st.markdown(f"**测试数据量：** {len(test_df):,} 条")
    with col2:
        for metric, value in best_model['metrics'].items():
            st.markdown(f"**{metric}：** {value:.4f}" if isinstance(value, float) else f"**{metric}：** {value}")

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── PDF Report ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 📄 生成完整报告")
st.caption("包含数据概览、模型对比、预测图表和业务建议的完整 PDF 报告")

if st.button("🖨️ 生成 PDF 报告", type="primary", use_container_width=True):
    with st.spinner("正在生成报告..."):
        try:
            report_gen = ReportGenerator()
            pdf_bytes = report_gen.generate_report(
                st.session_state,
                best_model,
                forecast_result,
                forecast_df
            )
            st.download_button(
                label="📥 下载 PDF 报告",
                data=pdf_bytes,
                file_name=f"forecast_report_{st.session_state.get('forecast_target','report')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"报告生成失败: {e}")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

if st.button("✅ 进入反馈迭代 →", type="primary", use_container_width=True):
    st.switch_page("pages/5_🔄_Feedback_Iteration.py")
