from sqlalchemy import Column, Integer, String, ForeignKey, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    payment_type = Column(String(50), nullable=False)
    card_last_four = Column(String(4), nullable=True)
    transaction_status = Column(String(50), nullable=False, server_default='Pending')
    transaction_date = Column(DATETIME, nullable=False, default=datetime.now)

    order = relationship("Order", back_populates="payment")