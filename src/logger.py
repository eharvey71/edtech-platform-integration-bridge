import logging
from logging.handlers import RotatingFileHandler

# Set up the log file path
log_file_path = "./logs/log"

# Configure the logger
logger = logging.getLogger("RotatingLog")
logger.setLevel(logging.INFO)

# Add a rotating file handler
handler = RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def log(message):
    logger.info(message)

