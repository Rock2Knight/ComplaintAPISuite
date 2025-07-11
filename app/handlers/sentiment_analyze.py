"""Модуль для анализа тональности текста."""
import asyncio
from pathlib import Path
from typing import Dict, Any

import aiohttp
from loguru import logger
from fastapi import HTTPException

from app.config import settings
from app.exceptions import API_EXCEPTIONS


SENTIMENT_API_KEY = settings.get_sentiment_api_key()


async def sentiment_analyze(text: str) -> str:
    """Анализ тональности текста."""
    url = "https://api.promptapi.com/sentiment/analysis"
    
    headers = {
        "Content-Type": "application/json",
        "apikey": SENTIMENT_API_KEY
    }

    params = {
        "text": text
    }

    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=params) as response:
                if response.status == 200:
                    response_body = await response.json()
                    sentiment = response_body["sentiment"]
                    sentiments = list(["positive", "negative", "neutral"])
                    logger.info(f"Raw sentiment: {sentiment}")

                    if sentiment in sentiments:
                        return sentiment
                    matched = next((s for s in sentiments if s in sentiment), None)
                    logger.info(f"Handled sentiment: {matched}")
                    if matched:
                        return matched
                    raise ValueError(f"Sentiment {sentiment} not found")
                else:
                    return "unknown"
    except Exception as e:
        if any(isinstance(e, exc) for exc in API_EXCEPTIONS):
            if isinstance(e, aiohttp.ClientConnectionError):
                logger.error("Проблема с соединением")
                logger.error(f"Тело ответа: \n{e}")
            elif isinstance(e, aiohttp.ClientResponseError):
                logger.error(f"Ошибка ответа: {e.status}")
                logger.error(f"Тело ответа: \n{e}")
            elif isinstance(e, aiohttp.InvalidURL):
                logger.error("URL недействителен")
                logger.error(f"Тело ответа: \n{e}")
            elif isinstance(e, asyncio.TimeoutError):
                logger.error("Истекло время ожидания")
                logger.error(f"Тело ответа: \n{e}")
            else:
                logger.error("Неизвестная ошибка")
                logger.error(f"Тело ответа: \n{e}")
                
            return "unknown"

        detail = "Ошибка на стороне API"
        if hasattr(e, 'detail'):
            detail = e.detail
        raise HTTPException(status_code=500, detail=detail)