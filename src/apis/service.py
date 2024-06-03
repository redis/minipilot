import urllib

from flask import request, Response
from flask_restx import Resource, Namespace, reqparse
from langchain_community.chat_message_histories import RedisChatMessageHistory

from src.apis.validation import rate_limiter
from src.common.config import REDIS_CFG, MINIPILOT_HISTORY_TIMEOUT
from src.common.utils import generate_redis_connection_string, \
    history_to_json
from src.core.RedisRetrievalChain import RedisRetrievalChain

api = Namespace('Services', path="/", description='Chat and search services')


def min_length(min_len):
    def validate(s):
        if len(s) < min_len:
            raise ValueError(f'Minimum length is {min_len}')
        return s
    return validate


def validate_length(min_len, max_len):
    def validate(s):
        if len(s) < min_len:
            raise ValueError(f'Minimum length is {min_len}')
        if len(s) > max_len:
            raise ValueError(f'Maximum length is {max_len}')
        return s
    return validate


@api.route('/history')
class ChatHistory(Resource):
    @api.doc(params={'session-id': {'in': 'header', 'description': 'session-id'}})
    @api.doc(description='Get user conversation history', consumes=['application/json'])
    def get(self):
        """Get user conversation history"""
        session_id = str(request.headers.get("session-id"))
        redis_history = RedisChatMessageHistory(url=generate_redis_connection_string(REDIS_CFG["host"], REDIS_CFG["port"], REDIS_CFG["password"]),
                                                session_id=session_id,
                                                key_prefix='minipilot:history:',
                                                ttl=MINIPILOT_HISTORY_TIMEOUT)
        return history_to_json(redis_history.messages), 200


@api.route('/reset')
class ChatHistoryReset(Resource):
    @api.doc(params={'session-id': {'in': 'header', 'description': 'session-id'}})
    @api.doc(description='Reset user conversation history', consumes=['application/json'])
    def post(self):
        """Reset user conversation history"""
        session_id = str(request.headers.get("session-id"))
        engine = RedisRetrievalChain(session_id)
        engine.reset_history()
        return {"response": "Conversation restarted"}, 200


@api.route('/chat')
class Chat(Resource):
    service_query_parser = reqparse.RequestParser()
    service_query_parser.add_argument('q', type=validate_length(2, 500), required=True, help='Chat query', location='args')

    @api.expect(service_query_parser)
    @api.doc(params={'session-id': {'in': 'header', 'description': 'session-id'}})
    @rate_limiter(request)
    @api.doc(description='Ask a question in natural language: will answer, post the answer to the history and semantic cache', consumes=['application/json'])
    def post(self):
        """Ask a question in natural language: will answer, post the answer to the history and semantic cache"""
        args = self.service_query_parser.parse_args(req=request)
        session_id = str(request.headers.get("session-id"))

        engine = RedisRetrievalChain(session_id)
        engine.ask(args['q'])
        return Response(engine.streamer(), content_type="text/event-stream", headers={'X-Accel-Buffering': 'no'})


@api.route('/references')
class SearchReferences(Resource):
    service_query_parser = reqparse.RequestParser()
    service_query_parser.add_argument('q', type=str, required=True, help='References query', location='args')

    @api.expect(service_query_parser)
    @api.doc(description='Semantic references from a natural language query', consumes=['application/json'])
    def get(self):
        """Semantic references from a natural language query"""
        args = self.service_query_parser.parse_args(req=request)
        # This method is session-less, just performs vector search, we reuse the RedisRetrievalChain utility, though
        # And indicate a fake session id TODO clean up and use a new session-less constructor, or RedisVL
        session_id = "xxxxxxx"
        engine = RedisRetrievalChain(session_id)
        references = engine.references(urllib.parse.unquote(args['q']))
        return references, 200




