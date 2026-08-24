from app.models.base import Base

from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.models.shopping_item import ShoppingItem
from app.models.shopping_history import ShoppingHistory
from app.models.search_history import SearchHistory
from app.models.user_preferences import UserPreference

__all__ = [
    "Base",
    "Brand",
    "Category",
    "Product",
    "User",
    "ShoppingItem",
    "ShoppingHistory",
    "SearchHistory",
    "UserPreference",
]
