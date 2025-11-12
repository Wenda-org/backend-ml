import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Date,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False, name="password_hash")
    role = Column(String(10), nullable=False, default=UserRole.user.value)
    created_at = Column(DateTime, default=datetime.utcnow, name="created_at")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(String, primary_key=True)
    name = Column(String(200), nullable=False)
    province = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False, name="category_id")
    rating = Column(Numeric(2, 1), nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, name="created_at")


class TourismStatistics(Base):
    __tablename__ = "tourism_statistics"

    id = Column(Integer, primary_key=True)
    province = Column(String(100), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    domestic_visitors = Column(Integer, nullable=True)
    foreign_visitors = Column(Integer, nullable=True)
    occupancy_rate = Column(Float, nullable=True)
    avg_stay_days = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MLModelsRegistry(Base):
    __tablename__ = "ml_models_registry"

    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    algorithm = Column(String(100), nullable=True)
    metrics = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False, default="active")
    trained_on = Column(Date, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)


class MLPredictions(Base):
    __tablename__ = "ml_predictions"

    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(20), nullable=True)
    province = Column(String(100), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    predicted_visitors = Column(Integer, nullable=True)
    confidence_interval = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationsLog(Base):
    __tablename__ = "recommendations_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, name="user_id")
    destination_id = Column(String, ForeignKey("destinations.id"), nullable=True, name="destination_id")
    score = Column(Float, nullable=True)
    model_version = Column(String(20), nullable=True, name="model_version")
    created_at = Column(DateTime, default=datetime.utcnow, name="created_at")

    user = relationship("User", backref="recommendations")
    destination = relationship("Destination")
