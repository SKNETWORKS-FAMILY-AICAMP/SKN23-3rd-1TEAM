import os
import dotenv

# 프로젝트 루트 디렉토리 동적으로 파악
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# .env 로드 로직
possible_env_paths = [
    os.path.join(PROJECT_ROOT, ".env"),
    os.path.join(os.getcwd(), ".env"),
]

loaded_env_path = None
for p in possible_env_paths:
    if os.path.exists(p):
        dotenv.load_dotenv(p, override=True)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            loaded_env_path = p
            break

# 상수 및 설정
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
EC2_INSTANCE_ID = os.getenv("EC2_INSTANCE_ID")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO_URL")

# 앱 전역 설정 값 상수화
REMOTE_DB_PATH = "3team/AI_Interviewer/db/interview.db"
REMOTE_APP_DIR = "~/3team/app"
REMOTE_APP_FILE = "app.py"
STREAMLIT_PORT = 8501
