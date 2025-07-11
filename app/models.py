from datetime import datetime
from typing import TypeVar
from enum import Enum

from sqlalchemy import Column, Integer, Text, String, DateTime, BigInteger, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, class_mapper
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declarative_base

from app.database import uniq_str_an, str_an


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(server_default=func.now())

    async def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


ModelClass = TypeVar('ModelClass', bound=Base)  # Generic тип для модели


class ComplaintStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"


class Sentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class Category(Enum):
    TECHNICAL = "техническая"
    PAYMENT = "оплата"
    OTHER = "другое"


class Complaint(Base):
    __tablename__ = "complaints"

    text: Mapped[uniq_str_an]
    status: Mapped[ComplaintStatus] = mapped_column(String, nullable=False, default=ComplaintStatus.OPEN.value)
    sentiment: Mapped[Sentiment] = mapped_column(String, nullable=False)
    category: Mapped[Category] = mapped_column(String, nullable=False, default=Category.OTHER.value)
    