import logging
import json
import datetime

from gunicorn import glogging

class GunicornLoggerOverride(glogging.Logger):
    """Make the Gunicorn Logger propagate messages to the root handler."""

    def __init__(self, cfg):
        super().__init__(cfg)
        self.access_log.propagate = True
        self.error_log.propagate = True
        for handler in self.access_log.handlers:
            self.access_log.handlers.remove(handler)
        for handler in self.error_log.handlers:
            self.error_log.handlers.remove(handler)

class CustomLoggingFormatter(logging.Formatter):
    def __init__(self):
        super(CustomLoggingFormatter, self).__init__()

    def format(self, record):
        record.message = record.getMessage()
        input_data = {
            "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.message,
            "name": record.name,
        }
        if record.name == "uvicorn.access":
            try:
                input_data['method'] = record.args[1]
                input_data['endpoint'] = record.args[2]
                input_data['status'] = record.args[5]
            except:
                pass
        return json.dumps(input_data)

def setup_logging():
    import sys
    import os

    old_stdout = sys.stdout # backup current stdout
    old_stderr = sys.stderr # backup current stdout
    #sys.stdout = open(os.devnull, "w")
    #sys.stderr = open(os.devnull, "w")
    # sys.stdout = old_stdout # reset old stdout

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setStream(old_stderr)
    formatter = CustomLoggingFormatter()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
