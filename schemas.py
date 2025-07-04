from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple

import re

class PreciousMetals(BaseModel):
    metal: str
    price_per_gram: float


class ReadPreciousMetals(BaseModel):
    metal: str
    price_per_gram: float
    class Config:
        from_attributes = True


class Smoothies(BaseModel):
    id: int
    created_at: datetime.time
    title: str
    method: str
    rating: int


class ReadSmoothies(BaseModel):
    id: int
    created_at: datetime.time
    title: str
    method: str
    rating: int
    class Config:
        from_attributes = True


class Users(BaseModel):
    username: str
    password: str
    gold_in_gram: float
    silver_in_gram: float
    supabase_wallet: float
    email: str
    user_id: int


class ReadUsers(BaseModel):
    username: str
    password: str
    gold_in_gram: float
    silver_in_gram: float
    supabase_wallet: float
    email: str
    user_id: int
    class Config:
        from_attributes = True


class Crypto(BaseModel):
    symbol: str
    open: float
    close: float
    name: str
    price_currency: str


class ReadCrypto(BaseModel):
    symbol: str
    open: float
    close: float
    name: str
    price_currency: str
    class Config:
        from_attributes = True


class Stocks(BaseModel):
    symbol: str
    open: float
    close: float
    name: str
    price_currency: str
    date: str


class ReadStocks(BaseModel):
    symbol: str
    open: float
    close: float
    name: str
    price_currency: str
    date: str
    class Config:
        from_attributes = True


class Rickandmorty(BaseModel):
    name: str
    no_of_episodes: float


class ReadRickandmorty(BaseModel):
    name: str
    no_of_episodes: float
    class Config:
        from_attributes = True


class Transaction(BaseModel):
    id: int
    created_at: datetime.time
    user_id: float
    quantity_grams: float
    price_per_gram: float
    action: str
    amount: float
    asset_type: str


class ReadTransaction(BaseModel):
    id: int
    created_at: datetime.time
    user_id: float
    quantity_grams: float
    price_per_gram: float
    action: str
    amount: float
    asset_type: str
    class Config:
        from_attributes = True




class PostPreciousMetals(BaseModel):
    metal: str = Field(..., max_length=100)
    price_per_gram: Any = Field(...)

    class Config:
        from_attributes = True



class PostSmoothies(BaseModel):
    id: int = Field(...)
    created_at: Any = Field(...)
    title: str = Field(..., max_length=100)
    method: str = Field(..., max_length=100)
    rating: int = Field(...)

    class Config:
        from_attributes = True



class PostUsers(BaseModel):
    username: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)
    gold_in_gram: Any = Field(...)
    silver_in_gram: Any = Field(...)

    class Config:
        from_attributes = True



class PostCrypto(BaseModel):
    symbol: str = Field(..., max_length=100)
    open: Any = Field(...)
    close: Any = Field(...)
    name: str = Field(..., max_length=100)
    price_currency: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostStocks(BaseModel):
    symbol: str = Field(..., max_length=100)
    open: Any = Field(...)
    close: Any = Field(...)
    name: str = Field(..., max_length=100)
    price_currency: str = Field(..., max_length=100)
    date: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostRickandmorty(BaseModel):
    name: str = Field(..., max_length=100)
    no_of_episodes: Any = Field(...)

    class Config:
        from_attributes = True

