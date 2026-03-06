import os
import re
import logging

logger = logging.getLogger(__name__)


def setup_logger(name: str):
    from utils.logger import setup_logger as _setup
    return _setup(name)


def ensure_output_dir(path: str):
    """Creates the output directory (including parents) if it does not exist."""
    if os.path.exists(path):
        logger.debug(f"[pdf_utils] Output directory already exists: {path}")
    else:
        os.makedirs(path, exist_ok=True)
        logger.info(f"[pdf_utils] Created output directory: {path}")


def validate_pdf_path(path: str):
    """Validates that the given path points to an existing .pdf file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Document not found: {path}")
    if not path.lower().endswith(".pdf"):
        raise ValueError(f"File does not appear to be a PDF: {path}")
    logger.debug(f"[pdf_utils] Document validated: {path}")


def sanitize_filename(name: str) -> str:
    """
    Removes characters that are invalid in filenames across major OS platforms
    and trims leading/trailing whitespace.
    """
    sanitized = re.sub(r'[\\/:*?"<>|]', "_", name).strip()
    logger.debug(f"[pdf_utils] Sanitized filename: '{name}' → '{sanitized}'")
    return sanitized
