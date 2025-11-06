# ================================
# 📜 Logging Setup
# ================================

# Importing required libraries
import logging                # Python's built-in logging module
import os                     # To handle file paths and directories
from datetime import datetime # To generate unique log filenames with timestamps



# ================================
# 🕒 Create log file name with timestamp
# ================================
# Example: "23_09_2025_11_55_30.log"
LOG_FILE = f"{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.log"

# Why? 
# - Ensures every run of the pipeline has a unique log file.
# - Helps in debugging later (logs are separated per run).
# - Makes audit trail possible in production.



# ================================
# 📂 Create "logs" folder if not exists
# ================================
logs_path = os.path.join(os.getcwd(), "logs")   # "current_directory/logs"
os.makedirs(logs_path, exist_ok=True)           # create folder, do nothing if already exists

# Why?
# - Keeps logs organized in a separate folder.
# - `exist_ok=True` prevents error if folder already exists.



# ================================
# 📄 Full path for current log file
# ================================
LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Example:
# /home/rudra/project/logs/23_09_2025_11_55_30.log



# ================================
# ⚙️ Logging configuration
# ================================
logging.basicConfig(
    filename = LOG_FILE_PATH,   # Where logs will be saved
    format = "[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s ",
    level = logging.INFO,       # Logging level: INFO and above (INFO, WARNING, ERROR, CRITICAL)
)

# Explanation of format:
# - %(asctime)s → Timestamp of the log
# - %(lineno)d  → Line number where the log was generated
# - %(name)s    → Logger name (usually module/package name)
# - %(levelname)s → Logging level (INFO, ERROR, etc.)
# - %(message)s → The actual log message

# Why?
# - Logs provide visibility into your pipeline execution.
# - In production, logs are critical for debugging issues.
# - You’re setting INFO level (good default) → logs all important info without overwhelming debug noise.
