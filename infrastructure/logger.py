import logging
import sys

def get_logger(name: str = "herpai") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Logger already configured

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
