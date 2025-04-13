from django.urls import path, re_path
from pretalx.event.models.event import SLUG_REGEX

from .views import (
    EventMetricsView,
    GlobalMetricsView,
    OpenmetricsUrlAdminView,
    OpenmetricsUrlEventView,
)

urlpatterns = [
    re_path(
        rf"^orga/event/(?P<event>{SLUG_REGEX})/settings/p/pretalx_openmetrics/$",
        OpenmetricsUrlEventView.as_view(),
        name="settings",
    ),
    re_path(
        rf"^(?P<event>{SLUG_REGEX})/p/openmetrics/(?P<token>{SLUG_REGEX})/$",
        EventMetricsView.as_view(),
        name="metrics",
    ),
    re_path(
        rf"^p/openmetrics/metrics/(?P<token>{SLUG_REGEX})/$",
        GlobalMetricsView.as_view(),
        name="globalmetrics",
    ),
    path(
        "orga/admin/openmetrics/",
        OpenmetricsUrlAdminView.as_view(),
        name="globalsettings",
    ),
]
