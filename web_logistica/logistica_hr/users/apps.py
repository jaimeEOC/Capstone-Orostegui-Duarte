from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logistica_hr.users'
    verbose_name = 'Usuarios'

    def ready(self):
        import logistica_hr.users.signals  # noqa
