import logging

from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _
from pretalx.orga.signals import nav_event_settings, nav_global

logger = logging.getLogger(__name__)


@receiver(nav_global)
def admin_menu(sender, request, **kwargs):
    """
    _Generate the global admin menu entry._
    """
    logger.info("Generating the admin menu")
    if not request.user.is_administrator:
        return []

    url = resolve(request.path_info)

    return [
        {
            "label": _("Openmetrics Global Settings"),
            "url": "/orga/admin/openmetrics/",
            "icon": "line-chart",
            "active": (
                (url.url_name == "openmetrics")
                and (url.namespaces == ["plugins", "pretalx_openmetrics"])
            ),
        }
    ]


@receiver(nav_event_settings)
def pretalx_openmetrics_settings(sender, request, **kwargs):
    """
    _Generate a settings menu entry for a single event._
    """
    if not request.user.has_perm("orga.change_settings", request.event):
        return []

    url = resolve(request.path_info)

    return [
        {
            "label": "Openmetrics",
            "icon": "line-chart",
            "url": reverse(
                "plugins:pretalx_openmetrics:settings",
                kwargs={"event": request.event.slug},
            ),
            "active": (
                (url.url_name in ("settings"))
                and (url.namespaces == ["plugins", "pretalx_openmetrics"])
            ),
        }
    ]
