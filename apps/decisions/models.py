from django.db import models
from apps.tokens.models import Token


class Decision(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="decisions")
    as_of = models.DateTimeField()
    action = models.CharField(max_length=24)
    operational_status = models.CharField(max_length=32)
    opportunity_type = models.CharField(max_length=32, blank=True)
    policy_version = models.CharField(max_length=24)
    why_now = models.TextField()
    main_risks = models.TextField()
    what_changed = models.TextField()
    invalidation = models.TextField()
    positive = models.JSONField(default=list)
    negative = models.JSONField(default=list)
    hard_gates = models.JSONField(default=list)
    missing = models.JSONField(default=list)
    feature_snapshot = models.JSONField(default=dict)
    evidence_refs = models.JSONField(default=list)
    synthetic = models.BooleanField(default=False)

    class Meta:
        ordering = ["-as_of"]
