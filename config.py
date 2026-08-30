import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
DATABASE_PATH = os.getenv("DATABASE_PATH")

API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

LOG_FILE = "etl_pipeline.log"