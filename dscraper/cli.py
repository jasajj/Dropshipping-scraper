import typer
from typing import Optional, List
from .config import DB_URL
from .db import init_engine, init_db
from .meta_client import fetch_ads
from .persist import upsert_ad
from .scorer import compute_scores
from .exporters import export_csv


app = typer.Typer(help="Dropshipping Ad Scraper CLI")

@app.command()
def initdb():
    """Create the local database tables."""
    init_engine(DB_URL)
    init_db()
    typer.echo("✅ Database ready.")

@app.command()
def fetch(
    countries: str = typer.Option(..., help="Comma list of ISO codes e.g. BE,NL,DE,FR,IT,ES,GB"),
    terms: Optional[str] = typer.Option(None, help="Keyword search (e.g. 'dumbbell')"),
    since: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
    until: Optional[str] = typer.Option(None, help="YYYY-MM-DD"),
    status: str = typer.Option("ACTIVE", help="ACTIVE | INACTIVE | ALL"),
):
    """Download ads from Meta Ad Library and save to the DB."""
    init_engine(DB_URL)
    c_list = [c.strip() for c in countries.split(",") if c.strip()]
    total = 0
    for item in fetch_ads(countries=c_list, terms=terms, since=since, until=until, status=status):
        upsert_ad(item)
        total += 1
        if total % 100 == 0:
            typer.echo(f"...{total} ads saved")
    typer.echo(f"✅ Done. Saved {total} ads.")

@app.command()
def score():
    """Compute heuristic scores for ads."""
    init_engine(DB_URL)
    compute_scores()
    typer.echo("✅ Scores computed.")
    
@app.command()
def export(out: str = "out/ads.csv"):
    """Export ads (with one creative + score) to a CSV file."""
    from .config import DB_URL
    from .db import init_engine
    init_engine(DB_URL)
    export_csv(out)
    typer.echo(f"✅ Exported to {out}")

if __name__ == "__main__":
    app()

