from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError, ProgrammingError
)

from app.database import connection
from app.models import Complaint


@connection
async def check_complaints(**kwargs) -> list[Complaint]:
    """Закрывает жалобы."""
    session = kwargs.pop("session")
    closed_complaints = list([])

    try:
        # Ищем открытые за последний час жалобы
        get_open_complaints = select(Complaint).filter_by(status="open")
        get_open_complaints = get_open_complaints.filter(
            Complaint.timestamp >= datetime.now() - timedelta(hours=1)
        )
        result = await session.execute(get_open_complaints)
        await session.commit()
        open_complaints = result.scalars().all()

        # Закрываем найденные жалобы
        for complaint in open_complaints:
            complaint.status = "closed"
            await session.commit()
            await session.refresh(complaint)
            closed_complaints.append(complaint)
        return closed_complaints
    except Exception as e:
        await session.rollback()
        if isinstance(e, IntegrityError) or isinstance(e, ProgrammingError):
            raise HTTPException(status_code=500, detail=str(e.args))
    finally:
        await session.close()