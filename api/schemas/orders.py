from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .order_details import OrderDetail
from .customers import Customer
from .promotions import Promotion


class OrderBase(BaseModel):
    order_type: str = 'Takeout'
    order_status: Optional[str] = 'Pending'
    total_price: Optional[float] = 0.00


class OrderCreate(OrderBase):
    customer_id: Optional[int] = None
    promotion_id: Optional[int] = None
    tracking_number: Optional[str] = None


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    promotion_id: Optional[int] = None
    order_type: Optional[str] = None
    order_status: Optional[str] = None
    tracking_number: Optional[str] = None
    total_price: Optional[float] = None


class Order(OrderBase):
    id: int
    customer_id: Optional[int] = None      # ← add this line
    promotion_id: Optional[int] = None     # ← add this line
    order_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    customer: Optional[Customer] = None
    promotion: Optional[Promotion] = None
    order_details: list[OrderDetail] = []

    class ConfigDict:
        from_attributes = True