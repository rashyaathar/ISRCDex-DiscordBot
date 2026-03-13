from django.apps import AppConfig


class ExtensionsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'extensions_app'
    dpy_package = 'extensions_app.image_generation_ext'
