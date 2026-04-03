import streamlit as st
from modules.session_manager import init_session_state
from modules.model_engine import ModelEngine
from modules.gpt_agent import GPTAgent
from modules.ai_assistant import get_progress_html, get_ai_assistant_html
import pandas as pd
import time

st.set_page_config(page_title="模型训练 — ForecastAI", page_icon="🤖", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

if not st.session_state.get('data_validated'):
    st.warning("⚠️ 请先完成数据上传和验证")
    if st.button("← 返回数据上传"):
        st.switch_page("pages/2_📊_Data_Upload.py")
    st.stop()

# ── Enhanced Progress Bar ──
st.markdown(get_progress_html(current_step=3, completed_steps=[1, 2]), unsafe_allow_html=True)

# ── AI Assistant ──
st.markdown(get_ai_assistant_html(step=3), unsafe_allow_html=True)

st.markdown(f"""
<div class="page-header">
  <h1>🤖 第三步：模型训练</h1>
  <p>AI 将自动训练多个预测模型，并为您选出最优方案</p>
</div>
""", unsafe_allow_html=True)

# ── Training Section ──
if st.session_state.get('model_results') is None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 开始训练")

    st.info("""
    **训练说明：**
    - 系统将自动训练 6+ 个预测模型
    - 根据数据量自动选择合适的算法
    - 使用 MAPE（平均绝对百分比误差）评估模型
    - 预计耗时：30 秒 - 2 分钟
    """)

    if st.button("🎯 开始训练模型", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Prepare data
            status_text.text("📊 准备训练数据...")
            progress_bar.progress(10)
            time.sleep(0.5)

            processor = st.session_state.data_processor
            train_df, test_df = processor.split_train_test()
            st.session_state.train_data = train_df
            st.session_state.test_data = test_df

            # Initialize engine
            status_text.text("🔧 初始化模型引擎...")
            progress_bar.progress(20)
            time.sleep(0.5)

            engine = ModelEngine(
                train_df,
                test_df,
                st.session_state.date_column,
                st.session_state.target_column,
                has_seasonality=st.session_state.get('has_seasonality', False)
            )
            st.session_state.model_engine = engine

            # Train models
            status_text.text("🤖 训练模型中（这可能需要 1-2 分钟）...")
            progress_bar.progress(40)

            results = engine.train_all_models()
            progress_bar.progress(90)

            # Save results
            st.session_state.model_results = results
            st.session_state.models_trained = True

            progress_bar.progress(100)
            status_text.text("✅ 训练完成！")
            time.sleep(0.5)

            st.success("🎉 模型训练成功！")
            st.balloons()
            st.rerun()

        except Exception as e:
            st.error(f"❌ 训练失败: {str(e)}")
            progress_bar.empty()
            status_text.empty()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ── Results Display ──
    results = st.session_state.model_results
    best_model = results[0]

    # Winner Banner
    st.markdown(f"""
    <div class="winner-banner">
        <div class="trophy">🏆</div>
        <div class="info">
            <h3>最佳模型：{best_model['model_name']}</h3>
            <p>MAPE: {best_model['metrics']['MAPE']:.2f}% |
               MAE: {best_model['metrics']['MAE']:.2f} |
               RMSE: {best_model['metrics']['RMSE']:.2f}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Performance Metrics ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📊 模型性能对比")

    # Metrics cards
    mape = best_model['metrics']['MAPE']
    quality = "🟢 优秀" if mape < 10 else "🟡 良好" if mape < 20 else "🔴 可接受"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("最佳模型", best_model['model_name'])
    with col2:
        st.metric("MAPE 误差率", f"{mape:.2f}%")
    with col3:
        st.metric("训练模型数", len(results))
    with col4:
        st.metric("模型质量", quality)

    # Comparison table
    comparison_data = []
    for i, model in enumerate(results):
        comparison_data.append({
            "排名": f"#{i+1}",
            "模型": model['model_name'],
            "MAPE (%)": f"{model['metrics']['MAPE']:.2f}",
            "MAE": f"{model['metrics']['MAE']:.2f}",
            "RMSE": f"{model['metrics']['RMSE']:.2f}",
            "R²": f"{model['metrics'].get('R2', 0):.3f}"
        })

    df_comparison = pd.DataFrame(comparison_data)

    # Style the dataframe
    def highlight_best(row):
        if row['排名'] == '#1':
            return ['background-color: #e8f5e9'] * len(row)
        return [''] * len(row)

    styled_df = df_comparison.style.apply(highlight_best, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── AI Explanation ──
    with st.expander("💡 AI 模型选择说明", expanded=False):
        st.markdown('<div class="ai-box"><div class="ai-tag">🤖 AI 分析</div>', unsafe_allow_html=True)
        gpt = GPTAgent()
        context = {
            'industry': st.session_state.get('industry'),
            'best_model': best_model['model_name'],
            'mape': mape,
            'data_points': len(st.session_state.train_data)
        }
        explanation = gpt.explain_model_selection(context)
        st.markdown(explanation)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Continue Button ──
    if st.button("✅ 查看预测报告 →", type="primary", use_container_width=True):
        st.switch_page("pages/4_📈_Forecast_Report.py")
