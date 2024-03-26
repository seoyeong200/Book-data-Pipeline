import logging

class Logging:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_logger(self):
        logFormatter = logging.Formatter(
            "%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s"
            )
        
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logFormatter)

        logger = logging.getLogger(self.name)
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)

        return logger