import csv, os, json
from sqlmodel import select
from .db import get_session, Ad, Creative, Score

def export_csv(path: str = "out/ads.csv"):
    """Write a simple CSV of ads + one creative + score."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with get_session() as s, open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ad_id","page_name","start","stop","platforms","title","body","score","snapshot"])
        ads = s.exec(select(Ad)).all()
        for ad in ads:
            sc = s.get(Score, ad.ad_id)
            cr = s.exec(select(Creative).where(Creative.ad_id == ad.ad_id)).first()
            platforms = ad.publisher_platforms_json or "[]"
            title = (cr.link_title if cr else "") or ""
            body  = (cr.body if cr else "") or ""
            score = f"{sc.score:.2f}" if sc else ""
            w.writerow([
                ad.ad_id,
                ad.page_name or "",
                ad.ad_delivery_start_time or "",
                ad.ad_delivery_stop_time or "",
                platforms,
                title,
                body,
                score,
                ad.ad_snapshot_url or ""
            ])

