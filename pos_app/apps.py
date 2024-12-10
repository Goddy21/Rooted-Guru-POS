from django.apps import AppConfig

class PosAppConfig(AppConfig):
    name = 'pos_app'  

    def ready(self):
        import pos_app.signals  # This imports your signals, if you have any
