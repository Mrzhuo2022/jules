import logging
import sys

def setup_logging():
    """
    Configures the root logger for the application.

    This setup directs log output to both a file (`app.log`) and
    standard output, making logs accessible whether running directly
    or as a background service.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Logging configured.")
