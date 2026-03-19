from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Create data folder
os.makedirs("data", exist_ok=True)

# Database
engine = create_engine("sqlite:///data/congestion.db", echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()

# -------- TABLES --------

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True)
    source = Column(String)
    destination = Column(String)
    predicted_time = Column(Integer)
    route_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# -------- FUNCTIONS --------

def init_db():
    Base.metadata.create_all(engine)


def save_route(source, destination, route_data, estimated_time):
    with Session() as s:
        r = Route(
            source=source,
            destination=destination,
            route_data=route_data,
            predicted_time=estimated_time
        )
        s.add(r)
        s.commit()
        s.refresh(r)
        return r.id


def save_feedback(route_id, rating, comment):
    with Session() as s:
        fb = Feedback(
            route_id=route_id,
            rating=rating,
            comment=comment
        )
        s.add(fb)
        s.commit()


# 🔥 AI Learning Function
def get_average_rating():
    with Session() as s:
        ratings = s.query(Feedback.rating).all()

        if not ratings:
            return 3  # default neutral

        avg = sum(r[0] for r in ratings) / len(ratings)
        return avg
    # Add this at the bottom of db.py

def get_route_by_id(route_id: int):
    with Session() as s:
        return s.query(Route).filter(Route.id == route_id).first()