import inspect
from datetime import datetime
from typing import Annotated
from functools import wraps

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import mapped_column
from loguru import logger

from app.config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(url=DATABASE_URL)
main_session_maker = async_sessionmaker(engine, expire_on_commit=False)

uniq_str_an = Annotated[str, mapped_column(nullable=False, unique=True)]
str_an = Annotated[str, mapped_column(nullable=False)]

# Декоратор для работы с сессией в асинхронных методах
def connection(method):

    @wraps(method)
    async def wrapper(*args, **kwargs):

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        sig = inspect.signature(method)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        # Если session уже был передан (в args или kwargs) — не подставляем заново
        if 'session' in bound_args.arguments:
            logger.info(f"Argument session is passed to {method.__name__} in kwargs")
            return await method(*args, **kwargs)

        async with main_session_maker() as session:
            logger.info(f"Session is been created for {method.__name__} and been passed to it as named parameter")
            try:
                logger.info(f"Session: {session}")
                logger.info(f"Args of CRUD-method: {args}")
                logger.info(f"Kwargs of CRUD-method: {kwargs}")
                kwargs.setdefault('session', session)
                return await method(*args, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper
