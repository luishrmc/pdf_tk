import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """
    Creates and returns a logger that writes to stdout with a consistent
    format showing timestamp, level, and module name.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # avoid adding duplicate handlers on re-import

    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
