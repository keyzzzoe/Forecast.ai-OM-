import streamlit as st
from modules.session_manager import init_session_state, get_progress

st.set_page_config(
    page_title="ForecastAI - AI需求预测系统",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

# ── Sidebar ──
with st.sidebar:
    st.markdown("## 🔮 ForecastAI")
    st.caption("AI驱动的需求预测系统")
    st.divider()

    progress = get_progress()
    st.markdown(f"**📍 完成进度: {progress}%**")
    st.progress(progress / 100)

    st.divider()
    st.markdown("### 📋 操作步骤")
    steps = [
        ("1. 行业设定", st.session_state.industry is not None),
        ("2. 数据上传", st.session_state.data_validated),
        ("3. 模型分析", st.session_state.models_trained),
        ("4. 预测报告", st.session_state.report_generated),
        ("5. 反馈迭代", len(st.session_state.model_versions) > 1),
    ]
    for label, done in steps:
        icon = "✅" if done else "⬜"
        st.markdown(f"{icon} {label}")

    st.divider()

    # AI Chat Assistant
    st.markdown("### 💬 AI 助手")
    st.caption("有任何问题可以随时问我")

    for msg in st.session_state.chat_history[-5:]:
        role_icon = "🧑" if msg["role"] == "user" else "🤖"
        st.markdown(f"{role_icon} {msg['content']}")

    chat_input = st.text_input("输入问题...", key="sidebar_chat", label_visibility="collapsed")
    if chat_input:
        st.session_state.chat_history.append({"role": "user", "content": chat_input})
        # Mock response
        from modules.gpt_agent import GPTAgent
        agent = GPTAgent()
        response = agent.chat_response(chat_input, st.session_state)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    st.divider()
    st.markdown("### ⚙️ 设置")
    lang = st.selectbox("语言", ["中文", "English"], index=0, key="lang_select")

# ── Main Content ──
st.markdown("""
<div class="page-header" style="text-align:center;padding:2.5rem 2rem">
  <h1 style="font-size:2.4rem">🔮 ForecastAI</h1>
  <p style="font-size:1.05rem;opacity:0.9">AI 驱动的需求预测系统 · 为运营管理者而生</p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:2.2rem;margin-bottom:0.6rem">🏢</div>
        <h3>跨行业通用</h3>
        <p>支持零售、医疗、电商、航空等多个行业，内置行业知识库</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:2.2rem;margin-bottom:0.6rem">🤖</div>
        <h3>全自动建模</h3>
        <p>自动训练 6+ 个预测模型，AI 智能推荐最优方案</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:2.2rem;margin-bottom:0.6rem">📊</div>
        <h3>精致可视化</h3>
        <p>交互式预测图表，置信区间展示，一键导出 PDF 报告</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size:2.2rem;margin-bottom:0.6rem">🔄</div>
        <h3>持续进化</h3>
        <p>录入真实数据验证精度，误差超标自动触发重训练</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# Workflow steps
st.markdown("""
<div class="section-card">
  <h3>🗺️ 五步完成需求预测</h3>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.8rem;margin-top:1rem;text-align:center">
    <div style="padding:1rem;background:#e3f2fd;border-radius:12px">
      <div style="font-size:1.8rem">🏢</div>
      <div style="font-weight:700;color:#1565c0;margin-top:0.3rem">行业设定</div>
      <div style="font-size:0.78rem;color:#78909c;margin-top:0.2rem">选择行业，填写预测目标</div>
    </div>
    <div style="padding:1rem;background:#e8f5e9;border-radius:12px">
      <div style="font-size:1.8rem">📊</div>
      <div style="font-weight:700;color:#2e7d32;margin-top:0.3rem">数据上传</div>
      <div style="font-size:0.78rem;color:#78909c;margin-top:0.2rem">上传 CSV 或使用示例数据</div>
    </div>
    <div style="padding:1rem;background:#fff3e0;border-radius:12px">
      <div style="font-size:1.8rem">🤖</div>
      <div style="font-weight:700;color:#e65100;margin-top:0.3rem">模型训练</div>
      <div style="font-size:0.78rem;color:#78909c;margin-top:0.2rem">自动训练并对比多个模型</div>
    </div>
    <div style="padding:1rem;background:#f3e5f5;border-radius:12px">
      <div style="font-size:1.8rem">📈</div>
      <div style="font-weight:700;color:#6a1b9a;margin-top:0.3rem">预测报告</div>
      <div style="font-size:0.78rem;color:#78909c;margin-top:0.2rem">查看预测图表，下载报告</div>
    </div>
    <div style="padding:1rem;background:#fce4ec;border-radius:12px">
      <div style="font-size:1.8rem">🔄</div>
      <div style="font-weight:700;color:#880e4f;margin-top:0.3rem">反馈迭代</div>
      <div style="font-size:0.78rem;color:#78909c;margin-top:0.2rem">录入实际值，持续优化</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

col_start, col_sample = st.columns(2)
with col_start:
    if st.button("▶️ 开始预测之旅", type="primary", use_container_width=True):
        st.switch_page("pages/1_🏢_Industry_Setup.py")
with col_sample:
    if st.button("📂 使用零售示例数据快速体验", use_container_width=True):
        st.session_state.industry = "retail"
        st.switch_page("pages/2_📊_Data_Upload.py")

st.markdown("---")
st.caption("ForecastAI v3.0 | AI-Powered Demand Forecasting System")
