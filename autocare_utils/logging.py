# ================================
# 📜 Logging Setup (Pipeline-Aware)
# ================================

import logging
import os
from datetime import datetime


# ==========================================================
# ⚙️ Dynamic Path Configuration Based on Pipeline (DIABETES)
# ==========================================================

# You can set these from your pipeline's test.py before importing this file:
# os.environ["PIPELINE_ROOT"] = "machine_learning/training/diabetes/diabetes_work"
# os.environ["PIPELINE_NAME"] = "diabetes"

PIPELINE_ROOT = os.getenv("PIPELINE_ROOT", os.getcwd())     # Default → current dir if not set
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "autocare")      # Default → generic name if not set

# ---------------------------
# 📂 Logs folder path
# ---------------------------
logs_dir = os.path.join(PIPELINE_ROOT, "logs")
os.makedirs(logs_dir, exist_ok=True)

# ---------------------------
# 🕒 Timestamped log file name
# ---------------------------
LOG_FILE = f"{PIPELINE_NAME}_training_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

# Example:
# For Diabetes:
# machine_learning/training/diabetes/diabetes_work/logs/diabetes_training_08_11_2025_14_35_27.log
#
# For others (if not configured):
# <current_working_dir>/logs/autocare_training_08_11_2025_14_35_27.log


# ==========================================================
# 🧩 Configure Logging
# ==========================================================
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s",
    level=logging.INFO,   # Default level: INFO → can be overridden using logging.getLogger().setLevel()
)

# Expose root logger for consistency
logger = logging.getLogger()
