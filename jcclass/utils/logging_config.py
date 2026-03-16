import logging


def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a library-safe logger.
    Attaches a NullHandler by default so that log records are silently
    discarded unless the *application* (not this library) configures logging.
    Users who want to see log output can do:
        import logging
        logging.getLogger("jcclass").setLevel(logging.DEBUG)
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger
