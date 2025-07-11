from typing_extensions import Self

from pydantic import BaseModel, conint, model_validator


class ComplaintDto:

    class Create(BaseModel):
        text: str

    class Response(BaseModel):
        id: conint(gt=0)
        status: str
        sentiment: str
        category: str | None = None

        @model_validator(mode="after")
        def validate_complaint(self) -> Self:
            allowed_statuses = ("open", "closed")
            allowed_sentiments = ("positive", "negative", "neutral", "unknown")
            allowed_categories = ("техническая", "оплата", "другое")

            if self.status not in allowed_statuses:
                raise ValueError(f"Status must be one of {allowed_statuses}")
            if self.sentiment not in allowed_sentiments:
                raise ValueError(f"Sentiment must be one of {allowed_sentiments}")
            if self.category:
                if self.category not in allowed_categories:
                    raise ValueError(f"Category must be one of {allowed_categories}")
            else:
                self.category = "другое"
            return self