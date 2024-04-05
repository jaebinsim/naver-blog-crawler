import os
import sys
from datetime import datetime
import logging


class LoggingConfig:
    @staticmethod
    def setup_logging():
        formatter = logging.Formatter('(NBC) %(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        log_dir = os.path.join(os.getcwd(), "Logs")
        os.makedirs(log_dir, exist_ok=True)

        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(log_dir, f"{current_time}.log")

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception


LoggingConfig.setup_logging()
