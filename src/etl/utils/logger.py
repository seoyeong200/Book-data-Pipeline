import logging

class Logging:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_stream_logger(self):
        handler = logging.StreamHandler()
        return self.get_logger(handler)

    def get_file_logger(self):
        import os, datetime
        
        logPath = os.getenv('LOGPATH')
        fileName = datetime.datetime.today().strftime('%Y-%m-%d')
        handler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
        return self.get_logger(handler)

    def get_logger(self, handler):
        logFormatter = logging.Formatter(
            "%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s"
            )

        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logFormatter)

        logger = logging.getLogger(self.name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        return logger