import os
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///scam_radar.db")

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


class Incident(Base):
    __tablename__ = "incidents"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    title        = Column(String(500), nullable=False)
    summary      = Column(Text, default="")
    source       = Column(String(200))
    source_url   = Column(String(1000))
    published_at = Column(DateTime, default=datetime.now)
    province     = Column(String(100))
    category     = Column(String(50))
    severity     = Column(String(20))
    lat          = Column(Float)
    lng          = Column(Float)
    victims      = Column(Integer, default=0)
    amount_thb   = Column(Float, default=0.0)
    
    def to_dict(self):
        return {
            "id":         self.id,
            "title":      self.title,
            "summary":    self.summary,
            "source":     self.source,
            "source_url": self.source_url,
            "date":       self.published_at.strftime("%Y-%m-%d") if self.published_at else None,
            "province":   self.province,
            "category":   self.category,
            "severity":   self.severity,
            "lat":        self.lat,
            "lng":        self.lng,
            "victims":    self.victims,
            "amount_thb": self.amount_thb,
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def get_recent_incidents(limit=200):
    with SessionLocal() as db:
        return db.query(Incident)\
                 .order_by(Incident.published_at.desc())\
                 .limit(limit)\
                 .all()
                 