import streamlit as st
from modules.session_manager import init_session_state
from modules.data_processor import DataProcessor
from modules.ai_assistant import get_progress_html, get_ai_assistant_html
import pandas as pd
import config

st.set_page_config(page_title="数据上传 — ForecastAI", page_icon="📊", layout="wide")

with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

init_session_state()

if not st.session_state.get('industry'):
    st.warning("⚠️ 请先完成第一步：行业设定")
    if st.button("← 返回行业设定"):
        st.switch_page("pages/1_🏢_Industry_Setup.py")
    st.stop()

# ── Enhanced Progress Bar ──
st.markdown(get_progress_html(current_step=2, completed_steps=[1]), unsafe_allow_html=True)

# ── AI Assistant ──
st.markdown(get_ai_assistant_html(step=2), unsafe_allow_html=True)

industry_labels = {"retail": "零售业", "healthcare": "医疗健康", "ecommerce": "电商", "aviation": "航空"}
ind_label = industry_labels.get(st.session_state.industry, st.session_state.industry)

st.markdown(f"""
<div class="page-header">
  <h1>📊 第二步：数据上传</h1>
  <p>行业：{ind_label} &nbsp;|&nbsp; 预测目标：{st.session_state.get('forecast_target', 'N/A')}</p>
</div>
""", unsafe_allow_html=True)

# ── Sample Data ──
sample_datasets = {
    "retail":     ("🛒 零售业销售数据（730天）", "data/sample_datasets/retail_sales.csv"),
    "healthcare": ("🏥 医院就诊数据（730天）",   "data/sample_datasets/hospital_admissions.csv"),
    "ecommerce":  ("📦 电商订单数据（730天）",   "data/sample_datasets/ecommerce_orders.csv"),
    "aviation":   ("✈️ 航班预订数据（730天）",   "data/sample_datasets/flight_bookings.csv"),
}

industry = st.session_state.industry
tab1, tab2 = st.tabs(["📂 使用示例数据", "⬆️ 上传自己的数据"])

with tab1:
    if industry in sample_datasets:
        sample_name, sample_path = sample_datasets[industry]
        st.markdown(f"""
        <div class="section-card">
          <h3>🎯 推荐示例</h3>
          <p style="color:#546e7a;margin:0.5rem 0 1rem 0">
            我们为 <strong>{ind_label}</strong> 行业准备了真实感样本数据，包含趋势、季节性和随机波动，适合快速体验完整流程。
          </p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📄 {sample_name}")
        with col2:
            if st.button("加载示例数据", type="primary", use_container_width=True):
                with st.spinner("加载中..."):
                    try:
                        processor = DataProcessor()
                        df = processor.load_data(sample_path)
                        st.session_state.uploaded_data = df
                        st.session_state.data_source = "sample"
                        st.success("✅ 示例数据加载成功！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"加载失败: {e}")

with tab2:
    st.markdown("""
    <div class="section-card">
      <h3>📤 上传您的数据文件</h3>
      <p style="color:#546e7a;margin:0.5rem 0">
        支持 CSV 格式，需包含日期列和数值列。建议至少 60 天历史数据。
      </p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "选择 CSV 文件",
        type=["csv"],
        help="文件需包含日期列（如 2024-01-01）和数值列（您的预测目标）"
    )

    if uploaded_file:
        if st.button("确认上传", type="primary", use_container_width=True):
            with st.spinner("处理中..."):
                try:
                    processor = DataProcessor()
                    df = processor.load_data(uploaded_file)
                    st.session_state.uploaded_data = df
                    st.session_state.data_source = "upload"
                    st.success("✅ 文件上传成功！")
                    st.rerun()
                except Exception as e:
                    st.error(f"上传失败: {e}")

# ── Data Preview & Validation ──
if st.session_state.get('uploaded_data') is not None:
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    df = st.session_state.uploaded_data

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 📋 数据预览")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总行数", f"{len(df):,}")
    with col2:
        st.metric("总列数", len(df.columns))
    with col3:
        st.metric("数据来源", "示例数据" if st.session_state.data_source == "sample" else "上传文件")
    with col4:
        st.metric("状态", "✅ 已加载")

    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Column Selection ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 选择数据列")

    col1, col2 = st.columns(2)
    with col1:
        date_column = st.selectbox(
            "日期列",
            options=df.columns.tolist(),
            help="选择包含日期的列"
        )
    with col2:
        target_column = st.selectbox(
            "预测目标列",
            options=df.columns.tolist(),
            index=1 if len(df.columns) > 1 else 0,
            help="选择要预测的数值列"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Validate & Continue ──
    if st.button("✅ 验证数据并继续 →", type="primary", use_container_width=True):
        with st.spinner("验证中..."):
            processor = DataProcessor()
            result = processor.validate_data(df, date_column, target_column)

            if result['valid']:
                summary = processor.get_data_summary()
                st.session_state.date_column = date_column
                st.session_state.target_column = target_column
                st.session_state.data_validated = True

                date_start, date_end = summary['date_range']
                mean_val = summary.get('mean', 0)
                st.success(f"""
                ✅ 数据验证通过！

                - 数据范围：{date_start} 至 {date_end}
                - 总天数：{summary['total_rows']} 天
                - 平均值：{mean_val:.2f}
                """)
                st.balloons()
                st.switch_page("pages/3_🤖_Model_Training.py")
            else:
                st.error(f"❌ 数据验证失败：{result['message']}")

else:
    st.info("👆 请先加载示例数据或上传您的数据文件")
