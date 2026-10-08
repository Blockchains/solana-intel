from django.db import models


class Token(models.Model):
    chain = models.CharField(max_length=32, default="solana")
    mint = models.CharField(max_length=64)
    name = models.CharField(max_length=80, blank=True)
    symbol = models.CharField(max_length=20, blank=True)
    decimals = models.PositiveSmallIntegerField(default=6)
    launch_source = models.CharField(max_length=64, blank=True)
    creator = models.CharField(max_length=64, blank=True)
    token_program = models.CharField(max_length=64, blank=True)
    mint_authority_revoked = models.BooleanField(null=True)
    freeze_authority_active = models.BooleanField(null=True)
    discovered_at = models.DateTimeField()
    discovery_provenance = models.CharField(max_length=120)
    coverage_notes = models.TextField(blank=True)
    synthetic = models.BooleanField(default=False)

    class Meta:
        unique_together = [("chain", "mint")]

    def __str__(self):
        return f"{self.symbol or self.mint[:6]}:{self.mint[:8]}"


class Pool(models.Model):
    token = models.ForeignKey(Token, on_delete=models.CASCADE, related_name="pools")
    pool_address = models.CharField(max_length=64)
    venue = models.CharField(max_length=40)
    quote_mint = models.CharField(max_length=64, blank=True)
    migrated_from = models.CharField(max_length=64, blank=True)

    class Meta:
        unique_together = [("pool_address", "venue")]
