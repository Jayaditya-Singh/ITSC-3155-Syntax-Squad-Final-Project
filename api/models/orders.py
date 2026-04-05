from sqlalchemy import Column, Integer, String, DECIMAL, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    promotion_id = Column(Integer, ForeignKey("promotions.id"), nullable=True)
    order_date = Column(DATETIME, nullable=False, default=datetime.now)
    tracking_number = Column(String(50), unique=True, nullable=True)
    order_status = Column(String(50), nullable=False, server_default='Pending')
    order_type = Column(String(20), nullable=False, server_default='Takeout')
    total_price = Column(DECIMAL(8, 2), nullable=False, server_default='0.00')

    customer = relationship("Customer", back_populates="orders")
    promotion = relationship("Promotion", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)
    review = relationship("Review", back_populates="order", uselist=False)