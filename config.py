import os
# API配置
API_KEY = os.environ["DEEPSEEK_API_KEY"]  # ← 运行时 set DEEPSEEK_API_KEY=你的key
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 评测配置
MAX_TOKENS = 500       # 每次回答最多500个token
TEMPERATURE = 0.7      # 创意程度，0=严谨，1=发散

# 输出路径
OUTPUT_DIR = "./output"
JSON_RESULT_FILE = "./output/eval_results.json"
REPORT_FILE = "./output/eval_report.html"
