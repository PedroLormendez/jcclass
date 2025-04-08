import logging


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with a given name and level.

    Args:
        name (str): Name of the logger.
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Avoid adding duplicate handlers
        logger.setLevel(level)
        handler = logging.StreamHandler()  # Output to console
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
