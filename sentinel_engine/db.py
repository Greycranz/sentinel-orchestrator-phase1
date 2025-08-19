from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

ROOT = Path(__file__).resolve().parents[1]
SQLITE_PATH = ROOT / "ops" / "data" / "sentinel.sqlite"

engine = create_engine(f"sqlite:///{SQLITE_PATH}", connect_args={"check_same_thread": False}, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
