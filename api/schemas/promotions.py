from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PromotionBase(BaseModel):
    promo_code: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    expiration_date: datetime
    is_active: Optional[bool] = True


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    promo_code: Optional[str] = None
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    expiration_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Promotion(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True