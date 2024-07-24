import os
import redis

from src.common.config import REDIS_CFG, MINIPILOT_HISTORY_ENABLED


# this object is read and used in the scope of the request. In the future, it should be a global object
# refreshed with client-side caching to update for changes initiated by some other application server
class ConfigProvider:
    def __init__(self, redis_host=REDIS_CFG["host"], redis_port=REDIS_CFG["port"], redis_password=REDIS_CFG["password"]):
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        self.config_key = 'minipilot:configuration'
        self.config = self._load_config()

    def _load_config(self):
        config_json = self.redis_client.json().get("minipilot:configuration", "$")
        if config_json:
            return config_json[0]
        else:
            raise ValueError("Configuration not found in Redis")

    def _get_env_value(self, key):
        return os.getenv('MINIPILOT_HISTORY_ENABLED',"True").lower() in ('true', '1', 't', 'on')

    def set_key_value(self, key, value):
        self._set_value(key, value)

    def get_config(self):
        return self.config

    def is_distributed(self):
        return self.config.get("minipilot_distributed_configuration_enabled", False)

    def set_distributed(self, value):
        self._set_value('minipilot_distributed_configuration_enabled', value)

    def is_rate_limiter(self):
        return self._get_value('minipilot_rate_limiter_enabled')

    def set_rate_limiter(self, value):
        self._set_value('minipilot_rate_limiter_enabled', value)

    def is_memory(self):
        return self._get_value('minipilot_history_enabled')

    def set_memory(self, value):
        self._set_value('minipilot_history_enabled', value)

    def is_semantic_cache(self):
        return self._get_value('minipilot_cache_enabled')

    def set_semantic_cache(self, value):
        self._set_value('minipilot_cache_enabled', value)

    def _get_value(self, key):
        if self.is_distributed():
            print("reading from Redis")
            return self.config.get(key, False)
        else:
            print("reading from environment")
            return self._get_env_value(key)

    def _set_value(self, key, value):
        self.config[key] = value
        self.redis_client.json().set("minipilot:configuration", f"$.{key}", value)


