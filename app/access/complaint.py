from typing import Optional

from fastapi import HTTPException

from app.handlers import sentiment_analyze, classify_text_async
from app.loaders.complaint import ComplaintLoader
from app.models import Complaint, Category


async def access_complaint(**kwargs) -> Optional[Complaint | HTTPException]:
    match kwargs['method']:
        case "get":
            item = await ComplaintLoader.get(item_id=kwargs['id'])
            return await item.to_dict()
        case "post":
            sentiment = await sentiment_analyze(kwargs['dto']['text'])  # проводим анализ тональности текста
            kwargs['dto']['sentiment'] = sentiment
            
            complaint = await ComplaintLoader.create(**kwargs['dto'])

            categories = [category.value for category in Category]
            category = await classify_text_async(kwargs['dto']['text'], categories)  # определяем категорию жалобы
            category = category.lower()
            
            update_dict = {"item_id": complaint.id, "category": category}
            
            complaint = await ComplaintLoader.update(**update_dict)
            complaint_dump = await complaint.to_dict()

            complaint_dump.pop("text")
            complaint_dump.pop("timestamp")
            if complaint_dump["category"] == "другое":
                complaint_dump.pop("category")

            return complaint_dump
        case "delete":
            item_dict = await ComplaintLoader.delete(item_id=kwargs['id'])
            return item_dict
            