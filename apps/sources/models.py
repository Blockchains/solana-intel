from django.db import models


class Source(models.Model):
    key = models.SlugField(unique=True)
    provider = models.CharField(max_length=80)
    kind = models.CharField(max_length=40)
    access_method = models.CharField(max_length=80)
    live_verification = models.CharField(max_length=40, default="blocked")
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.key


class SourceHealth(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="health")
    status = models.CharField(max_length=32)
    lag_seconds = models.FloatField(null=True, blank=True)
    detail = models.TextField(blank=True)
    checked_at = models.DateTimeField()

    class Meta:
        ordering = ["-checked_at"]
