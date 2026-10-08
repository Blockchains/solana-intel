"""Attention quality. Copies and shared upstream posts are not independent."""

import re

MINT_RE = re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b")


def extract_contracts(text: str):
    return sorted(set(MINT_RE.findall(text or "")))


def attention_quality(posts):
    raw = len(posts)
    independent = []
    seen_upstream = set()
    seen_near = set()
    communities = set()
    for post in posts:
        communities.add(post.get("community") or "unknown")
        upstream = post.get("upstream_id") or ""
        near = post.get("near_duplicate_of") or ""
        if upstream and upstream in seen_upstream:
            continue
        if near and near in seen_near:
            continue
        if upstream:
            seen_upstream.add(upstream)
        if near:
            seen_near.add(near)
        if post.get("independent", True) and not near:
            independent.append(post)
    authors = {p.get("author_id") for p in independent}
    return {
        "raw_mentions": raw,
        "effective_independent_sources": len(authors),
        "communities": sorted(c for c in communities if c),
        "cross_community_spread": len([c for c in communities if c and c != "unknown"]),
        "source_concentration": round(1 - (len(authors) / raw), 3) if raw else 1.0,
    }
