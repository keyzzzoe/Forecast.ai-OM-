import streamlit as st
from modules.session_manager import init_session_state
from modules.ai_assistant import get_progress_html, get_ai_assistant_html
import config

st.set_page_config(page_title="行业设定 — ForecastAI", page_icon="🏢", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

# ── Enhanced Progress Bar ──
st.markdown(get_progress_html(current_step=1, completed_steps=[]), unsafe_allow_html=True)

# ── AI Assistant ──
st.markdown(get_ai_assistant_html(step=1), unsafe_allow_html=True)

# ── Page Header ──
st.markdown("""
<div class="page-header">
  <h1>🏢 第一步：行业设定</h1>
  <p>选择您所在的行业，填写预测目标，系统将为您定制专属预测方案</p>
</div>
""", unsafe_allow_html=True)

# ── Industry Selection ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 选择您的行业")

selected_industry = st.session_state.get('industry')

industries = {
    "retail":     ("🛒", "零售业",  "库存 · 销售 · 客流"),
    "healthcare": ("🏥", "医疗健康", "就诊 · 床位 · 药品"),
    "ecommerce":  ("📦", "电商",    "订单 · GMV · 用户"),
    "aviation":   ("✈️", "航空",    "客座 · 货运 · 收益"),
}

cols = st.columns(4)
for i, (ind_id, (icon, label, desc)) in enumerate(industries.items()):
    with cols[i]:
        selected_cls = "selected" if selected_industry == ind_id else ""
        st.markdown(f"""
        <div class="industry-card {selected_cls}">
          <span class="icon">{icon}</span>
          <div class="label">{label}</div>
          <div class="desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("选择" if selected_industry != ind_id else "✓ 已选择",
                     key=f"btn_{ind_id}", use_container_width=True,
                     type="primary" if selected_industry == ind_id else "secondary"):
            st.session_state.industry = ind_id
            st.rerun()

if selected_industry:
    icon, label, _ = industries[selected_industry]
    st.success(f"✅ 已选择行业：{icon} **{label}**")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Setup Form ──
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 📝 填写预测信息")

col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input(
        "公司 / 部门名称",
        value=st.session_state.get('company_name', ''),
        placeholder="例如：XX零售连锁",
        help="填写您的公司或部门名称"
    )
with col2:
    forecast_target = st.text_input(
        "预测目标",
        value=st.session_state.get('forecast_target', ''),
        placeholder="例如：日销售额、订单数、客流量",
        help="具体说明您要预测的指标"
    )

col3, col4 = st.columns(2)
with col3:
    planning_horizon = st.slider(
        "预测周期（天）",
        min_value=7, max_value=180,
        value=st.session_state.get('planning_horizon', 30),
        step=7,
        help="预测未来多少天的需求，建议 30-90 天"
    )
with col4:
    has_seasonality = st.toggle(
        "数据有明显季节性 / 周期性",
        value=st.session_state.get('has_seasonality', False),
        help="例如：周末客流高、节假日销售旺季"
    )

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Industry Knowledge Preview ──
if selected_industry:
    icon, label, _ = industries[selected_industry]
    with st.expander(f"💡 {icon} {label} 行业洞察", expanded=False):
        from modules.rag_module import RAGModule
        rag = RAGModule()
        st.markdown(rag.get_industry_overview(selected_industry))

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Submit Button ──
if st.button("✅ 保存并继续 →", type="primary", use_container_width=True):
    if not selected_industry:
        st.error("❌ 请先选择行业")
    elif not company_name or not forecast_target:
        st.error("❌ 请填写公司名称和预测目标")
    else:
        st.session_state.company_name = company_name
        st.session_state.forecast_target = forecast_target
        st.session_state.planning_horizon = planning_horizon
        st.session_state.has_seasonality = has_seasonality
        st.balloons()
        st.switch_page("pages/2_📊_Data_Upload.py")
