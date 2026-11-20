import logging
from pathlib import Path


def configure_logging(log_directory: str | Path = "logs") -> logging.Logger:
    directory = Path(log_directory)
    directory.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("toolmate")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = logging.FileHandler(directory / "toolmate.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
