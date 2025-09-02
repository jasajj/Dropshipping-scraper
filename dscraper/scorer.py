import json
from datetime import datetime, timezone
from sqlmodel import select
from .db import Ad, Creative, Score, get_session

def _days_between(start_iso: str, stop_iso: str) -> float:
    """Return number of days an ad has been running (or ran)."""
    fmt = "%Y-%m-%dT%H:%M:%S%z"
    def parse(x):
        if not x:
            return None
        try:
            return datetime.strptime(x, fmt)
        except Exception:
            return None

    start = parse(start_iso)
    stop  = parse(stop_iso) or datetime.now(timezone.utc)
    if not start:
        return 0.0
    return max((stop - start).days, 0)

def compute_scores():
    """
    Score each ad using simple, transparent rules:
    - longer-running ads score higher
    - more creative variants score higher
    - more platforms (FB + IG) score higher
    """
    with get_session() as s:
        ads = s.exec(select(Ad)).all()
        for ad in ads:
            duration_days = _days_between(ad.ad_delivery_start_time, ad.ad_delivery_stop_time)
            duration_norm = min(duration_days / 90.0, 1.0)  # 0..1 (cap at 90 days)

            platforms = json.loads(ad.publisher_platforms_json or "[]")
            platform_norm = min(len(set(platforms)) / 3.0, 1.0)  # 0..1

            creatives_count = s.exec(select(Creative).where(Creative.ad_id == ad.ad_id)).count()
            creative_norm = min(creatives_count / 5.0, 1.0)  # 0..1

            score = (
                0.35 * duration_norm +
                0.20 * creative_norm +
                0.15 * platform_norm
            )

            existing = s.get(Score, ad.ad_id)
            if existing:
                existing.score = float(score)
                s.add(existing)
            else:
                s.add(Score(ad_id=ad.ad_id, score=float(score)))
        s.commit()

