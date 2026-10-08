from django.db import models
from apps.tokens.models import Token


class WalletObservation(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="wallet_obs")
    wallet = models.CharField(max_length=64)
    role = models.CharField(max_length=32)
    association = models.CharField(max_length=16, default="unverified")
    balance_pct = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    action = models.CharField(max_length=32, blank=True)
    observed_at = models.DateTimeField()
    note = models.CharField(max_length=200, blank=True)
