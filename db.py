import asyncio
from sqlalchemy import Column, BigInteger, JSON

from gino import Gino

from app.config import DB_URI


async def get_all_users_id() -> list:
    return []


async def get_user_data(user_id: int) -> User:
    return User
