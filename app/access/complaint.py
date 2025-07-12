from typing import Optional

from fastapi import HTTPException

from app.handlers import (
    sentiment_analyze, 
    classify_text_async, 
    check_complaints
)
from app.loaders.complaint import ComplaintLoader
from app.models import Complaint, Category
from app.utils.dict_cleaner import remove_keys


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

            complaint_dump = remove_keys(
                keys=["text", "timestamp"], 
                data=complaint_dump
            )

            return complaint_dump

        case "patch":
            if kwargs["route"] == "check_open_complaints":
                closed_complaints = await check_complaints()

                if not closed_complaints:
                    return []

                complaints_dump = [
                    await complaint.to_dict() 
                    for complaint 
                    in closed_complaints
                ]

                list(map(
                    lambda x: remove_keys(
                        keys=["text", "timestamp"], 
                        data=x
                    ), 
                    complaints_dump
                ))
                
                return complaints_dump
                
        case "delete":
            item_dict = await ComplaintLoader.delete(item_id=kwargs['id'])
            return item_dict
            