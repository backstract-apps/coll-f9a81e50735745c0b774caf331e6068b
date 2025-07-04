from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_, or_
from typing import *
from fastapi import Request, UploadFile, HTTPException
import models, schemas
import boto3
import jwt
import datetime
import requests
from pathlib import Path


async def get_precious_metals(db: Session):

    query = db.query(models.PreciousMetals)

    precious_metals_all = query.all()
    precious_metals_all = (
        [new_data.to_dict() for new_data in precious_metals_all]
        if precious_metals_all
        else precious_metals_all
    )

    import requests
    from typing import List
    from typing import Dict

    try:
        supabase_url = "https://dvnxmmwjpuuujdsjpmft.supabase.co"
        supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2bnhtbXdqcHV1dWpkc2pwbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMzIzNzksImV4cCI6MjA2NDcwODM3OX0.OVO-XPigErZOFyVOEVdPa6pHXtHEYGIIG637IhGFhSE"

        rates_api_url = "https://data-asg.goldprice.org/dbXRates/INR"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": "https://www.goldprice.org/",
            "X-Requested-With": "XMLHttpRequest",
        }

        try:
            response = requests.get(rates_api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print("API Request Failed:", e)
            exit()

        # Extract gold and silver prices per gram
        char_list: List[Dict[str, Any]] = []

        for item in data.get("items", []):
            gold_oz = item.get("xauPrice")
            silver_oz = item.get("xagPrice")

            if gold_oz and silver_oz:
                gold_per_gram = gold_oz / 31.1035
                silver_per_gram = silver_oz / 31.1035

                char_list.append({"metal": "gold", "price_per_gram": gold_per_gram})
                char_list.append({"metal": "silver", "price_per_gram": silver_per_gram})
                break  # Only process first item

        # Push to Supabase
        for row in char_list:
            res = requests.post(
                f"{supabase_url}/rest/v1/precious_metals",
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json=row,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "precious_metals_all": char_list,
    }
    return res


async def get_buygold(db: Session, quantity: int, email: str):

    query = db.query(models.PreciousMetals)

    all_metals = query.all()
    all_metals = (
        [new_data.to_dict() for new_data in all_metals] if all_metals else all_metals
    )

    query = db.query(models.Users)

    user_data = query.first()

    user_data = (
        (user_data.to_dict() if hasattr(user_data, "to_dict") else vars(user_data))
        if user_data
        else user_data
    )

    import requests

    try:
        supabase_url = "https://dvnxmmwjpuuujdsjpmft.supabase.co"
        supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2bnhtbXdqcHV1dWpkc2pwbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMzIzNzksImV4cCI6MjA2NDcwODM3OX0.OVO-XPigErZOFyVOEVdPa6pHXtHEYGIIG637IhGFhSE"

        balance = user_data["supabase_wallet"]
        price_of_gold = all_metals[0]["price_per_gram"]
        amount = quantity * price_of_gold
        difference = balance - amount

        if difference < 0:
            print("Can't be processed")
        else:
            new_quant = user_data["gold_in_gram"] + quantity
            user_email = user_data["email"]
            res = requests.patch(
                f"{supabase_url}/rest/v1/users?email=eq.{user_email}",
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json={"supabase_wallet": difference, "gold_in_gram": new_quant},
            )
            d = res.status_code

            gres = requests.post(
                f"{supabase_url}/rest/v1/transaction",
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json={
                    "user_id": user_data["user_id"],
                    "action": "buy",
                    "quantity_grams": quantity,
                    "price_per_gram": price_of_gold,
                    "amount": amount,
                    "asset_type": "gold",
                },
            )
            l = gres.status_code

            if res.status_code == 200:
                print("Wallet updated:", res.json())
            else:
                print("Error updating wallet:", res.text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "output1": d,
        "output2": l,
    }
    return res


async def get_precious_metals_metal(db: Session, metal: int):

    query = db.query(models.PreciousMetals)

    precious_metals_one = query.first()

    precious_metals_one = (
        (
            precious_metals_one.to_dict()
            if hasattr(precious_metals_one, "to_dict")
            else vars(precious_metals_one)
        )
        if precious_metals_one
        else precious_metals_one
    )

    res = {
        "precious_metals_one": precious_metals_one,
    }
    return res


async def post_precious_metals(db: Session, raw_data: schemas.PostPreciousMetals):
    metal: str = raw_data.metal
    price_per_gram: float = raw_data.price_per_gram

    record_to_be_added = {"metal": metal, "price_per_gram": price_per_gram}
    new_precious_metals = models.PreciousMetals(**record_to_be_added)
    db.add(new_precious_metals)
    db.commit()
    db.refresh(new_precious_metals)
    precious_metals_inserted_record = new_precious_metals.to_dict()

    res = {
        "precious_metals_inserted_record": precious_metals_inserted_record,
    }
    return res


async def put_precious_metals_metal(db: Session, metal: str, price_per_gram: float):

    query = db.query(models.PreciousMetals)
    precious_metals_edited_record = query.first()

    if precious_metals_edited_record:
        for key, value in {"metal": metal, "price_per_gram": price_per_gram}.items():
            setattr(precious_metals_edited_record, key, value)

        db.commit()
        db.refresh(precious_metals_edited_record)

        precious_metals_edited_record = (
            precious_metals_edited_record.to_dict()
            if hasattr(precious_metals_edited_record, "to_dict")
            else vars(precious_metals_edited_record)
        )
    res = {
        "precious_metals_edited_record": precious_metals_edited_record,
    }
    return res


async def delete_precious_metals_metal(db: Session, metal: int):

    query = db.query(models.PreciousMetals)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        precious_metals_deleted = record_to_delete.to_dict()
    else:
        precious_metals_deleted = record_to_delete
    res = {
        "precious_metals_deleted": precious_metals_deleted,
    }
    return res


async def get_smoothies(db: Session):

    query = db.query(models.Smoothies)

    smoothies_all = query.all()
    smoothies_all = (
        [new_data.to_dict() for new_data in smoothies_all]
        if smoothies_all
        else smoothies_all
    )
    res = {
        "smoothies_all": smoothies_all,
    }
    return res


async def get_smoothies_id(db: Session, id: int):

    query = db.query(models.Smoothies)

    smoothies_one = query.first()

    smoothies_one = (
        (
            smoothies_one.to_dict()
            if hasattr(smoothies_one, "to_dict")
            else vars(smoothies_one)
        )
        if smoothies_one
        else smoothies_one
    )

    res = {
        "smoothies_one": smoothies_one,
    }
    return res


async def post_smoothies(db: Session, raw_data: schemas.PostSmoothies):
    id: int = raw_data.id
    created_at: datetime.datetime = raw_data.created_at
    title: str = raw_data.title
    method: str = raw_data.method
    rating: int = raw_data.rating

    record_to_be_added = {
        "id": id,
        "title": title,
        "method": method,
        "rating": rating,
        "created_at": created_at,
    }
    new_smoothies = models.Smoothies(**record_to_be_added)
    db.add(new_smoothies)
    db.commit()
    db.refresh(new_smoothies)
    smoothies_inserted_record = new_smoothies.to_dict()

    res = {
        "smoothies_inserted_record": smoothies_inserted_record,
    }
    return res


async def put_smoothies_id(
    db: Session, id: int, created_at: str, title: str, method: str, rating: int
):

    query = db.query(models.Smoothies)
    smoothies_edited_record = query.first()

    if smoothies_edited_record:
        for key, value in {
            "id": id,
            "title": title,
            "method": method,
            "rating": rating,
            "created_at": created_at,
        }.items():
            setattr(smoothies_edited_record, key, value)

        db.commit()
        db.refresh(smoothies_edited_record)

        smoothies_edited_record = (
            smoothies_edited_record.to_dict()
            if hasattr(smoothies_edited_record, "to_dict")
            else vars(smoothies_edited_record)
        )
    res = {
        "smoothies_edited_record": smoothies_edited_record,
    }
    return res


async def delete_smoothies_id(db: Session, id: int):

    query = db.query(models.Smoothies)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        smoothies_deleted = record_to_delete.to_dict()
    else:
        smoothies_deleted = record_to_delete
    res = {
        "smoothies_deleted": smoothies_deleted,
    }
    return res


async def get_users_email(db: Session, email: int):

    query = db.query(models.Users)

    users_one = query.first()

    users_one = (
        (users_one.to_dict() if hasattr(users_one, "to_dict") else vars(users_one))
        if users_one
        else users_one
    )

    res = {
        "users_one": users_one,
    }
    return res


async def post_users(db: Session, raw_data: schemas.PostUsers):
    username: str = raw_data.username
    email: str = raw_data.email
    password: str = raw_data.password
    gold_in_gram: float = raw_data.gold_in_gram
    silver_in_gram: float = raw_data.silver_in_gram

    record_to_be_added = {
        "email": email,
        "password": password,
        "username": username,
        "gold_in_gram": gold_in_gram,
        "silver_in_gram": silver_in_gram,
    }
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    users_inserted_record = new_users.to_dict()

    res = {
        "users_inserted_record": users_inserted_record,
    }
    return res


async def put_users_email(
    db: Session,
    username: str,
    email: str,
    password: str,
    gold_in_gram: float,
    silver_in_gram: float,
):

    query = db.query(models.Users)
    users_edited_record = query.first()

    if users_edited_record:
        for key, value in {
            "email": email,
            "password": password,
            "username": username,
            "gold_in_gram": gold_in_gram,
            "silver_in_gram": silver_in_gram,
        }.items():
            setattr(users_edited_record, key, value)

        db.commit()
        db.refresh(users_edited_record)

        users_edited_record = (
            users_edited_record.to_dict()
            if hasattr(users_edited_record, "to_dict")
            else vars(users_edited_record)
        )
    res = {
        "users_edited_record": users_edited_record,
    }
    return res


async def delete_users_email(db: Session, email: int):

    query = db.query(models.Users)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        users_deleted = record_to_delete.to_dict()
    else:
        users_deleted = record_to_delete
    res = {
        "users_deleted": users_deleted,
    }
    return res


async def get_crypto(db: Session):

    query = db.query(models.Crypto)

    crypto_all = query.all()
    crypto_all = (
        [new_data.to_dict() for new_data in crypto_all] if crypto_all else crypto_all
    )
    res = {
        "crypto_all": crypto_all,
    }
    return res


async def get_crypto_symbol(db: Session, symbol: int):

    query = db.query(models.Crypto)

    crypto_one = query.first()

    crypto_one = (
        (crypto_one.to_dict() if hasattr(crypto_one, "to_dict") else vars(crypto_one))
        if crypto_one
        else crypto_one
    )

    res = {
        "crypto_one": crypto_one,
    }
    return res


async def post_crypto(db: Session, raw_data: schemas.PostCrypto):
    symbol: str = raw_data.symbol
    open: float = raw_data.open
    close: float = raw_data.close
    name: str = raw_data.name
    price_currency: str = raw_data.price_currency

    record_to_be_added = {
        "name": name,
        "open": open,
        "close": close,
        "symbol": symbol,
        "price_currency": price_currency,
    }
    new_crypto = models.Crypto(**record_to_be_added)
    db.add(new_crypto)
    db.commit()
    db.refresh(new_crypto)
    crypto_inserted_record = new_crypto.to_dict()

    res = {
        "crypto_inserted_record": crypto_inserted_record,
    }
    return res


async def put_crypto_symbol(
    db: Session, symbol: str, open: float, close: float, name: str, price_currency: str
):

    query = db.query(models.Crypto)
    crypto_edited_record = query.first()

    if crypto_edited_record:
        for key, value in {
            "name": name,
            "open": open,
            "close": close,
            "symbol": symbol,
            "price_currency": price_currency,
        }.items():
            setattr(crypto_edited_record, key, value)

        db.commit()
        db.refresh(crypto_edited_record)

        crypto_edited_record = (
            crypto_edited_record.to_dict()
            if hasattr(crypto_edited_record, "to_dict")
            else vars(crypto_edited_record)
        )
    res = {
        "crypto_edited_record": crypto_edited_record,
    }
    return res


async def delete_crypto_symbol(db: Session, symbol: int):

    query = db.query(models.Crypto)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        crypto_deleted = record_to_delete.to_dict()
    else:
        crypto_deleted = record_to_delete
    res = {
        "crypto_deleted": crypto_deleted,
    }
    return res


async def get_stocks_symbol(db: Session, symbol: int):

    query = db.query(models.Stocks)

    stocks_one = query.first()

    stocks_one = (
        (stocks_one.to_dict() if hasattr(stocks_one, "to_dict") else vars(stocks_one))
        if stocks_one
        else stocks_one
    )

    res = {
        "stocks_one": stocks_one,
    }
    return res


async def post_stocks(db: Session, raw_data: schemas.PostStocks):
    symbol: str = raw_data.symbol
    open: float = raw_data.open
    close: float = raw_data.close
    name: str = raw_data.name
    price_currency: str = raw_data.price_currency
    date: str = raw_data.date

    record_to_be_added = {
        "date": date,
        "name": name,
        "open": open,
        "close": close,
        "symbol": symbol,
        "price_currency": price_currency,
    }
    new_stocks = models.Stocks(**record_to_be_added)
    db.add(new_stocks)
    db.commit()
    db.refresh(new_stocks)
    stocks_inserted_record = new_stocks.to_dict()

    res = {
        "stocks_inserted_record": stocks_inserted_record,
    }
    return res


async def put_stocks_symbol(
    db: Session,
    symbol: str,
    open: float,
    close: float,
    name: str,
    price_currency: str,
    date: str,
):

    query = db.query(models.Stocks)
    stocks_edited_record = query.first()

    if stocks_edited_record:
        for key, value in {
            "date": date,
            "name": name,
            "open": open,
            "close": close,
            "symbol": symbol,
            "price_currency": price_currency,
        }.items():
            setattr(stocks_edited_record, key, value)

        db.commit()
        db.refresh(stocks_edited_record)

        stocks_edited_record = (
            stocks_edited_record.to_dict()
            if hasattr(stocks_edited_record, "to_dict")
            else vars(stocks_edited_record)
        )
    res = {
        "stocks_edited_record": stocks_edited_record,
    }
    return res


async def delete_stocks_symbol(db: Session, symbol: int):

    query = db.query(models.Stocks)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        stocks_deleted = record_to_delete.to_dict()
    else:
        stocks_deleted = record_to_delete
    res = {
        "stocks_deleted": stocks_deleted,
    }
    return res


async def get_rickandmorty(db: Session):

    query = db.query(models.Rickandmorty)

    rickandmorty_all = query.all()
    rickandmorty_all = (
        [new_data.to_dict() for new_data in rickandmorty_all]
        if rickandmorty_all
        else rickandmorty_all
    )

    import requests
    from typing import List
    from typing import Any

    try:
        supabase_url = "https://dvnxmmwjpuuujdsjpmft.supabase.co"
        supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2bnhtbXdqcHV1dWpkc2pwbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMzIzNzksImV4cCI6MjA2NDcwODM3OX0.OVO-XPigErZOFyVOEVdPa6pHXtHEYGIIG637IhGFhSE"  # Replace with secure loading in production

        baseurl = "http://rickandmortyapi.com/api/"
        endpoint = "character"
        r = requests.get(baseurl + endpoint)
        data = r.json()
        char_list: List[Any] = []
        for item in data["results"]:
            char = {"name": item["name"], "no_of_episodes": len(item["episode"])}
            char_list.append(char)

        for row in char_list:
            res = requests.post(
                f"{supabase_url}/rest/v1/rickandmorty",  # Ensure this matches your Supabase table name
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json=row,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "rickandmorty_all": char_list,
    }
    return res


async def get_rickandmorty_name(db: Session, name: int):

    query = db.query(models.Rickandmorty)

    rickandmorty_one = query.first()

    rickandmorty_one = (
        (
            rickandmorty_one.to_dict()
            if hasattr(rickandmorty_one, "to_dict")
            else vars(rickandmorty_one)
        )
        if rickandmorty_one
        else rickandmorty_one
    )

    res = {
        "rickandmorty_one": rickandmorty_one,
    }
    return res


async def post_rickandmorty(db: Session, raw_data: schemas.PostRickandmorty):
    name: str = raw_data.name
    no_of_episodes: float = raw_data.no_of_episodes

    record_to_be_added = {"name": name, "no_of_episodes": no_of_episodes}
    new_rickandmorty = models.Rickandmorty(**record_to_be_added)
    db.add(new_rickandmorty)
    db.commit()
    db.refresh(new_rickandmorty)
    rickandmorty_inserted_record = new_rickandmorty.to_dict()

    res = {
        "rickandmorty_inserted_record": rickandmorty_inserted_record,
    }
    return res


async def get_sellgold(db: Session, quantity: int, email: str):

    query = db.query(models.PreciousMetals)

    all_metals = query.all()
    all_metals = (
        [new_data.to_dict() for new_data in all_metals] if all_metals else all_metals
    )

    query = db.query(models.Users)

    user_data = query.first()

    user_data = (
        (user_data.to_dict() if hasattr(user_data, "to_dict") else vars(user_data))
        if user_data
        else user_data
    )

    import requests

    try:
        supabase_url = "https://dvnxmmwjpuuujdsjpmft.supabase.co"
        supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2bnhtbXdqcHV1dWpkc2pwbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMzIzNzksImV4cCI6MjA2NDcwODM3OX0.OVO-XPigErZOFyVOEVdPa6pHXtHEYGIIG637IhGFhSE"

        new_quant = 0
        new_balance = 0
        inventory_gold = user_data["gold_in_gram"]
        if inventory_gold >= quantity:
            gold_price = all_metals[0]["price_per_gram"]
            amount = quantity * gold_price
            new_balance = user_data["supabase_wallet"] + amount
            new_quant = inventory_gold - quantity
            user_email = user_data["email"]
            res = requests.patch(
                f"{supabase_url}/rest/v1/users?email=eq.{user_email}",
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json={"supabase_wallet": new_balance, "gold_in_gram": new_quant},
            )
            d = res.status_code

            gres = requests.post(
                f"{supabase_url}/rest/v1/transaction",
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json={
                    "user_id": user_data["user_id"],
                    "action": "sell",
                    "quantity_grams": quantity,
                    "price_per_gram": gold_price,
                    "amount": amount,
                    "asset_type": "gold",
                },
            )
            l = gres.status_code

            if res.status_code == 200:
                print("Wallet updated:", res.json())
            else:
                print("Error updating wallet:", res.text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "output1": d,
        "output2": l,
    }
    return res


async def put_rickandmorty_name(db: Session, name: str, no_of_episodes: float):

    query = db.query(models.Rickandmorty)
    rickandmorty_edited_record = query.first()

    if rickandmorty_edited_record:
        for key, value in {"name": name, "no_of_episodes": no_of_episodes}.items():
            setattr(rickandmorty_edited_record, key, value)

        db.commit()
        db.refresh(rickandmorty_edited_record)

        rickandmorty_edited_record = (
            rickandmorty_edited_record.to_dict()
            if hasattr(rickandmorty_edited_record, "to_dict")
            else vars(rickandmorty_edited_record)
        )
    res = {
        "rickandmorty_edited_record": rickandmorty_edited_record,
    }
    return res


async def delete_rickandmorty_name(db: Session, name: int):

    query = db.query(models.Rickandmorty)

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        rickandmorty_deleted = record_to_delete.to_dict()
    else:
        rickandmorty_deleted = record_to_delete
    res = {
        "rickandmorty_deleted": rickandmorty_deleted,
    }
    return res


async def get_stocks(db: Session):

    query = db.query(models.Stocks)

    stocks_all = query.all()
    stocks_all = (
        [new_data.to_dict() for new_data in stocks_all] if stocks_all else stocks_all
    )

    import requests
    from typing import List
    from typing import Any

    try:
        supabase_url = "https://dvnxmmwjpuuujdsjpmft.supabase.co"
        supabase_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR2bnhtbXdqcHV1dWpkc2pwbWZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkxMzIzNzksImV4cCI6MjA2NDcwODM3OX0.OVO-XPigErZOFyVOEVdPa6pHXtHEYGIIG637IhGFhSE"  # Replace with secure loading in production

        # Alpha Vantage API setup
        alphavantage_key = "5U09BYJ7JR7GVOQR"  # Replace this
        baseurl_begin = (
            "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol="
        )
        baseurl_end = f"&apikey={alphavantage_key}"

        stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        char_list: List[Any] = []

        for stock in stocks:
            url = f"{baseurl_begin}{stock}{baseurl_end}"
            r = requests.get(url)
            if r.status_code != 200:
                print(f"Failed to get data for {stock}, status: {r.status_code}")
                continue

            response = r.json()
            time_series = response.get("Time Series (Daily)", {})

            if not time_series:
                print(f"No data for {stock}: {response.get('Note') or response}")
                continue

            latest_date = sorted(time_series.keys(), reverse=True)[0]
            data = time_series[latest_date]

            try:
                char = {
                    "symbol": response["Meta Data"]["2. Symbol"],
                    "open": float(data["1. open"]),
                    "close": float(data["4. close"]),
                    "name": stock,  # Add this if your table expects a `name` field
                    "price_currency": "USD",
                    "date": latest_date,
                }
                char_list.append(char)
            except KeyError as e:
                print(f"Missing data for {stock}: {e}")
            except ValueError as e:
                print(f"Data conversion error for {stock}: {e}")

        # Push to Supabase
        for row in char_list:
            res = requests.post(
                f"{supabase_url}/rest/v1/stocks",  # Ensure this matches your Supabase table name
                headers={
                    "Content-Type": "application/json",
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {supabase_api_key}",
                    "Prefer": "return=representation",
                },
                json=row,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "stocks_all": char_list,
    }
    return res


async def get_users(db: Session):

    query = db.query(models.Users)

    users_all = query.all()
    users_all = (
        [new_data.to_dict() for new_data in users_all] if users_all else users_all
    )
    res = {
        "users_all": users_all,
    }
    return res


async def get_login(db: Session, email: str, password: str):

    query = db.query(models.Users)
    query = query.filter(
        and_(models.Users.email == email, models.Users.password == password)
    )

    has_record = query.all()
    has_record = (
        [new_data.to_dict() for new_data in has_record] if has_record else has_record
    )
    res = {
        "has_record": has_record,
    }
    return res


async def get_buynsellcalci(db: Session, quantity: int):

    query = db.query(models.PreciousMetals)

    all_metals = query.all()
    all_metals = (
        [new_data.to_dict() for new_data in all_metals] if all_metals else all_metals
    )

    try:
        gold_price = all_metals[0]["price_per_gram"]

        amount = gold_price * quantity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "amount": amount,
    }
    return res


async def get_transaction_logs(db: Session, email: str):

    transaction_logs = aliased(models.Transaction)
    query = db.query(models.Users, transaction_logs)

    query = query.join(transaction_logs, and_(models.Users.email == email))

    transaction_logs = query.all()
    transaction_logs = (
        [
            {
                "transaction_logs_1": (
                    s1.to_dict() if hasattr(s1, "to_dict") else s1.__dict__
                ),
                "transaction_logs_2": (
                    s2.to_dict() if hasattr(s2, "to_dict") else s2.__dict__
                ),
            }
            for s1, s2 in transaction_logs
        ]
        if transaction_logs
        else transaction_logs
    )
    res = {
        "output": transaction_logs,
    }
    return res


async def get_buynsellsilver(db: Session, quantity: int):

    query = db.query(models.PreciousMetals)

    all_metals = query.all()
    all_metals = (
        [new_data.to_dict() for new_data in all_metals] if all_metals else all_metals
    )

    try:
        price = all_metals[1]["price_per_gram"]

        amount = price * quantity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "amount": amount,
    }
    return res
