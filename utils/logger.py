import logging
import os


class JobLogger:

    _logger = None

    @classmethod
    def get_logger(cls):

        if cls._logger:
            return cls._logger

        os.makedirs("logs", exist_ok=True)

        logger = logging.getLogger("JobIntelligence")

        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(

            "[%(asctime)s] "

            "[%(levelname)s] "

            "%(message)s"

        )

        console = logging.StreamHandler()

        console.setFormatter(formatter)

        logfile = logging.FileHandler(

            "logs/system.log",

            encoding="utf-8"

        )

        logfile.setFormatter(formatter)

        logger.addHandler(console)

        logger.addHandler(logfile)

        cls._logger = logger

        return logger