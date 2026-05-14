from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ScanRecord(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    scanned_path = Column(String, nullable=False)
    scan_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    total_dependencies = Column(Integer, default=0)
    total_vulnerabilities = Column(Integer, default=0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    ecosystems = Column(JSON, default=list)
    vulnerabilities_by_severity = Column(JSON, default=dict)
    result_json = Column(Text, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
