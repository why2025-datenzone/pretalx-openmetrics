import json
import logging

from django.core.exceptions import SuspiciousOperation
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, View
from pretalx.common.views.mixins import PermissionRequired
from pretalx.event.models.event import Event
from pretalx.submission.models.submission import SubmissionStates

from .models import OpenmetricsToken

logger = logging.getLogger(__name__)


class MetricsView(View):
    """
    _View that outputs Openmetrics compatible metrics about an event in text form_

    Right now, only the total number of submissions is reported.

    """

    def gen_response(self, event=None):
        """_Generate an HTTP resposne with the metrics for the given event._

        Args:
            event (_Event_, optional): _The event for which the metrics should be generated_. Defaults to none. When no event is specified, then metrics for all events on the server are generated.

        Returns:
            _HttpResponse_: _With Content-Type text/plain_
        """
        if event is None:
            query = Event.objects.all()
        else:
            query = Event.objects.filter(id=event.pk)

        query = query.annotate(
            subcount=Count(
                "submissions",
                filter=~Q(
                    submissions__state__in=[
                        SubmissionStates.DRAFT,
                        SubmissionStates.DELETED,
                    ]
                ),
            )
        ).values("name", "subcount")
        logger.info("Query is {}".format(query.query))
        result = [
            "submissions_total{{event={}}} {}".format(
                json.dumps(str(event["name"])), event["subcount"]
            )
            for event in query
        ]

        return HttpResponse("\n".join(result), content_type="text/plain")


class EventMetricsView(MetricsView):
    """
    _Generate metrics for a single event_
    """

    def get(self, request, event, token):
        token = OpenmetricsToken.objects.filter(
            event=self.request.event, token=token
        ).first()
        if token is None:
            raise SuspiciousOperation()
        return self.gen_response(self.request.event)


class GlobalMetricsView(MetricsView):
    """
    _Generate metrics for all events on the server_
    """

    def get(self, request, token):
        token = OpenmetricsToken.objects.filter(event__isnull=True, token=token).first()
        if token is None:
            raise SuspiciousOperation()
        return self.gen_response(None)


class OpenmetricsUrlView(TemplateView, PermissionRequired):
    """
    _Generic view to generate, reset or create an URL for a single event or all events.
    """

    template_name = "pretalx_openmetrics/settings.html"

    def post(self, request, **kwargs):
        action = self.request.POST.get("action")
        if action == "create":
            # Create a new token
            token = OpenmetricsToken.objects.create(
                token=get_random_string(32), event=self.get_event()
            )
            token.save()
        elif action == "reset":
            # Reset the current token
            token = OpenmetricsToken.objects.filter(event=self.get_event()).first()
            if token is None:
                raise SuspiciousOperation()
            token.token = get_random_string(32)
            token.save()
        elif action == "delete":
            # Delete a token
            token = OpenmetricsToken.objects.filter(event=self.get_event()).first()
            if token is None:
                raise SuspiciousOperation()
            token.delete()
        else:
            # None supported action (could also be None)
            raise SuspiciousOperation()
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_event()
        context["event"] = event
        context["token_url"] = None

        if event is None:
            token = OpenmetricsToken.objects.filter(event__isnull=True).first()
            if token is None:
                return context
            partial_url = reverse(
                "plugins:pretalx_openmetrics:globalmetrics",
                kwargs={"token": token.token},
            )
        else:
            token = OpenmetricsToken.objects.filter(event=event).first()
            if token is None:
                return context
            partial_url = reverse(
                "plugins:pretalx_openmetrics:metrics",
                kwargs={"event": self.request.event.slug, "token": token.token},
            )
        token_url = self.request.build_absolute_uri(partial_url)
        context["token_url"] = token_url
        return context


class OpenmetricsUrlAdminView(OpenmetricsUrlView):
    permission_required = "person.administrator_user"

    def get_event(self):
        return None


class OpenmetricsUrlEventView(OpenmetricsUrlView):
    permission_required = "event.update_event"

    def get_event(self):
        return self.request.event

    def get_object(self):
        return self.request.event
