import streamlit as st

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        # Page 1: Industry Setup
        'industry': None,
        'company_name': '',
        'forecast_target': '',
        'planning_horizon': 30,
        'has_seasonality': False,

        # Page 2: Data Upload
        'uploaded_data': None,
        'data_validated': False,
        'date_column': None,
        'target_column': None,
        'data_frequency': None,

        # Page 3: Model Training
        'models_trained': False,
        'model_results': None,
        'best_model': None,
        'best_model_name': None,

        # Page 4: Forecast Report
        'forecast_data': None,
        'report_generated': False,

        # Page 5: Feedback Iteration
        'model_versions': [],
        'current_version': 1,

        # AI Chat
        'chat_history': []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_from_page(page_num):
    """Reset session state from a specific page onwards"""
    if page_num <= 2:
        st.session_state.data_validated = False
        st.session_state.uploaded_data = None
    if page_num <= 3:
        st.session_state.models_trained = False
        st.session_state.model_results = None
        st.session_state.best_model = None
    if page_num <= 4:
        st.session_state.forecast_data = None
        st.session_state.report_generated = False

def get_progress():
    """Calculate overall progress percentage"""
    progress = 0
    if st.session_state.industry:
        progress += 20
    if st.session_state.data_validated:
        progress += 20
    if st.session_state.models_trained:
        progress += 30
    if st.session_state.report_generated:
        progress += 30
    return progress
