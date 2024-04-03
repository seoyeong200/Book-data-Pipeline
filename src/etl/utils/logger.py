import logging

class Logging:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self.logFormatter = logging.Formatter(
            "%(asctime)s [%(levelname)-5.5s] [%(name)s] %(message)s"
            )
    
    def get_logger(self):
        self.logger.setLevel(logging.DEBUG)

        self.get_stream_handler()
        self.get_file_handler()

        return self.logger
    
    def get_stream_handler(self)-> None:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.logFormatter)
        self.logger.addHandler(handler)

    def get_file_handler(self)-> None:
        import os, datetime

        logPath = os.getenv('LOGPATH')
        fileName = datetime.datetime.today().strftime('%Y-%m-%d')
        self._make_dir_(logPath)
        handler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(self.logFormatter)
        self.logger.addHandler(handler)

    @staticmethod
    def _make_dir_(path: str):
        import os, errno
        try:
            os.makedirs(path, exist_ok=True)  
        except TypeError:
            try:
                os.makedirs(path)
            except OSError as exc: 
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else: raise 