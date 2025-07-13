from typing import Optional

from fastapi import HTTPException

from app.handlers import (
    sentiment_analyze, 
    classify_text_async, 
    close_complaint,
    get_open_complaints
)
from app.loaders.complaint import ComplaintLoader
from app.models import Complaint, Category
from app.utils.dict_cleaner import remove_keys


async def access_complaint(**kwargs) -> Optional[Complaint | HTTPException]:
    match kwargs['method']:
        case "get":
            if kwargs.get('route', None) and kwargs['route'] == "get_open_complaints":
                open_complaints = await get_open_complaints()

                if not open_complaints:
                    return []

                complaints_dump = [
                    await complaint.to_dict() 
                    for complaint 
                    in open_complaints
                ]

                return complaints_dump

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

            complaint_dump = remove_keys(
                keys=["text", "timestamp"], 
                data=complaint_dump
            )

            return complaint_dump

        case "patch":
            if kwargs.get("route", None) and kwargs["route"] == "close_complaint":
                kwargs.pop("route")
                closed_complaint = await close_complaint(**kwargs)

                if not closed_complaint:
                    return {}

                return await closed_complaint.to_dict()
                
        case "delete":
            return await ComplaintLoader.delete(item_id=kwargs['id'])
            