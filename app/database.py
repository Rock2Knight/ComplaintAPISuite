from datetime import datetime
from typing import Annotated
from functools import wraps

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import mapped_column

from app.config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uniq_str_an = Annotated[str, mapped_column(nullable=False, unique=True)]
str_an = Annotated[str, mapped_column(nullable=False)]

# Декоратор для работы с сессией в асинхронных методах
def connection(method):

    @wraps(method)
    async def wrapper(*args, **kwargs):

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if 'session' in kwargs.keys():
            kwargs.pop('session')

        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper
