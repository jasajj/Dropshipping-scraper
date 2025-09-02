from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

class Ad(SQLModel, table=True):
    ad_id: str = Field(primary_key=True)
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    ad_creation_time: Optional[str] = None
    ad_delivery_start_time: Optional[str] = None
    ad_delivery_stop_time: Optional[str] = None
    ad_snapshot_url: Optional[str] = None
    languages_json: Optional[str] = None
    publisher_platforms_json: Optional[str] = None
    ad_type: Optional[str] = None
    countries_json: Optional[str] = None
    raw_json: Optional[str] = None
    first_seen_utc: datetime = Field(default_factory=datetime.utcnow)
    last_seen_utc: datetime = Field(default_factory=datetime.utcnow)
    active_status: Optional[str] = None

class Creative(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ad_id: str = Field(index=True)
    body: Optional[str] = None
    link_title: Optional[str] = None
    link_desc: Optional[str] = None
    link_caption: Optional[str] = None

class Score(SQLModel, table=True):
    ad_id: str = Field(primary_key=True)
    score: float
    components_json: Optional[str] = None
    version: str = "v1"

class Insight(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ad_id: str = Field(index=True)
    model: str
    json: str
    created_utc: datetime = Field(default_factory=datetime.utcnow)

engine = None

def init_engine(db_url: str):
    global engine
    engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)

