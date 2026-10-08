from django.db import models


class ResearchResult(models.Model):
    name = models.CharField(max_length=120)
    policy = models.CharField(max_length=64)
    as_of = models.DateTimeField()
    outcome = models.CharField(max_length=64)
    detail = models.JSONField(default=dict)
    leakage_controlled = models.BooleanField(default=True)
    note = models.TextField(blank=True)
