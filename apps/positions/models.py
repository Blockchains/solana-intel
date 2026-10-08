from django.db import models
from apps.tokens.models import Token


class Position(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="positions")
    kind = models.CharField(max_length=16, default="paper")
    status = models.CharField(max_length=16, default="open")
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    synthetic = models.BooleanField(default=False)

    @property
    def net_qty(self):
        from decimal import Decimal
        qty = Decimal("0")
        for fill in self.fills.all():
            signed = fill.quantity if fill.side == "buy" else -fill.quantity
            qty += signed
        return qty


class Fill(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="fills")
    side = models.CharField(max_length=8)
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=28, decimal_places=12)
    quantity = models.DecimalField(max_digits=28, decimal_places=6)
    fee_usd = models.DecimalField(max_digits=18, decimal_places=6, default=0)
    slippage_bps = models.IntegerField(default=0)
    quote_age_seconds = models.FloatField(null=True, blank=True)
    tx_ref = models.CharField(max_length=128, blank=True)
    failed = models.BooleanField(default=False)
    note = models.CharField(max_length=200, blank=True)
