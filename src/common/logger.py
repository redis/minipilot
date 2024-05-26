import logging
from logging.handlers import RotatingFileHandler

from src.common.config import MINIPILOT_LOG_LENGTH, MINIPILOT_LOG
from src.common.utils import get_db


class CustomHandler(logging.Handler):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flask_app = app

    def emit(self, record):
        log_message = self.format(record)
        with self.flask_app.app_context():
            get_db().xadd("minipilot:log",{"message":log_message}, maxlen=MINIPILOT_LOG_LENGTH)


def setup_logging(app):
    logger = logging.getLogger('root')
    max_log_size = 1024 * 1024 * 5 # 5 MB
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

    # A file system custom handler
    my_handler = RotatingFileHandler(filename=MINIPILOT_LOG,
                                     mode='a',
                                     maxBytes=max_log_size,
                                     backupCount=5,
                                     encoding=None,
                                     delay=0)

    my_handler.setFormatter(log_formatter)
    my_handler.setLevel(logging.WARNING)
    logger.addHandler(my_handler)

    # A Redis Stream custom handler
    custom_handler = CustomHandler(app)
    custom_handler.setFormatter(log_formatter)
    custom_handler.setLevel(logging.WARNING)
    logger.addHandler(custom_handler)


