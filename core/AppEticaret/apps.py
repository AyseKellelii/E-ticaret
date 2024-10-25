from django.apps import AppConfig


class AppeticaretConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AppEticaret'

    def ready(self):
        import AppEticaret.signals