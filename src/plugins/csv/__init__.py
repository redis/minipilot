from src.plugins.base import BasePlugin

class Csv(BasePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.config = app.config.get('MINIPILOT_CONFIG', {})

    def register_routes(self):
        @self.app.route('/csv')
        def index():
            return "Hello from Minipilot CSV loader!"

    def init_app(self):
        #self.app.static_folder = 'plugins/csv/static'
        #self.app.template_folder = 'plugins/csv/templates'
        self.register_routes()

    def teardown(self):
        pass
        # Clean up resources, remove routes if necessary
        # Flask does not provide an out-of-the-box way to remove routes dynamically
        # https://stackoverflow.com/questions/24129217/flask-delete-routes-added-with-add-url


def create_plugin(app):
    return Csv(app)