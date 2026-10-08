from django.db import models
from apps.tokens.models import Token


class Caller(models.Model):
    caller_id = models.SlugField(unique=True)
    platform = models.CharField(max_length=24)
    handle = models.CharField(max_length=80)
    sample_size = models.PositiveIntegerField(default=0)
    median_mfe = models.FloatField(null=True, blank=True)
    median_mae = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.handle


class Call(models.Model):
    caller = models.ForeignKey(Caller, on_delete=models.CASCADE, related_name="calls")
    token = models.ForeignKey(Token, on_delete=models.CASCADE)
    platform = models.CharField(max_length=24)
    source_post_id = models.CharField(max_length=80)
    usable_time = models.DateTimeField()
    price_at_call = models.DecimalField(max_digits=28, decimal_places=12)
    prior_move = models.FloatField(default=0)
    repeated = models.BooleanField(default=False)
    mfe = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)
    synthetic = models.BooleanField(default=False)

    class Meta:
        unique_together = [("caller", "token", "source_post_id")]
