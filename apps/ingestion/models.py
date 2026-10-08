from django.db import models


class RawEvent(models.Model):
    """Versioned event envelope. Redis is never the only copy."""

    event_id = models.CharField(max_length=64, unique=True)
    event_type = models.CharField(max_length=64)
    schema_version = models.PositiveIntegerField(default=1)
    source = models.CharField(max_length=64)
    source_event_id = models.CharField(max_length=128)
    entity_ids = models.JSONField(default=dict)
    transaction_signature = models.CharField(max_length=128, blank=True)
    instruction_or_log_index = models.IntegerField(null=True, blank=True)
    slot_reference = models.BigIntegerField(null=True, blank=True)
    event_time = models.DateTimeField()
    provider_observed_time = models.DateTimeField(null=True, blank=True)
    ingested_time = models.DateTimeField()
    available_at = models.DateTimeField()
    commitment_status = models.CharField(max_length=32, default="confirmed")
    deduplication_key = models.CharField(max_length=180, unique=True)
    payload = models.JSONField(default=dict)
    raw_payload_reference = models.CharField(max_length=180, blank=True)
    synthetic = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "event_time"]),
            models.Index(fields=["source", "available_at"]),
        ]


class DeadLetter(models.Model):
    source = models.CharField(max_length=64)
    reason = models.CharField(max_length=200)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
