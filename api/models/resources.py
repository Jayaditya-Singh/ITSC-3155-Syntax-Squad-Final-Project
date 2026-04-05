from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False, server_default='0.00')
    unit = Column(String(20), nullable=False)

    recipes = relationship("Recipe", back_populates="resource")