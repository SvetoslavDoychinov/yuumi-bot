import logging
import sys

from config import BotConfig


def configure_logger():
    """Configures bot logger"""
    # Create log files
    BotConfig.bot_logs_dir_path.mkdir(parents=True, exist_ok=True)

    # Configure logger
    steam_handler = logging.StreamHandler(stream=sys.stdout)
    file_handler = logging.FileHandler(BotConfig.bot_logs_path)
    steam_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    log_format = logging.Formatter("%(asctime)s:%(levelname)s:%(filename)s:%(funcName)s:%(lineno)s:%(message)s")
    steam_handler.setFormatter(log_format)
    file_handler.setFormatter(log_format)

    logger = logging.getLogger()
    logger.addHandler(steam_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
