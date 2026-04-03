import streamlit as st
from modules.session_manager import init_session_state
from modules.model_engine import ModelEngine
from modules.gpt_agent import GPTAgent
import pandas as pd
import time

st.set_page_config(page_title="模型训练 — ForecastAI", page_icon="🤖", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

if st.session_state.get('train_data') is None or st.session_state.get('test_data') is None:
    st.warning("⚠️ 请先完成数据上传和验证")
    if st.button("← 返回数据上传"):
        st.switch_page("pages/2_📊_Data_Upload.py")
    st.stop()

# ── Step Progress ──
st.markdown("""
<div class="step-progress">
  <div class="step-item"><div class="step-circle done">✓</div><div class="step-label done">行业设定</div></div>
  <div class="step-line done"></div>
  <div class="step-item"><div class="step-circle done">✓</div><div class="step-label done">数据上传</div></div>
  <div class="step-line done"></div>
  <div class="step-item"><div class="step-circle active">3</div><div class="step-label active">模型训练</div></div>
  <div class="step-line"></div>
  <div class="step-item"><div class="step-circle">4</div><div class="step-label">预测报告</div></div>
  <div class="step-line"></div>
  <div class="step-item"><div class="step-circle">5</div><div class="step-label">反馈迭代</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="page-header">
  <h1>🤖 第三步：模型训练与对比</h1>
  <p>预测目标：{st.session_state.get('forecast_target','—')} &nbsp;|&nbsp;
     训练集：{len(st.session_state.train_data)} 条 &nbsp;|&nbsp;
     测试集：{len(st.session_state.test_data)} 条</p>
</div>
""", unsafe_allow_html=True)

# ── Training ──
if not st.session_state.get('model_results'):
    st.markdown("""
    <div class="section-card" style="text-align:center;padding:2.5rem">
      <div style="font-size:3rem;margin-bottom:1rem">🧠</div>
      <h3 style="color:#1a237e;margin-bottom:0.5rem">准备好了吗？</h3>
      <p style="color:#78909c;margin-bottom:1.5rem">
        系统将自动训练 <strong>移动平均、指数平滑、ARIMA</strong> 等多个模型，<br>
        并按测试集误差排名，为您推荐最优方案。
      </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 开始训练所有模型", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="初始化...")
            status = st.empty()

            engine = ModelEngine()
            train_df = st.session_state.train_data
            test_df  = st.session_state.test_data
            date_col = st.session_state.date_column
            target_col = st.session_state.target_column
            has_seasonality = st.session_state.get('has_seasonality', False)

            progress_bar.progress(20, text="训练移动平均模型...")
            time.sleep(0.3)
            progress_bar.progress(50, text="训练指数平滑模型...")
            time.sleep(0.3)
            progress_bar.progress(75, text="训练 ARIMA 模型...")

            results = engine.train_all_models(train_df, test_df, date_col, target_col, has_seasonality)

            progress_bar.progress(100, text="✅ 训练完成！")
            time.sleep(0.4)

            st.session_state.model_results = results
            st.session_state.model_engine = engine
            st.rerun()

else:
    results = st.session_state.model_results
    if not results:
        st.warning("模型训练未产生结果，请重新训练")
        if st.button("重新训练"):
            del st.session_state['model_results']
            st.rerun()
        st.stop()

    best = results[0]
    mape = best['metrics']['MAPE']
    quality = "🟢 优秀" if mape < 10 else "🟡 良好" if mape < 20 else "🔴 可接受"

    # ── Winner Banner ──
    st.markdown(f"""
    <div class="winner-banner">
      <div class="trophy">🏆</div>
      <div class="info">
        <h3>{best['model_name']}</h3>
        <p>MAPE {mape:.2f}% &nbsp;·&nbsp; RMSE {best['metrics']['RMSE']:.2f}
           &nbsp;·&nbsp; R² {best['metrics']['R²']:.4f} &nbsp;·&nbsp; 质量评级 {quality}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics ──
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card blue">
        <div class="m-icon">📉</div>
        <div class="m-value">{best['metrics']['MAE']:.2f}</div>
        <div class="m-label">MAE</div>
      </div>
      <div class="metric-card orange">
        <div class="m-icon">📊</div>
        <div class="m-value">{best['metrics']['RMSE']:.2f}</div>
        <div class="m-label">RMSE</div>
      </div>
      <div class="metric-card green">
        <div class="m-icon">🎯</div>
        <div class="m-value">{mape:.2f}%</div>
        <div class="m-label">MAPE</div>
      </div>
      <div class="metric-card purple">
        <div class="m-icon">📈</div>
        <div class="m-value">{best['metrics']['R²']:.4f}</div>
        <div class="m-label">R²</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Model Comparison Table ──
    st.markdown("### 📊 全部模型对比")

    rows = []
    for i, r in enumerate(results):
        medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
        rows.append({
            "排名": medal,
            "模型": r['model_name'],
            "MAE": r['metrics']['MAE'],
            "RMSE": r['metrics']['RMSE'],
            "MAPE (%)": r['metrics']['MAPE'],
            "R²": r['metrics']['R²'],
        })

    df_cmp = pd.DataFrame(rows)
    st.dataframe(
        df_cmp.style.highlight_min(subset=["MAPE (%)"], color="#c8e6c9")
                    .highlight_max(subset=["R²"], color="#c8e6c9")
                    .format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "MAPE (%)": "{:.2f}", "R²": "{:.4f}"}),
        use_container_width=True, hide_index=True
    )

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── AI Analysis ──
    with st.expander("💡 AI 模型分析", expanded=True):
        st.markdown('<div class="ai-box"><div class="ai-tag">🤖 AI 分析</div>', unsafe_allow_html=True)
        gpt = GPTAgent()
        explanation = gpt.explain_model_selection({
            'best_model': best['model_name'],
            'mape': mape,
            'industry': st.session_state.get('industry'),
            'has_seasonality': st.session_state.get('has_seasonality', False)
        })
        st.markdown(explanation)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 重新训练", use_container_width=True):
            for k in ['model_results', 'model_engine']:
                st.session_state.pop(k, None)
            st.rerun()
    with col2:
        if st.button("查看预测结果 →", type="primary", use_container_width=True):
            st.switch_page("pages/4_📈_Forecast_Report.py")
