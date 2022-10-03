import asyncio
from typing import TypedDict

from sqlalchemy import Column, BigInteger, JSON

from gino import Gino

from config import DB_URI


db = Gino()


class User(db.Model):
    __tablename__ = 'bot_database'
    user_id = Column(BigInteger, primary_key=True)
    user_data = Column(JSON)


class UserData(TypedDict):
    keywords: list


async def get_user(user_id: int) -> User:
    return await User.get(user_id)


async def get_all_users() -> list[User, ]:
    return await User.query.gino.all()


async def create_new_user(user_id: int, user_data: UserData) -> None:
    await User.create(user_id=user_id, user_data=user_data)


async def update_user_data(user_id: int, user_data: UserData) -> None:
    await User.update.values(user_data=user_data).where(User.user_id == user_id).gino.status()


async def set_db_connection() -> None:
    await db.set_bind(DB_URI)


async def create_database() -> None:
    await db.set_bind(DB_URI)
    await db.gino.create_all()


if __name__ == "__main__":
    asyncio.run(create_database())
