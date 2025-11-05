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
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class UserRole(enum.Enum):
    tourist = "tourist"
    operator = "operator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(32), nullable=False, default=UserRole.tourist.value)
    country = Column(String(80), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    province = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(String(50), nullable=True)
    rating_avg = Column(Float, nullable=True)
    images = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


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
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    destination_id = Column(PG_UUID(as_uuid=True), ForeignKey("destinations.id"), nullable=True)
    score = Column(Float, nullable=True)
    model_version = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="recommendations")
    destination = relationship("Destination")
