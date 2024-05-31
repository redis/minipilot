from enum import Enum
import redis
from src.prompt.Prompt import Prompt
from src.prompt.templates.default_system_prompt import system_template
from src.prompt.templates.default_user_prompt import user_template


class Type(Enum):
    USER = 'user'
    SYSTEM = 'system'

class PromptManager:
    def __init__(self, app):
        self.app = app
        self.conn = redis.Redis(connection_pool=app.pool, decode_responses=True)
        if not self.conn.exists('minipilot:prompt:user'):
            self.load_defaults()

    def load_defaults(self):
        prompt = Prompt(title="Default user prompt", content=user_template, category=Type.USER.value)
        self.conn.hset('minipilot:prompt:user', mapping=prompt.to_dict())

        prompt = Prompt("Default system prompt", system_template, category=Type.SYSTEM.value)
        self.conn.hset('minipilot:prompt:system', mapping=prompt.to_dict())
        return

    def get_user_prompt(self):
        data = self.conn.hgetall(f'minipilot:prompt:user')
        return data

    def get_system_prompt(self):
        data = self.conn.hgetall(f'minipilot:prompt:system')
        return data

    def update_prompt(self, data):
        return self.conn.hset(f"minipilot:prompt:{data['prompt']}", 'content', data['content'])



