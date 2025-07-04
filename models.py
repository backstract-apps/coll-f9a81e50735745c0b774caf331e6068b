from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import class_mapper
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Time, Float, Text, ForeignKey, JSON, Numeric, Date, \
    TIMESTAMP, UUID
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




class PreciousMetals(Base):
    __tablename__ = 'precious_metals'
    metal = Column(String, primary_key=True)
    price_per_gram = Column(String, primary_key=False)


class Smoothies(Base):
    __tablename__ = 'smoothies'
    id = Column(Integer, primary_key=True)
    created_at = Column(Time, primary_key=False)
    title = Column(String, primary_key=False)
    method = Column(String, primary_key=False)
    rating = Column(Integer, primary_key=False)


class Users(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=False)
    password = Column(String, primary_key=False)
    gold_in_gram = Column(String, primary_key=False)
    silver_in_gram = Column(String, primary_key=False)
    supabase_wallet = Column(String, primary_key=False)
    email = Column(String, primary_key=False)
    user_id = Column(Integer, primary_key=True)


class Crypto(Base):
    __tablename__ = 'crypto'
    symbol = Column(String, primary_key=True)
    open = Column(String, primary_key=False)
    close = Column(String, primary_key=False)
    name = Column(String, primary_key=False)
    price_currency = Column(String, primary_key=False)


class Stocks(Base):
    __tablename__ = 'stocks'
    symbol = Column(String, primary_key=True)
    open = Column(String, primary_key=False)
    close = Column(String, primary_key=False)
    name = Column(String, primary_key=False)
    price_currency = Column(String, primary_key=False)
    date = Column(String, primary_key=False)


class Rickandmorty(Base):
    __tablename__ = 'rickandmorty'
    name = Column(String, primary_key=True)
    no_of_episodes = Column(String, primary_key=False)


class Transaction(Base):
    __tablename__ = 'transaction'
    id = Column(Integer, primary_key=True)
    created_at = Column(Time, primary_key=False)
    user_id = Column(String, primary_key=False)
    quantity_grams = Column(String, primary_key=False)
    price_per_gram = Column(String, primary_key=False)
    action = Column(String, primary_key=False)
    amount = Column(String, primary_key=False)
    asset_type = Column(String, primary_key=False)


