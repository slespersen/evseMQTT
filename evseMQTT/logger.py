import logging

class Logger:
    def __init__(self):
        self.logger = logging.getLogger("evseBLE")
        logging.basicConfig(level=logging.DEBUG)
    
    def log_event(self, message):
        self.logger.info(message)
    
    def log_error(self, error):
        self.logger.error(error)
    
    def retrieve_logs(self):
        # This can be extended to retrieve logs from a file or other storage
        pass
