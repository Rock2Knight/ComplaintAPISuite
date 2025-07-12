from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.database import connection
from app.models import Complaint


class ComplaintLoader:

    @classmethod
    @connection
    async def get(cls, session: AsyncSession, item_id: int) -> Complaint | None:
        """Получает жалобу по ID."""
        query = select(Complaint).filter_by(id=item_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


    @classmethod
    @connection
    async def create(cls, session: AsyncSession, **kwargs) -> Complaint:
        """Создает новую жалобу."""
        if "session" in kwargs.keys():
            kwargs.pop("session")

        item = Complaint(**kwargs)
        session.add(item)
        try:
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            raise HTTPException(status_code=500, args=e.args, detail=str(e))
        return item


    @classmethod
    @connection
    async def update(cls, session: AsyncSession, **kwargs) -> Complaint | None:
        """Обновляет жалобу."""
        if "session" in kwargs.keys():
            kwargs.pop("session")

        item_id = kwargs.pop('item_id')

        query_select = select(Complaint).filter_by(id=item_id)
        item = await session.scalars(query_select)

        if not item:
            return None
        
        item = item.first()
        if not item:
            return None
            
        for key, value in kwargs.items():
            setattr(item, key, value)

        try:    
            await session.commit()
            await session.refresh(item)
        except Exception as e:
            raise HTTPException(status_code=500, args=e.args, detail=str(e))
        return item


    @classmethod
    @connection
    async def delete(cls, session: AsyncSession, item_id: int) -> dict[str, Any]:
        """Удаляет жалобу и возвращает ее данные в виде словаря."""
        query_select = select(Complaint).filter_by(id=item_id)
        item = await session.scalars(query_select)

        if item is None:
            logger.error(f'Complaint {item_id} not found')
            raise HTTPException(status_code=404, detail=f'Complaint {item_id} not found')
        item = item.first()
        if item is None:
            logger.error(f'Complaint {item_id} not found')
            raise HTTPException(status_code=404, detail=f'Complaint {item_id} not found')
            
        item_dict = await item.to_dict()
        logger.info(f'Info about {item}:\n {item_dict}')
        await session.delete(item)
        logger.info(f'Complaint {item_id} deleted')
        await session.commit()
        logger.info(f'Query is commited')
        return item_dict