import logging
import os
import time
from http.client import HTTPException

import redis
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_session import Session
from redis.commands.search.field import TextField, TagField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redisvl.extensions.llmcache import SemanticCache
from redisvl.utils.vectorize import OpenAITextVectorizer

from src.apis import api
from src.common.PluginManager import PluginManager
from src.common.config import REDIS_CFG, CFG_SECRET_KEY, MINIPILOT_CACHE_TTL, MINIPILOT_CACHE_THRESHOLD, \
    MINIPILOT_DEBUG, OPENAI_API_KEY
from src.common.logger import setup_logging
from src.common.utils import generate_redis_connection_string, read_index_schema
from src.prompt.PromptManager import PromptManager


def redis_waiter():
    # database may be down or reloading
    while True:
        try:
            conn = redis.StrictRedis(host=REDIS_CFG["host"], port=REDIS_CFG["port"], password=REDIS_CFG["password"])
            conn.ping()
            break
        except Exception as e:
            print(e)
            time.sleep(5)


def create_app():
    # make sure Redis is up and running, and the dataset is loaded in memory
    redis_waiter()

    app = Flask(__name__, template_folder="templates")
    app.secret_key = CFG_SECRET_KEY
    app.config["SESSION_TYPE"] = "redis"
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_NAME'] = 'minipilot'
    app.config['SESSION_REDIS'] = redis.StrictRedis(host=REDIS_CFG["host"], port=REDIS_CFG["port"], password=REDIS_CFG["password"])
    app.config['USE_REDIS_CONNECTION_POOL'] = True
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../assets'))
    app.url_map.strict_slashes = False
    CORS(app)
    Session(app)

    # Check if the folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Folder '{app.config['UPLOAD_FOLDER']}' created.")
    else:
        print(f"Folder '{app.config['UPLOAD_FOLDER']}' already exists.")

    # Redis configuration
    redis_url = generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"])

    # Configuring the RedisVL semantic cache
    oai = OpenAITextVectorizer(
        model="text-embedding-ada-002",
        api_config={"api_key": OPENAI_API_KEY},
    )

    llmcache = SemanticCache(
        name="minipilot_cache_idx",
        prefix="minipilot:cache:item",
        ttl=MINIPILOT_CACHE_TTL,
        redis_url=redis_url,
        distance_threshold=MINIPILOT_CACHE_THRESHOLD,
        vectorizer=oai
    )

    app.llmcache = llmcache

    # Creating the connection pool for the whole server
    try:
        app.pool = redis.ConnectionPool(host=REDIS_CFG["host"],
                                        port=REDIS_CFG["port"],
                                        password=REDIS_CFG["password"],
                                        decode_responses=True)
    except redis.exceptions.ConnectionError:
        print("error connecting to Redis")

    # Load plugins
    plugin_manager = PluginManager(app)
    plugin_manager.load_plugins()

    # Load prompts
    app.prompt_manager = PromptManager(app)

    # Configuring the REST API
    api.init_app(app)

    # Read index schema
    app.index_schema = read_index_schema(app.pool, "minipilot_rag_alias")

    # As the functions says, setup logging
    setup_logging(app)


    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    from .routes import minipilot_bp
    app.register_blueprint(minipilot_bp)

    from .cache.routes import cache_bp
    app.register_blueprint(cache_bp)

    from .prompt.routes import prompt_bp
    app.register_blueprint(prompt_bp)

    from .data.routes import data_bp
    app.register_blueprint(data_bp)

    @app.route('/assets/<filename>')
    def serve_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    conn = redis.StrictRedis(connection_pool=app.pool)
    indexes = conn.execute_command("FT._LIST")
    if "minipilot_data_idx" not in indexes:
        app.logger.info("The index minipilot_data_idx does not exist, creating it")
        index_def = IndexDefinition(prefix=["minipilot:data:"], index_type=IndexType.HASH)
        schema = (TextField("description", as_name="description"),
                  TagField("filename", as_name="filename"),
                  NumericField("uploaded", as_name="uploaded"))
        conn.ft('minipilot_data_idx').create_index(schema, definition=index_def)

    if not MINIPILOT_DEBUG:
        @app.errorhandler(Exception)
        def handle_exception(e):
            # database error
            if isinstance(e, redis.exceptions.ConnectionError):
                return render_template('61.html'), 500

            # pass through HTTP errors
            if isinstance(e, HTTPException):
                return render_template('404.html'), e.code

            # now you're handling non-HTTP exceptions only
            logging.error(e)
            return render_template('500.html'), 500

    return app
