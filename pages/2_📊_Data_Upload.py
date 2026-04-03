import streamlit as st
from modules.session_manager import init_session_state
from modules.data_processor import DataProcessor
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

# ── Step Progress ──
st.markdown("""
<div class="step-progress">
  <div class="step-item"><div class="step-circle done">✓</div><div class="step-label done">行业设定</div></div>
  <div class="step-line done"></div>
  <div class="step-item"><div class="step-circle active">2</div><div class="step-label active">数据上传</div></div>
  <div class="step-line"></div>
  <div class="step-item"><div class="step-circle">3</div><div class="step-label">模型训练</div></div>
  <div class="step-line"></div>
  <div class="step-item"><div class="step-circle">4</div><div class="step-label">预测报告</div></div>
  <div class="step-line"></div>
  <div class="step-item"><div class="step-circle">5</div><div class="step-label">反馈迭代</div></div>
</div>
""", unsafe_allow_html=True)

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
        col1, col2, col3 = st.columns([2, 1, 1])
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
                        st.rerun()
                    except Exception as e:
                        st.error(f"加载失败: {e}")

with tab2:
    st.markdown("""
    <div class="section-card">
      <h3>📋 数据格式要求</h3>
      <p style="color:#546e7a;font-size:0.9rem">
        • 支持 CSV / Excel 格式<br>
        • 必须包含 <strong>日期列</strong>（如 date、日期）和 <strong>数值列</strong>（如 sales、订单数）<br>
        • 建议至少 <strong>60 行</strong>以上数据，越多越准确
      </p>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "拖拽文件到此处，或点击上传",
        type=['csv', 'xlsx', 'xls'],
        label_visibility="collapsed"
    )
    if uploaded_file:
        try:
            processor = DataProcessor()
            df = processor.load_data(uploaded_file)
            st.session_state.uploaded_data = df
            st.session_state.data_source = "upload"
            st.success("✅ 文件上传成功！")
        except Exception as e:
            st.error(f"❌ 读取失败: {e}")
            st.stop()

# ── Data Preview ──
if st.session_state.get('uploaded_data') is not None:
    df = st.session_state.uploaded_data
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    src = "示例数据" if st.session_state.get('data_source') == "sample" else "用户上传"
    st.markdown(f"""
    <div class="metric-row">
      <div class="metric-card blue">
        <div class="m-icon">📋</div>
        <div class="m-value">{len(df):,}</div>
        <div class="m-label">数据行数</div>
      </div>
      <div class="metric-card green">
        <div class="m-icon">📐</div>
        <div class="m-value">{len(df.columns)}</div>
        <div class="m-label">列数</div>
      </div>
      <div class="metric-card orange">
        <div class="m-icon">🗂️</div>
        <div class="m-value">{src}</div>
        <div class="m-label">数据来源</div>
      </div>
      <div class="metric-card purple">
        <div class="m-icon">✅</div>
        <div class="m-value">{df.notna().sum().sum()}</div>
        <div class="m-label">有效数据点</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("👀 预览数据（前10行）", expanded=True):
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    # ── Column Mapping ──
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🗺️ 列映射")
    st.caption("告诉系统哪一列是日期，哪一列是要预测的目标值")

    with st.form("column_mapping"):
        col1, col2 = st.columns(2)
        with col1:
            date_column = st.selectbox("📅 日期列", options=df.columns.tolist())
        with col2:
            target_column = st.selectbox(
                "🎯 目标变量列",
                options=[c for c in df.columns if c != date_column]
            )
        submitted = st.form_submit_button("✅ 验证数据", type="primary", use_container_width=True)

        if submitted:
            with st.spinner("验证中..."):
                processor = DataProcessor()
                result = processor.validate_data(df, date_column, target_column)
            if result['valid']:
                summary = processor.get_data_summary()
                result.update(summary)
                st.session_state.date_column = date_column
                st.session_state.target_column = target_column
                st.session_state.validation_result = result
                st.session_state.processor = processor
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")

    st.markdown('</div>', unsafe_allow_html=True)

# ── Quality Report ──
if st.session_state.get('validation_result', {}).get('valid'):
    result = st.session_state.validation_result
    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section-card">
      <h3>📋 数据质量报告</h3>
      <div class="metric-row" style="margin-top:0.5rem">
        <div class="metric-card blue">
          <div class="m-icon">📊</div>
          <div class="m-value">{result['total_rows']:,}</div>
          <div class="m-label">有效数据点</div>
        </div>
        <div class="metric-card green">
          <div class="m-icon">📅</div>
          <div class="m-value" style="font-size:0.9rem">{result['date_range'][0]}</div>
          <div class="m-label">起始日期</div>
        </div>
        <div class="metric-card orange">
          <div class="m-icon">📅</div>
          <div class="m-value" style="font-size:0.9rem">{result['date_range'][1]}</div>
          <div class="m-label">结束日期</div>
        </div>
        <div class="metric-card purple">
          <div class="m-icon">🔄</div>
          <div class="m-value">{result.get('frequency','—')}</div>
          <div class="m-label">数据频率</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if result.get('missing_values', 0) > 0:
            st.warning(f"⚠️ 检测到 {result['missing_values']} 个缺失值，将自动填充")
        else:
            st.success("✅ 无缺失值")
    with col2:
        if result.get('outliers', 0) > 0:
            st.info(f"ℹ️ 检测到 {result['outliers']} 个异常值（IQR方法）")
        else:
            st.success("✅ 无明显异常值")

    with st.expander("📈 数据统计摘要"):
        df = st.session_state.uploaded_data
        target_col = st.session_state.target_column
        st.dataframe(df[target_col].describe().to_frame().T, use_container_width=True)

    st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

    if st.button("🚀 开始模型训练 →", type="primary", use_container_width=True):
        with st.spinner("准备训练数据..."):
            processor = DataProcessor()
            df = st.session_state.uploaded_data
            date_col = st.session_state.date_column
            target_col = st.session_state.target_column
            ts_data = processor.prepare_time_series(df, date_col, target_col)
            st.session_state.ts_data = ts_data
            train, test = processor.split_train_test(ts_data)
            st.session_state.train_data = train
            st.session_state.test_data = test
        st.switch_page("pages/3_🤖_Model_Training.py")
