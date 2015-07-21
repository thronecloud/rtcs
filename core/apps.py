from django.apps import AppConfig


class CabshareConfig(AppConfig):
    name = 'core'
    verbose_name = "CabShare"

    def ready(self):
        import core.handlers # noqa
