import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
USE_REAL_API = False  # Set to True when OpenAI API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model Configuration
DEFAULT_FORECAST_HORIZON = 30
TRAIN_TEST_SPLIT_RATIO = 0.8
ERROR_THRESHOLD_PERCENT = 15.0

# Supported Industries
INDUSTRIES = {
    "retail": "零售业",
    "healthcare": "医疗健康",
    "ecommerce": "电商",
    "aviation": "航空"
}
