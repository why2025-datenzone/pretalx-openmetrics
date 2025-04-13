from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from . import __version__


class PluginApp(AppConfig):
    name = "pretalx_openmetrics"
    verbose_name = "Pretalx Openmetrics"

    class PretalxPluginMeta:
        name = gettext_lazy("Pretalx Openmetrics")
        author = "Erik Tews"
        description = gettext_lazy("Exporter for metrics in the Openmetrics format")
        visible = True
        version = __version__
        category = "INTEGRATION"

    def ready(self):
        from . import signals  # NOQA
