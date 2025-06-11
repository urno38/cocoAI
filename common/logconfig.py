import logging
import sys
from pathlib import Path


def configure_logger():
    # Create a custom logger
    logfile = Path(Path(sys.argv[0]).name).with_suffix(".log")
    logger = logging.getLogger("cocoAI")
    logger.setLevel(logging.DEBUG)  # Set the minimum log level for the logger

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(logfile, mode="w", encoding="utf-8")

    # Set the logging level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # Create formatters and add them to handlers
    console_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # print(f"logfile available {logfile.resolve()}")
    return logger


LOGGER = configure_logger()


if __name__ == "__main__":

    # Configure the logger

    # Example usage
    LOGGER.debug("This is a debug message with a special character: é.")
    LOGGER.info("This is an info message.")
    LOGGER.warning("This is a warning message.")
    LOGGER.error("This is an error message.")
    LOGGER.critical("This is a critical message.")
