class BasePlugin:
    def __init__(self, app):
        self.app = app

    def register_routes(self):
        pass

    def init_app(self):
        pass