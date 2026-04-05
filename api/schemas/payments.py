from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PaymentBase(BaseModel):
    payment_type: str
    card_last_four: Optional[str] = None
    transaction_status: Optional[str] = 'Pending'


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentUpdate(BaseModel):
    payment_type: Optional[str] = None
    card_last_four: Optional[str] = None
    transaction_status: Optional[str] = None


class Payment(PaymentBase):
    id: int
    order_id: int
    transaction_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True