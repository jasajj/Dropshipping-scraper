import orjson
from datetime import datetime, timezone
from sqlmodel import select
from .db import Ad, Creative, get_session

def upsert_ad(item: dict):
    """Store one ad + its creative texts into the database (insert or update)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    ad = Ad(
        ad_id=item.get("id"),
        page_id=item.get("page_id"),
        page_name=item.get("page_name"),
        ad_creation_time=item.get("ad_creation_time"),
        ad_delivery_start_time=item.get("ad_delivery_start_time"),
        ad_delivery_stop_time=item.get("ad_delivery_stop_time"),
        ad_snapshot_url=item.get("ad_snapshot_url"),
        languages_json=orjson.dumps(item.get("languages") or []).decode(),
        publisher_platforms_json=orjson.dumps(item.get("publisher_platforms") or []).decode(),
        ad_type="ALL",
        countries_json=orjson.dumps(item.get("ad_reached_countries") or []).decode(),
        raw_json=orjson.dumps(item).decode(),
        active_status=item.get("ad_active_status", "ACTIVE"),
        last_seen_utc=now,
    )

    with get_session() as s:
        existing = s.get(Ad, ad.ad_id)
        if existing:
            # update fields
            for field in Ad.model_fields.keys():
                if field in ["ad_id", "first_seen_utc"]:
                    continue
                setattr(existing, field, getattr(ad, field))
            s.add(existing)
        else:
            ad.first_seen_utc = now
            s.add(ad)

        # clear old creatives for this ad (simple approach for MVP)
        s.exec(f"DELETE FROM creative WHERE ad_id = :ad_id", {"ad_id": ad.ad_id})

        bodies = item.get("ad_creative_bodies") or []
        titles = item.get("ad_creative_link_titles") or []
        descs  = item.get("ad_creative_link_descriptions") or []
        caps   = item.get("ad_creative_link_captions") or []

        max_len = max(len(bodies), len(titles), len(descs), len(caps), 1)
        for i in range(max_len):
            c = Creative(
                ad_id=ad.ad_id,
                body=(bodies[i] if i < len(bodies) else None),
                link_title=(titles[i] if i < len(titles) else None),
                link_desc=(descs[i] if i < len(descs) else None),
                link_caption=(caps[i] if i < len(caps) else None),
            )
            s.add(c)

        s.commit()

