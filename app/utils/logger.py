import logging
from logging.handlers import RotatingFileHandler
import os

# Log file path from env or default
log_file = os.getenv("SHEPARD_LOG_FILE", "shepard_app.log")

# Rotating file handler to prevent huge log files
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)

# Create a logger for the whole app
logger = logging.getLogger("ShepardApp")
logger.setLevel(logging.INFO)  # Or DEBUG for more details
logger.addHandler(handler)

# Optional: print logs to console too
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
