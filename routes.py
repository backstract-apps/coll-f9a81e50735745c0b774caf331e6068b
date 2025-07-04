from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile,Query, Form
from sqlalchemy.orm import Session
from typing import List,Annotated
import service, models, schemas
from fastapi import Query
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/precious_metals/')
async def get_precious_metals(db: Session = Depends(get_db)):
    try:
        return await service.get_precious_metals(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/buygold')
async def get_buygold(quantity: int, email: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.get_buygold(db, quantity, email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/precious_metals/metal')
async def get_precious_metals_metal(metal: int, db: Session = Depends(get_db)):
    try:
        return await service.get_precious_metals_metal(db, metal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/precious_metals/')
async def post_precious_metals(raw_data: schemas.PostPreciousMetals, db: Session = Depends(get_db)):
    try:
        return await service.post_precious_metals(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/precious_metals/metal/')
async def put_precious_metals_metal(metal: Annotated[str, Query(max_length=100)], price_per_gram: float, db: Session = Depends(get_db)):
    try:
        return await service.put_precious_metals_metal(db, metal, price_per_gram)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/precious_metals/metal')
async def delete_precious_metals_metal(metal: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_precious_metals_metal(db, metal)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/smoothies/')
async def get_smoothies(db: Session = Depends(get_db)):
    try:
        return await service.get_smoothies(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/smoothies/id')
async def get_smoothies_id(id: int, db: Session = Depends(get_db)):
    try:
        return await service.get_smoothies_id(db, id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/smoothies/')
async def post_smoothies(raw_data: schemas.PostSmoothies, db: Session = Depends(get_db)):
    try:
        return await service.post_smoothies(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/smoothies/id/')
async def put_smoothies_id(id: int, created_at: str, title: Annotated[str, Query(max_length=100)], method: Annotated[str, Query(max_length=100)], rating: int, db: Session = Depends(get_db)):
    try:
        return await service.put_smoothies_id(db, id, created_at, title, method, rating)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/smoothies/id')
async def delete_smoothies_id(id: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_smoothies_id(db, id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/users/email')
async def get_users_email(email: int, db: Session = Depends(get_db)):
    try:
        return await service.get_users_email(db, email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/users/')
async def post_users(raw_data: schemas.PostUsers, db: Session = Depends(get_db)):
    try:
        return await service.post_users(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/users/email/')
async def put_users_email(username: Annotated[str, Query(max_length=100)], email: Annotated[str, Query(max_length=100)], password: Annotated[str, Query(max_length=100)], gold_in_gram: float, silver_in_gram: float, db: Session = Depends(get_db)):
    try:
        return await service.put_users_email(db, username, email, password, gold_in_gram, silver_in_gram)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/users/email')
async def delete_users_email(email: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_users_email(db, email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/crypto/')
async def get_crypto(db: Session = Depends(get_db)):
    try:
        return await service.get_crypto(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/crypto/symbol')
async def get_crypto_symbol(symbol: int, db: Session = Depends(get_db)):
    try:
        return await service.get_crypto_symbol(db, symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/crypto/')
async def post_crypto(raw_data: schemas.PostCrypto, db: Session = Depends(get_db)):
    try:
        return await service.post_crypto(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/crypto/symbol/')
async def put_crypto_symbol(symbol: Annotated[str, Query(max_length=100)], open: float, close: float, name: Annotated[str, Query(max_length=100)], price_currency: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.put_crypto_symbol(db, symbol, open, close, name, price_currency)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/crypto/symbol')
async def delete_crypto_symbol(symbol: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_crypto_symbol(db, symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/stocks/symbol')
async def get_stocks_symbol(symbol: int, db: Session = Depends(get_db)):
    try:
        return await service.get_stocks_symbol(db, symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/stocks/')
async def post_stocks(raw_data: schemas.PostStocks, db: Session = Depends(get_db)):
    try:
        return await service.post_stocks(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/stocks/symbol/')
async def put_stocks_symbol(symbol: Annotated[str, Query(max_length=100)], open: float, close: float, name: Annotated[str, Query(max_length=100)], price_currency: Annotated[str, Query(max_length=100)], date: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.put_stocks_symbol(db, symbol, open, close, name, price_currency, date)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/stocks/symbol')
async def delete_stocks_symbol(symbol: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_stocks_symbol(db, symbol)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/rickandmorty/')
async def get_rickandmorty(db: Session = Depends(get_db)):
    try:
        return await service.get_rickandmorty(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/rickandmorty/name')
async def get_rickandmorty_name(name: int, db: Session = Depends(get_db)):
    try:
        return await service.get_rickandmorty_name(db, name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/rickandmorty/')
async def post_rickandmorty(raw_data: schemas.PostRickandmorty, db: Session = Depends(get_db)):
    try:
        return await service.post_rickandmorty(db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/sellgold')
async def get_sellgold(quantity: int, email: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.get_sellgold(db, quantity, email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/rickandmorty/name/')
async def put_rickandmorty_name(name: Annotated[str, Query(max_length=100)], no_of_episodes: float, db: Session = Depends(get_db)):
    try:
        return await service.put_rickandmorty_name(db, name, no_of_episodes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/rickandmorty/name')
async def delete_rickandmorty_name(name: int, db: Session = Depends(get_db)):
    try:
        return await service.delete_rickandmorty_name(db, name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/stocks/')
async def get_stocks(db: Session = Depends(get_db)):
    try:
        return await service.get_stocks(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/users/')
async def get_users(db: Session = Depends(get_db)):
    try:
        return await service.get_users(db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/login')
async def get_login(email: Annotated[str, Query(max_length=100)], password: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.get_login(db, email, password)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/buynsellcalci')
async def get_buynsellcalci(quantity: int, db: Session = Depends(get_db)):
    try:
        return await service.get_buynsellcalci(db, quantity)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/transaction_logs')
async def get_transaction_logs(email: Annotated[str, Query(max_length=100)], db: Session = Depends(get_db)):
    try:
        return await service.get_transaction_logs(db, email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/buynsellsilver')
async def get_buynsellsilver(quantity: int, db: Session = Depends(get_db)):
    try:
        return await service.get_buynsellsilver(db, quantity)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

