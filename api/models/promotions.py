from sqlalchemy import Column, Integer, String, DECIMAL, DATETIME, Boolean
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    promo_code = Column(String(50), unique=True, nullable=False)
    discount_percent = Column(DECIMAL(5, 2), nullable=True)
    discount_amount = Column(DECIMAL(6, 2), nullable=True)
    expiration_date = Column(DATETIME, nullable=False)
    is_active = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="promotion")