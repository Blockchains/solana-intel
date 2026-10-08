from django.db import models
from apps.tokens.models import Token


class Narrative(models.Model):
    narrative_id = models.SlugField(unique=True)
    title = models.CharField(max_length=160)
    state = models.CharField(max_length=24)
    summary = models.TextField(blank=True)
    synthetic = models.BooleanField(default=False)
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.title


class AttentionPost(models.Model):
    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE, related_name="posts")
    platform = models.CharField(max_length=24)
    source_post_id = models.CharField(max_length=80)
    author_id = models.CharField(max_length=80)
    text = models.TextField()
    posted_at = models.DateTimeField()
    ingested_at = models.DateTimeField()
    upstream_id = models.CharField(max_length=80, blank=True)
    near_duplicate_of = models.CharField(max_length=80, blank=True)
    independent = models.BooleanField(default=False)
    community = models.CharField(max_length=40, blank=True)
    contracts = models.JSONField(default=list)
    synthetic = models.BooleanField(default=False)

    class Meta:
        unique_together = [("platform", "source_post_id")]


class TokenCandidate(models.Model):
    narrative = models.ForeignKey(Narrative, on_delete=models.CASCADE, related_name="candidates")
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    score = models.FloatField()
    rank = models.PositiveIntegerField()
    resolution = models.CharField(max_length=32)
    confidence = models.FloatField()
    supporting = models.JSONField(default=list)
    contrary = models.JSONField(default=list)
    as_of = models.DateTimeField()
