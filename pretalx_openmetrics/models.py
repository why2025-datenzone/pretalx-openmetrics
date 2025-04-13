from django.db import models


class OpenmetricsToken(models.Model):

    class Meta:
        constraints = [models.UniqueConstraint(fields=["event"], name="unique_event")]

    event = models.OneToOneField(
        to="event.Event",
        on_delete=models.CASCADE,
        related_name="pretalx_openmetrics_token",
        null=True,
    )
    token = models.CharField(max_length=50)
