import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

CFG_SECRET_KEY = os.getenv('CFG_SECRET_KEY', '1234567890abcdefghijklmnopqrstuvwxyz')

MINIPILOT_DEBUG = os.getenv('MINIPILOT_DEBUG',"True").lower() in ('true', '1', 't')
MINIPILOT_LOG = os.getenv('MINIPILOT_LOG', './minipilot.log')

MINIPILOT_HISTORY_TIMEOUT = os.getenv('MINIPILOT_HISTORY_TIMEOUT', 604800)
MINIPILOT_HISTORY_LENGTH = os.getenv('MINIPILOT_HISTORY_LENGTH', 30)
MINIPILOT_RATE_LIMITER_ENABLED = os.getenv('MINIPILOT_RATE_LIMITER_ENABLED',"True").lower() in ('true', '1', 't')

# if minipilot is behind a front-end, use "session" and limit for ip at the front-end
MINIPILOT_RATE_LIMITER_CRITERIA = os.getenv('MINIPILOT_RATE_LIMITER_CRITERIA', "session").lower() # ip | session | all

MINIPILOT_RATE_LIMITER_ALLOW = os.getenv('MINIPILOT_RATE_LIMITER_ALLOW', 10)
MINIPILOT_CONVERSATION_LENGTH = os.getenv('MINIPILOT_CONVERSATION_LENGTH', 10000)
MINIPILOT_LOG_LENGTH = os.getenv('MINIPILOT_LOG_LENGTH', 1000)
MINIPILOT_CONTEXT_LENGTH = os.getenv('MINIPILOT_CONTEXT_LENGTH', 5)
MINIPILOT_RELEVANCE_SCORE = os.getenv('MINIPILOT_RELEVANCE_SCORE', 0.78)
MINIPILOT_MODEL = os.getenv('MINIPILOT_MODEL', "gpt-3.5-turbo-16k")
MINIPILOT_LLM_TIMEOUT = os.getenv('MINIPILOT_LLM_TIMEOUT', 10)
MINIPILOT_SEARCH_RESULTS = os.getenv('MINIPILOT_SEARCH_RESULTS', 10)
MINIPILOT_CACHE_TTL = os.getenv('MINIPILOT_CACHE_TTL', 3600 * 24 * 30)
MINIPILOT_CACHE_THRESHOLD = os.getenv('MINIPILOT_CACHE_THRESHOLD', 0.1)
MINIPILOT_CACHE_ENABLED = os.getenv('MINIPILOT_CACHE_ENABLED',"True").lower() in ('true', '1', 't')



# Redis
REDIS_CFG = {"host": os.getenv('DB_SERVICE', '127.0.0.1'),
             "port": int(os.getenv('DB_PORT',6379)),
             "password": os.getenv('DB_PWD',''),
             "ssl": os.getenv('DB_SSL', False),
             "ssl_keyfile": os.getenv('DB_SSL_KEYFILE', ''),
             "ssl_certfile": os.getenv('DB_SSL_CERTFILE', ''),
             "ssl_cert_reqs": os.getenv('DB_CERT_REQS', 'none'),
             "ssl_ca_certs": os.getenv('DB_CA_CERTS', '')}
