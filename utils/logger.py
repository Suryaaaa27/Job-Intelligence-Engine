import logging
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")


class JobLogger:

    _logger = None

    @classmethod
    def get_logger(cls):

        if cls._logger:
            return cls._logger

        os.makedirs(_LOG_DIR, exist_ok=True)

        logger = logging.getLogger("JobIntelligence")

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s"
        )

        console = logging.StreamHandler()
        console.setFormatter(formatter)

        logfile = logging.FileHandler(
            os.path.join(_LOG_DIR, "system.log"),
            encoding="utf-8"
        )
        logfile.setFormatter(formatter)

        logger.addHandler(console)
        logger.addHandler(logfile)

        cls._logger = logger

        return logger