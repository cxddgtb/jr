from loguru import logger
from pathlib import Path
import sys

def setup_logger(root: Path):
    log_dir = root / "data/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(log_dir / "runtime_{time:YYYY-MM-DD}.log", rotation="10 MB", retention="30 days", level="INFO")
    logger.add(sys.stdout, level="INFO", colorize=True)
    return logger
