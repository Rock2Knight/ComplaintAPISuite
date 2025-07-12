"""Module for testing post-request for complaint"""
import asyncio
from typing import Type, TypeVar, Any

import pytest
from sqlalchemy import select, delete
from loguru import logger

from app.models import Complaint


@pytest.mark.complaint
@pytest.mark.asyncio(scope="session")
async def test_create_complaint(client, test_data, async_session_maker):
    """Testing post-request for complaint."""
    for key in test_data.keys():
        if key in ("OTHER_NEUT", "TEST_DATA_FOR_CLOSING"):
            continue
        
        text = test_data[key]["text"]
        category = test_data[key]["category"]
        sentiment = test_data[key]["sentiment"]
        status = test_data[key]["status"]
        
        # Удаляем объект из тестовой базы данных, если такой там есть
        async with async_session_maker() as session:
            query = select(Complaint).filter_by(text=text)
            result = await session.execute(query)
            complaint = result.scalar_one_or_none()
            if complaint:
                await session.delete(complaint)
                await session.commit()

        logger.info(f"User complaint: {text}")
        logger.info(f"Expected category: {category}")
        logger.info(f"Expected sentiment: {sentiment}")
        logger.info(f"Expected status: {status}\n")

        response = await client.post("/complaint/", json={"text": text})
        response_body = response.json()
        logger.info(f"Response: {response_body}\n")
        assert response.status_code == 201

        complaint = None
        async with async_session_maker() as session:
            query = select(Complaint).filter_by(id=response.json()["id"])
            result = await session.execute(query)
            complaint = result.scalar_one_or_none()

        id = complaint.id
        category = complaint.category
        sentiment = complaint.sentiment    
        status = complaint.status

        logger.info(f"Response: {response_body}\n")
        assert response_body["id"] == id
        assert response_body["sentiment"] == sentiment
        assert response_body["status"] == status

        if "category" in response_body.keys():
            assert response_body["category"] == category


@pytest.mark.open_last_hour_complaints
@pytest.mark.asyncio(scope="session")
async def test_check_open_complaints_no_open_complaints(
    client,
    async_session_maker
):
    """Test when there are no open complaints within last hour."""

    # Delete all complaints from test database
    async with async_session_maker() as session:
        await session.execute(delete(Complaint))
        await session.commit()
    
    response = await client.patch("/complaint/check_open_complaints")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.open_last_hour_complaints
@pytest.mark.asyncio
async def test_check_open_complaints_success(
    client,
    test_data,
    async_session_maker
):
    """Test error handling when database error occurs."""
    complaints = list([])

    # Delete all complaints from test database
    async with async_session_maker() as session:
        await session.execute(delete(Complaint))
        await session.commit()
        test_data_for_method = test_data["TEST_DATA_FOR_CLOSING"]
        for complaint_dump in test_data_for_method:
            complaint = Complaint(**complaint_dump)
            session.add(complaint)
            await session.commit()    
            await session.refresh(complaint)
            complaints.append(complaint)

        # DEBUG: проверяем, что тестовые данные загружены в базу
        log_query = select(Complaint).filter_by(status="open").order_by(Complaint.id)
        result = await session.execute(log_query)
        await session.commit()
        open_complaints = result.scalars().all()
        oc_dump = [await complaint.to_dict() for complaint in open_complaints]
        list(map(lambda x: logger.info(f"Created complaints: {x}"), oc_dump))
            

    # Update open complaints for last hour by http-request    
    response = await client.patch("/complaint/check_open_complaints")
    assert response.status_code == 200
    
    # Check that all complaints are closed
    closed_complaints = response.json()
    for complaint in closed_complaints:
        if complaint.get("category") != "другое":
            assert complaint.get("status") == "closed"
