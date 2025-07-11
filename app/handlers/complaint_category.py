"""Определние категории текста с помощью GPT3.5-turbo."""
import openai
from openai import AsyncOpenAI, OpenAIError
from loguru import logger
from fastapi import HTTPException

from app.config import settings

client = AsyncOpenAI(api_key=settings.get_openai_api_key())

async def classify_text_async(text: str, categories: list[str]) -> str:
    """Определние категории текста с помощью GPT3.5-turbo."""
    category_prompt = ", ".join(categories)

    system_prompt = (
        "Ты классификатор текста. " +
        "Твоя задача — выбрать только одну категорию из предложенного списка, " +
        "которая наиболее точно соответствует содержанию текста."
    )

    user_prompt = (
        f"Текст: \"{text}\"\n" +
        f"Категории: {category_prompt}\n" +
        "Ответь только названием одной наиболее подходящей категории."
    )
    logger.info(f"User prompt: {user_prompt}")

    
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0
        )
        logger.info(f"Категория текста: \"{text}\":")
        logger.info(response.choices[0].message.content.strip(), "\n")
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        logger.error(f"Ошибка классификации текста: {e}")
        
        if isinstance(e, openai.APIError):
            logger.error(f"API Error: {e}")
            return "другое"
        detail = "Ошибка на стороне API"
        if hasattr(e, 'detail'):
            detail = e.detail
        raise HTTPException(status_code=500, detail=detail)