"""Synthetic vertical slice. Every observation is labelled synthetic.

Clock is controlled. Decisions use only rows with available_at <= as_of.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone as dj_tz

from apps.callers.models import Call, Caller
from apps.decisions.models import Decision
from apps.decisions.policy import evaluate
from apps.hottakes.models import HotTake
from apps.ingestion.models import RawEvent
from apps.markets.candles import build_candles
from apps.markets.models import Candle, MarketSnapshot, Trade
from apps.narratives.attention import attention_quality
from apps.narratives.models import AttentionPost, Narrative, TokenCandidate
from apps.narratives.resolution import resolve_candidates
from apps.positions.accounting import account
from apps.positions.models import Fill, Position
from apps.research.models import ResearchResult
from apps.sources.models import Source, SourceHealth
from apps.tokens.models import Pool, Token
from apps.wallets.models import WalletObservation

T0 = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)
LEADER = "So1CatMoonLeaderMint1111111111111111111111"
CLONE = "So1CatMoonCloneMint22222222222222222222222"
DOG = "So1DogWifUnrelatedMint33333333333333333333"


def _event(eid, etype, source, when, payload, entities):
    RawEvent.objects.update_or_create(
        deduplication_key=f"syn:{eid}",
        defaults=dict(
            event_id=eid,
            event_type=etype,
            schema_version=1,
            source=source,
            source_event_id=eid,
            entity_ids=entities,
            transaction_signature=payload.get("signature", ""),
            instruction_or_log_index=payload.get("log_index"),
            event_time=when,
            provider_observed_time=when,
            ingested_time=when,
            available_at=when,
            commitment_status="confirmed",
            payload=payload,
            raw_payload_reference=f"synthetic://{eid}",
            synthetic=True,
        ),
    )


class Command(BaseCommand):
    help = "Run the labelled synthetic end-to-end scenario."

    def handle(self, *args, **options):
        self._reset()
        self._sources()
        tokens = self._tokens()
        self._trades(tokens)
        self._narrative(tokens)
        actions = self._decide(tokens)
        self.stdout.write(self.style.SUCCESS("synthetic scenario stored"))
        for label, action in actions:
            self.stdout.write(f"{label}: {action}")

    def _reset(self):
        for model in (
            ResearchResult, Fill, Position, HotTake, Decision, Call, Caller,
            TokenCandidate, AttentionPost, Narrative, WalletObservation,
            Candle, MarketSnapshot, Trade, Pool, Token, RawEvent, SourceHealth, Source,
        ):
            model.objects.all().delete()

    def _sources(self):
        rows = [
            ("synthetic-feed", "local", "fixture", "not-applicable", "Labelled synthetic observations only."),
            ("solana-rpc", "solana-rpc", "chain", "blocked", "No RPC credential. Adapter not live-verified."),
            ("pumpportal", "pumpportal.fun", "third-party-ws", "blocked", "Third-party stream. Not an official Pump.fun API."),
            ("dexscreener", "dexscreener", "public-rest", "blocked", "Public REST exists. Not exercised in this run."),
            ("telegram-bot", "telegram-bot-api", "bot", "blocked", "Bot token absent. Bot cannot read chats it is not in."),
            ("x-api", "x", "official-api", "blocked", "Bearer token absent."),
            ("openai", "openai", "llm", "blocked", "Key absent. Fallback extractor only."),
        ]
        for key, provider, kind, live, notes in rows:
            src, _ = Source.objects.update_or_create(
                key=key,
                defaults=dict(provider=provider, kind=kind, access_method=kind, live_verification=live, notes=notes),
            )
            SourceHealth.objects.create(
                source=src,
                status="SYNTHETIC" if key == "synthetic-feed" else "SOURCE UNAVAILABLE",
                lag_seconds=0 if key == "synthetic-feed" else None,
                detail=notes,
                checked_at=T0,
            )

    def _tokens(self):
        specs = [
            (LEADER, "Cat Moon", "CATMOON", T0, "pump.fun-like fixture", "CreatorWalletCatMoon11111111111111111111"),
            (CLONE, "Cat Moon", "CATMOON", T0 + timedelta(minutes=6), "clone fixture", "CreatorWalletClone2222222222222222222222"),
            (DOG, "Dog Wif", "DOGWIF", T0 + timedelta(minutes=2), "unrelated fixture", "CreatorWalletDog333333333333333333333333"),
        ]
        out = {}
        for mint, name, symbol, when, src, creator in specs:
            token = Token.objects.create(
                mint=mint, name=name, symbol=symbol, discovered_at=when,
                launch_source=src, creator=creator, token_program="token-2022-fixture",
                mint_authority_revoked=True, freeze_authority_active=False,
                discovery_provenance="synthetic earliest observation, not first-ever appearance",
                coverage_notes="Synthetic coverage only.", synthetic=True,
            )
            Pool.objects.create(token=token, pool_address=f"pool-{mint}", venue="synthetic-amm", quote_mint="SOL")
            _event(f"disc-{mint[-8:]}", "token.discovered", "synthetic-feed", when, {"mint": mint}, {"mint": mint})
            out[mint] = token
        return out

    def _trades(self, tokens):
        leader = tokens[LEADER]
        price = Decimal("0.000010")
        trades = []
        for i in range(40):
            when = T0 + timedelta(minutes=i % 30, seconds=i)
            side = "buy" if i % 5 else "sell"
            price = price * (Decimal("1.03") if side == "buy" else Decimal("0.99"))
            row = {
                "signature": f"sig-leader-{i}",
                "log_index": 0,
                "side": side,
                "price_usd": price,
                "size_usd": Decimal("400") + i,
                "wallet": f"wallet-{i}",
                "event_time": when,
                "available_at": when,
            }
            trades.append(row)
            Trade.objects.create(token=leader, pool_address=f"pool-{LEADER}", synthetic=True, **row)
        for extra in range(2):
            row = {
                "signature": f"sig-leader-extra-{extra}",
                "log_index": 0,
                "side": "buy",
                "price_usd": price,
                "size_usd": Decimal("500"),
                "wallet": f"wallet-extra-{extra}",
                "event_time": T0 + timedelta(minutes=18, seconds=extra),
                "available_at": T0 + timedelta(minutes=18, seconds=extra),
            }
            trades.append(row)
            Trade.objects.create(token=leader, pool_address=f"pool-{LEADER}", synthetic=True, **row)
        built = build_candles(trades, T0, T0 + timedelta(minutes=31), fill_empty=False)
        for c in built:
            if c["empty"]:
                continue
            Candle.objects.create(
                token=leader, origin=Candle.DERIVED, bucket_start=c["bucket_start"],
                open=c["open"], high=c["high"], low=c["low"], close=c["close"],
                volume_usd=c["volume_usd"], buy_count=c["buy_count"], sell_count=c["sell_count"],
                unique_buyers=c["unique_buyers"], unique_sellers=c["unique_sellers"],
                provisional=c["provisional"], empty=False,
            )
        MarketSnapshot.objects.create(
            token=leader, as_of=T0 + timedelta(minutes=8), price_usd=Decimal("0.000012"),
            liquidity_usd=Decimal("3500"), holder_count=40, top10_holder_pct=Decimal("0.30"),
            circulating_supply=Decimal("1000000000"), total_supply=Decimal("1000000000"),
            valuation_label="circulating market cap", valuation_usd=Decimal("12000"),
            quote_age_seconds=5, price_impact_pct_1k=Decimal("1.2"), synthetic=True,
        )
        MarketSnapshot.objects.create(
            token=leader, as_of=T0 + timedelta(minutes=20), price_usd=Decimal("0.000018"),
            liquidity_usd=Decimal("22000"), holder_count=180, top10_holder_pct=Decimal("0.28"),
            circulating_supply=Decimal("1000000000"), total_supply=Decimal("1000000000"),
            valuation_label="circulating market cap", valuation_usd=Decimal("18000"),
            quote_age_seconds=4, price_impact_pct_1k=Decimal("0.9"), synthetic=True,
        )
        MarketSnapshot.objects.create(
            token=leader, as_of=T0 + timedelta(minutes=28), price_usd=Decimal("0.000027"),
            liquidity_usd=Decimal("9000"), holder_count=160, top10_holder_pct=Decimal("0.33"),
            circulating_supply=Decimal("1000000000"), total_supply=Decimal("1000000000"),
            valuation_label="circulating market cap", valuation_usd=Decimal("27000"),
            quote_age_seconds=6, price_impact_pct_1k=Decimal("2.4"), creator_sold=True, synthetic=True,
        )

    def _narrative(self, tokens):
        narrative = Narrative.objects.create(
            narrative_id="airport-cat",
            title="Airport cat delays a flight",
            state="EMERGING",
            summary="Synthetic cultural fixture. Not a live news claim.",
            synthetic=True,
            updated_at=T0 + timedelta(minutes=5),
        )
        posts = [
            ("x", "p1", "author-news", "Airport cat sat on the jet bridge and delayed departure.", T0 + timedelta(minutes=5), "", "", True, "news"),
            ("x", "p2", "author-copy1", "Airport cat sat on the jet bridge and delayed departure.", T0 + timedelta(minutes=6), "p1", "p1", False, "news"),
            ("tg", "p3", "author-copy2", "Airport cat sat on the jet bridge and delayed departure.", T0 + timedelta(minutes=6), "p1", "p1", False, "telegram"),
            ("x", "p4", "author-meme", "the airport cat is the timeline. contract " + LEADER, T0 + timedelta(minutes=12), "", "", True, "meme"),
            ("x", "p5", "author-sol", "independent note, same story, mint " + LEADER, T0 + timedelta(minutes=14), "", "", True, "solana"),
            ("tg", "p6", "author-clone", "buy the cat clone " + CLONE, T0 + timedelta(minutes=15), "", "", True, "callers"),
        ]
        for platform, pid, author, text, when, upstream, near, indep, community in posts:
            AttentionPost.objects.create(
                narrative=narrative, platform=platform, source_post_id=pid, author_id=author,
                text=text, posted_at=when, ingested_at=when, upstream_id=upstream,
                near_duplicate_of=near, independent=indep, community=community,
                contracts=[], synthetic=True,
            )
        caller, _ = Caller.objects.get_or_create(caller_id="caller-sol", defaults={"platform": "x", "handle": "caller_sol"})
        Call.objects.create(
            caller=caller, token=tokens[LEADER], platform="x", source_post_id="p5",
            usable_time=T0 + timedelta(minutes=14), price_at_call=Decimal("0.000014"),
            prior_move=0.2, repeated=False, synthetic=True,
        )

    def _decide(self, tokens):
        leader = tokens[LEADER]
        narrative = Narrative.objects.get(narrative_id="airport-cat")
        actions = []
        stages = [
            ("t+8 emerging", T0 + timedelta(minutes=8), "EMERGING", False),
            ("t+20 leader", T0 + timedelta(minutes=20), "ACCELERATING", False),
            ("t+22 after fill", T0 + timedelta(minutes=22), "ACCELERATING", True),
            ("t+28 deterioration", T0 + timedelta(minutes=28), "DECAYING", True),
        ]
        position = None
        for label, as_of, state, has_pos in stages:
            narrative.state = state
            narrative.updated_at = as_of
            narrative.save()
            posts = list(AttentionPost.objects.filter(posted_at__lte=as_of).values(
                "author_id", "upstream_id", "near_duplicate_of", "independent", "community"
            ))
            quality = attention_quality(posts)
            snap = MarketSnapshot.objects.filter(token=leader, as_of__lte=as_of).order_by("-as_of").first()
            explicit = LEADER in " ".join(AttentionPost.objects.filter(posted_at__lte=as_of).values_list("text", flat=True))
            ranked = resolve_candidates([
                {"mint": LEADER, "score": 0.81 if explicit else 0.40, "explicit_contract": explicit},
                {"mint": CLONE, "score": 0.42, "explicit_contract": False},
            ])
            TokenCandidate.objects.filter(narrative=narrative, as_of=as_of).delete()
            for i, row in enumerate(ranked["ranked"], start=1):
                TokenCandidate.objects.create(
                    narrative=narrative, token=tokens[row["mint"]], score=row["score"], rank=i,
                    resolution=ranked["state"], confidence=row["score"],
                    supporting=["explicit contract"] if row.get("explicit_contract") else [],
                    contrary=["clone ticker"] if row["mint"] == CLONE else [],
                    as_of=as_of,
                )
            buyers = Trade.objects.filter(token=leader, side="buy", event_time__lte=as_of).values("wallet").distinct().count()
            sells = Trade.objects.filter(token=leader, side="sell", event_time__lte=as_of).count() or 1
            buys = Trade.objects.filter(token=leader, side="buy", event_time__lte=as_of).count()
            obs = {
                "synthetic": True,
                "quote_age_seconds": snap.quote_age_seconds,
                "mint_authority_revoked": leader.mint_authority_revoked,
                "freeze_authority_active": leader.freeze_authority_active,
                "top10_holder_pct": float(snap.top10_holder_pct),
                "liquidity_usd": float(snap.liquidity_usd),
                "price_impact_pct_1k": float(snap.price_impact_pct_1k),
                "resolution": ranked["state"],
                "unique_buyers_5m": buyers,
                "buy_sell_ratio_5m": round(buys / sells, 2),
                "extension_from_first": float(snap.price_usd) / 0.000010,
                "independent_sources": quality["effective_independent_sources"],
                "narrative_state": state,
                "age_minutes": (as_of - T0).total_seconds() / 60,
                "creator_sold": snap.creator_sold,
                "return_1h": 0.4,
                "volume_acceleration": 0.7 if state == "DECAYING" else 1.8,
                "position": has_pos,
                "unrealised_pct": 0.45 if state == "DECAYING" else 0.1,
                "liquidity_drop_from_entry": 0.59 if state == "DECAYING" else 0,
                "adds_used": 0,
                "watch_profile": "EARLY_RUNNER",
            }
            result = evaluate(obs)
            Decision.objects.create(
                token=leader, as_of=as_of, action=result["action"],
                operational_status=result["operational_status"],
                opportunity_type=result["opportunity_type"],
                policy_version=result["policy_version"],
                why_now=result["why_now"],
                main_risks=result["main_risks"],
                what_changed=f"{label}; independent={quality['effective_independent_sources']}; resolution={ranked['state']}",
                invalidation=result["invalidation"],
                positive=result["positive"], negative=result["negative"],
                hard_gates=result["hard_gates"], missing=result["missing"],
                feature_snapshot={**obs, "attention": quality, "resolution": ranked},
                evidence_refs=[f"snapshot:{snap.id}", "narrative:airport-cat"],
                synthetic=True,
            )
            HotTake.objects.update_or_create(
                token=leader,
                defaults=dict(
                    narrative=narrative,
                    entry_reason="Emerging airport-cat fixture with competing mints",
                    priority=80 if has_pos else 60,
                    active=True,
                    last_evaluation=as_of,
                    last_change=result["action"],
                    next_check=as_of + timedelta(minutes=5),
                    expiry=as_of + timedelta(hours=6),
                    triggers=["volume", "leader-change", "liquidity"],
                ),
            )
            if result["action"] == "BUY SMALL NOW" and position is None:
                position = Position.objects.create(
                    token=leader, kind="paper", status="open", opened_at=as_of,
                    notes="Paper fill after decision. Not a recommendation fill.", synthetic=True,
                )
                Fill.objects.create(
                    position=position, side="buy", time=as_of + timedelta(seconds=8),
                    price=snap.price_usd * Decimal("1.005"), quantity=Decimal("1000000"),
                    fee_usd=Decimal("1.20"), slippage_bps=50, quote_age_seconds=4,
                    note="Modelled 8s decision latency and 50 bps slippage. Not a candle extreme.",
                )
            if result["action"] in {"EXIT", "TAKE PROFIT"} and position and position.status == "open":
                Fill.objects.create(
                    position=position, side="sell", time=as_of + timedelta(seconds=10),
                    price=snap.price_usd * Decimal("0.995"), quantity=Decimal("1000000"),
                    fee_usd=Decimal("1.40"), slippage_bps=70, quote_age_seconds=6,
                    note="Paper exit after deterioration.",
                )
                position.status = "closed"
                position.closed_at = as_of
                position.save()
            actions.append((label, result["action"]))
        if position:
            pnl = account(
                [{"side": f.side, "price": f.price, "quantity": f.quantity, "fee_usd": f.fee_usd, "failed": f.failed}
                 for f in position.fills.all()],
                None,
            )
            ResearchResult.objects.create(
                name="synthetic-airport-cat",
                policy="policy-v1.0",
                as_of=T0 + timedelta(minutes=28),
                outcome=actions[-1][1],
                detail={"actions": actions, "pnl": {k: str(v) for k, v in pnl.items()}},
                leakage_controlled=True,
                note="Single synthetic path. Not evidence of predictive edge.",
            )
        return actions
