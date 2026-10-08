from django.db import models
from apps.tokens.models import Token


class Trade(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="trades")
    pool_address = models.CharField(max_length=64)
    signature = models.CharField(max_length=128)
    log_index = models.IntegerField(default=0)
    side = models.CharField(max_length=8)
    price_usd = models.DecimalField(max_digits=28, decimal_places=12)
    size_usd = models.DecimalField(max_digits=28, decimal_places=6)
    wallet = models.CharField(max_length=64)
    event_time = models.DateTimeField()
    available_at = models.DateTimeField()
    synthetic = models.BooleanField(default=False)

    class Meta:
        unique_together = [("signature", "log_index")]


class Candle(models.Model):
    DERIVED = "derived"
    VENDOR = "vendor"
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="candles")
    origin = models.CharField(max_length=16, default=DERIVED)
    bucket_start = models.DateTimeField()
    open = models.DecimalField(max_digits=28, decimal_places=12)
    high = models.DecimalField(max_digits=28, decimal_places=12)
    low = models.DecimalField(max_digits=28, decimal_places=12)
    close = models.DecimalField(max_digits=28, decimal_places=12)
    volume_usd = models.DecimalField(max_digits=28, decimal_places=6)
    buy_count = models.PositiveIntegerField(default=0)
    sell_count = models.PositiveIntegerField(default=0)
    unique_buyers = models.PositiveIntegerField(default=0)
    unique_sellers = models.PositiveIntegerField(default=0)
    provisional = models.BooleanField(default=False)
    empty = models.BooleanField(default=False)

    class Meta:
        unique_together = [("token", "origin", "bucket_start")]
        ordering = ["bucket_start"]


class MarketSnapshot(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="snapshots")
    as_of = models.DateTimeField()
    price_usd = models.DecimalField(max_digits=28, decimal_places=12)
    liquidity_usd = models.DecimalField(max_digits=28, decimal_places=6)
    holder_count = models.IntegerField(null=True, blank=True)
    top10_holder_pct = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    circulating_supply = models.DecimalField(max_digits=36, decimal_places=6, null=True, blank=True)
    total_supply = models.DecimalField(max_digits=36, decimal_places=6, null=True, blank=True)
    valuation_label = models.CharField(max_length=40)
    valuation_usd = models.DecimalField(max_digits=28, decimal_places=2, null=True, blank=True)
    quote_age_seconds = models.FloatField()
    price_impact_pct_1k = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    creator_sold = models.BooleanField(default=False)
    synthetic = models.BooleanField(default=False)
