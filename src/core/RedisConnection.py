from src.common.utils import get_db


class RedisConnection:
    def __init__(self):
        self.conn = get_db()
