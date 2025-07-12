import pytest
import asyncio

from loguru import logger

from app.handlers.complaint_category import classify_text_async

@pytest.mark.complaint_category
@pytest.mark.asyncio(scope="session")
async def test_category_of_complaint(test_data):
    """Testing classifing category of complaint by GPT3.5-Turbo."""
    for key in test_data.keys():
        if key in ("OTHER_NEUT", "TEST_DATA_FOR_CLOSING"):
            continue
        
        text = test_data[key]["text"]
        category = test_data[key]["category"]

        logger.info(f"User prompt: {text}")
        logger.info(f"Expected category: {category}")

        gotten_category = await classify_text_async(text, ["техническая", "оплата", "другое"])
        assert gotten_category.lower() == category.lower()
        await asyncio.sleep(0.5)