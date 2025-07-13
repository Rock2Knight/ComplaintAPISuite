from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError, ProgrammingError
)

from app.database import connection
from app.models import Complaint


@connection
async def get_open_complaints(**kwargs) -> list[Complaint]:
    """Получает открытые жалобы за последний час."""
    session = kwargs.pop("session")
    try:
        get_open_complaints = select(Complaint).filter_by(status="open")
        get_open_complaints = get_open_complaints.filter(
            Complaint.timestamp >= datetime.now() - timedelta(hours=1)
        )
        result = await session.execute(get_open_complaints)
        await session.commit()
        open_complaints = result.scalars().all()
        return open_complaints
    except Exception as e:
        await session.rollback()
        if isinstance(e, IntegrityError) or isinstance(e, ProgrammingError):
            raise HTTPException(status_code=500, args=e.args, detail=str(e))
    finally:
        await session.close()


@connection
async def close_complaint(**kwargs) -> Complaint | None:
    """Закрывает жалобу по id."""
    session = kwargs.pop("session")
    complaint_id = kwargs.pop("id")

    try:
        # Ищем открытые за последний час жалобы
        get_complaint = select(Complaint).filter_by(id=complaint_id)
        result = await session.execute(get_complaint)
        await session.commit()
        complaint = result.scalar_one_or_none()
        if not complaint:
            return None
        
        complaint.status = "closed"
        await session.commit()
        await session.refresh(complaint)
        return complaint
    except Exception as e:
        await session.rollback()
        if isinstance(e, IntegrityError) or isinstance(e, ProgrammingError):
            raise HTTPException(status_code=500, detail=str(e.args))
    finally:
        await session.close()