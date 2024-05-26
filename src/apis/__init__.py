from flask_restx import Api

from .service import api as ns_service

authorizations = {
    'api_key': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'admin-token'
    }
}

api = Api(
    title='Minipilot Server REST API',
    version='1.0',
    description='Welcome to the Minipilot Server REST API. Use this API to train your GenAI chatbot with online docs',
    doc='/api',
    prefix='/api',
    authorizations=authorizations,
    security='api_key'
)

api.add_namespace(ns_service)
