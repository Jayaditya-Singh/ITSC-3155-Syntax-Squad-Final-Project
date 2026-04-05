from typing import Optional
from pydantic import BaseModel
from .menu_items import MenuItem
from .resources import Resource


class RecipeBase(BaseModel):
    amount: float


class RecipeCreate(RecipeBase):
    menu_item_id: int
    resource_id: int


class RecipeUpdate(BaseModel):
    menu_item_id: Optional[int] = None
    resource_id: Optional[int] = None
    amount: Optional[float] = None


class Recipe(RecipeBase):
    id: int
    menu_item: Optional[MenuItem] = None
    resource: Optional[Resource] = None

    class ConfigDict:
        from_attributes = True