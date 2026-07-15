from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import class_mapper
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, Text, ForeignKey, JSON, Numeric, Date, \
    TIMESTAMP, UUID, LargeBinary, text as text_sql, Interval
from sqlalchemy.types import Enum
from sqlalchemy.ext.declarative import declarative_base


@as_declarative()
class Base:
    id: int
    __name__: str

    # Auto-generate table name if not provided
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Generic to_dict() method
    def to_dict(self):
        """
        Converts the SQLAlchemy model instance to a dictionary, ensuring UUID fields are converted to strings.
        """
        result = {}
        for column in class_mapper(self.__class__).columns:
            value = getattr(self, column.key)
                # Handle UUID fields
            if isinstance(value, uuid.UUID):
                value = str(value)
            # Handle datetime fields
            elif isinstance(value, datetime):
                value = value.isoformat()  # Convert to ISO 8601 string
            # Handle Decimal fields
            elif isinstance(value, Decimal):
                value = float(value)

            result[column.key] = value
        return result




class Listings(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seller_id = Column(Integer, nullable=True)
    title = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    category = Column(String, nullable=True)
    item_condition = Column(String, nullable=True)
    images_json = Column(String, nullable=True)
    status = Column(String, nullable=True)
    views_count = Column(Integer, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))
    updated_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, nullable=True)
    sender_id = Column(Integer, nullable=True)
    receiver_id = Column(Integer, nullable=True)
    body = Column(String)
    offer_amount = Column(Float, nullable=True)
    offer_status = Column(String, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Orders(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, nullable=True)
    buyer_id = Column(Integer, nullable=True)
    seller_id = Column(Integer, nullable=True)
    final_price = Column(Float)
    status = Column(String, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))
    updated_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Profiles(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, nullable=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    rating_avg = Column(Float, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))
    updated_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Reviews(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, nullable=True)
    reviewer_id = Column(Integer, nullable=True)
    reviewee_id = Column(Integer, nullable=True)
    rating = Column(Integer)
    comment = Column(String, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    password = Column(String)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, nullable=True)
    listing_id = Column(Integer, nullable=True)
    created_at_dt = Column(DateTime, nullable=True, server_default=text_sql("now()"))


