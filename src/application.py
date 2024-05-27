import logging
from http.client import HTTPException

import redis
from flask import Flask, render_template
from flask_cors import CORS
from flask_session import Session
import wtforms_json
from redisvl.llmcache import SemanticCache

from src.apis import api
from src.common.config import REDIS_CFG, CFG_SECRET_KEY, MINIPILOT_CACHE_TTL, MINIPILOT_CACHE_THRESHOLD,  MINIPILOT_DEBUG
from src.common.logger import setup_logging
from src.common.utils import generate_redis_connection_string


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = CFG_SECRET_KEY
    app.config["SESSION_TYPE"] = "redis"
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_NAME'] = 'minipilot'
    app.config['SESSION_REDIS'] = redis.StrictRedis(host=REDIS_CFG["host"], port=REDIS_CFG["port"], password=REDIS_CFG["password"])
    app.config['USE_REDIS_CONNECTION_POOL'] = True
    app.url_map.strict_slashes = False
    CORS(app)
    Session(app)
    wtforms_json.init()

    # Configuring the RedisVL semantic cache
    llmcache = SemanticCache(
        name="minipilot_cache_idx",
        prefix="minipilot:cache:item",
        ttl=MINIPILOT_CACHE_TTL,
        redis_url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]),
        distance_threshold=MINIPILOT_CACHE_THRESHOLD
    )

    app.llmcache = llmcache

    # Configuring the REST API
    api.init_app(app)

    @app.after_request
    def add_header(r):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
        return r

    try:
        app.pool = redis.ConnectionPool(host=REDIS_CFG["host"],
                                        port=REDIS_CFG["port"],
                                        password=REDIS_CFG["password"],
                                        decode_responses=True)

    except redis.exceptions.ConnectionError:
        print("error connecting to Redis")

    from .routes import minipilot_bp
    app.register_blueprint(minipilot_bp)

    from .cache.routes import cache_bp
    app.register_blueprint(cache_bp)

    from .status.routes import status_bp
    app.register_blueprint(status_bp)

    # As the functions says, setup logging
    setup_logging(app)

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
