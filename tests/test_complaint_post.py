"""Module for testing post-request for complaint"""
import asyncio
from typing import Type, TypeVar, Any

import pytest
from sqlalchemy import select, delete
from loguru import logger

from app.models import Complaint


@pytest.mark.complaint
@pytest.mark.asyncio(scope="session")
async def test_post_complaint(client, test_data, async_session_maker):
    """Testing post-request for complaint."""
    for key in test_data.keys():
        if key == "OTHER_NEUT":
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