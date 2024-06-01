from src.common.config import MINIPILOT_CONVERSATION_LENGTH
from src.core.RedisConnection import RedisConnection


class Core(RedisConnection):
    def __init__(self):
        super().__init__()

    def log(self, session_id, question, answer, ttft, etel):
        data = {'session': session_id,
                'question': question,
                'answer': answer,
                'ttft': ttft,
                'etel': etel}
        self.conn.xadd("minipilot:conversation", data, maxlen=MINIPILOT_CONVERSATION_LENGTH)
