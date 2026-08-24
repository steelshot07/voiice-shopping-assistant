"""Seed the database with initial categories, brands, and products."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session

from app.database import engine
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product


CATEGORIES = [
    "Dairy", "Produce", "Bakery", "Beverages",
    "Snacks", "Personal Care", "Household", "Frozen", "Staples",
]

BRANDS = ["Amul", "Britannia", "Colgate", "Nestle", "Dove", "Surf Excel", "Generic"]

PRODUCTS = [
    # Produce
    ("Apples", "Generic", "Produce", "Fresh apples", 1, "kg", 150.00),
    ("Bananas", "Generic", "Produce", "Fresh bananas", 1, "dozen", 60.00),
    ("Oranges", "Generic", "Produce", "Fresh oranges", 1, "kg", 80.00),
    ("Mangoes", "Generic", "Produce", "Fresh mangoes", 1, "kg", 200.00),
    ("Grapes", "Generic", "Produce", "Fresh grapes", 500, "gram", 90.00),
    ("Tomatoes", "Generic", "Produce", "Fresh tomatoes", 1, "kg", 40.00),
    ("Potatoes", "Generic", "Produce", "Fresh potatoes", 1, "kg", 30.00),
    ("Onions", "Generic", "Produce", "Fresh onions", 1, "kg", 35.00),
    ("Carrots", "Generic", "Produce", "Fresh carrots", 1, "kg", 50.00),
    ("Spinach", "Generic", "Produce", "Fresh spinach", 1, "bunch", 20.00),
    ("Cucumber", "Generic", "Produce", "Fresh cucumber", 1, "kg", 40.00),
    ("Garlic", "Generic", "Produce", "Fresh garlic", 200, "gram", 60.00),
    ("Ginger", "Generic", "Produce", "Fresh ginger", 200, "gram", 50.00),
    ("Lemon", "Generic", "Produce", "Fresh lemons", 6, "pieces", 30.00),
    ("Coriander", "Generic", "Produce", "Fresh coriander leaves", 1, "bunch", 15.00),
    ("Green Chilies", "Generic", "Produce", "Fresh green chilies", 100, "gram", 20.00),
    ("Cabbage", "Generic", "Produce", "Fresh green cabbage", 1, "piece", 40.00),
    ("Cauliflower", "Generic", "Produce", "Fresh cauliflower", 1, "piece", 50.00),
    ("Capsicum", "Generic", "Produce", "Green bell pepper", 500, "gram", 60.00),
    ("Mushrooms", "Generic", "Produce", "Button mushrooms", 200, "gram", 55.00),
    # Dairy
    ("Milk", "Amul", "Dairy", "Fresh toned milk", 1, "litre", 68.00),
    ("Curd", "Amul", "Dairy", "Fresh curd", 400, "gram", 35.00),
    ("Butter", "Amul", "Dairy", "Salted butter", 500, "gram", 270.00),
    ("Cheese", "Amul", "Dairy", "Cheese slices", 200, "gram", 140.00),
    ("Paneer", "Amul", "Dairy", "Fresh paneer", 200, "gram", 90.00),
    ("Eggs", "Generic", "Dairy", "Farm fresh eggs", 6, "pack", 45.00),
    ("Ice Cream", "Amul", "Dairy", "Vanilla ice cream tub", 1, "litre", 200.00),
    # Staples
    ("Rice", "Generic", "Staples", "Basmati rice", 1, "kg", 120.00),
    ("Wheat Flour", "Generic", "Staples", "Whole wheat atta", 5, "kg", 220.00),
    ("Sugar", "Generic", "Staples", "Refined sugar", 1, "kg", 50.00),
    ("Salt", "Generic", "Staples", "Iodized salt", 1, "kg", 25.00),
    ("Toor Dal", "Generic", "Staples", "Toor dal / Pigeon pea", 1, "kg", 160.00),
    ("Moong Dal", "Generic", "Staples", "Yellow moong dal", 1, "kg", 140.00),
    ("Cooking Oil", "Generic", "Staples", "Refined sunflower oil", 1, "litre", 130.00),
    ("Pasta", "Generic", "Staples", "Penne pasta", 500, "gram", 90.00),
    ("Noodles", "Nestle", "Staples", "Instant noodles", 4, "pack", 56.00),
    ("Ketchup", "Generic", "Staples", "Tomato ketchup", 500, "gram", 120.00),
    ("Honey", "Generic", "Staples", "Pure honey", 500, "gram", 220.00),
    # Snacks
    ("Biscuits", "Britannia", "Snacks", "Digestive biscuits", 250, "gram", 50.00),
    ("Chips", "Generic", "Snacks", "Potato chips", 100, "gram", 30.00),
    ("Bread", "Britannia", "Bakery", "Whole wheat bread", 400, "gram", 45.00),
    ("Peanut Butter", "Generic", "Snacks", "Creamy peanut butter", 340, "gram", 150.00),
    ("Cornflakes", "Generic", "Snacks", "Breakfast cereal", 475, "gram", 180.00),
    ("Chocolate", "Nestle", "Snacks", "Milk chocolate bar", 50, "gram", 40.00),
    # Beverages
    ("Tea", "Generic", "Beverages", "Black tea leaves", 500, "gram", 250.00),
    ("Coffee", "Nestle", "Beverages", "Instant coffee", 100, "gram", 320.00),
    ("Green Tea", "Generic", "Beverages", "Green tea bags", 25, "pack", 150.00),
    ("Fruit Juice", "Generic", "Beverages", "Mixed fruit juice", 1, "litre", 110.00),
    ("Bottled Water", "Generic", "Beverages", "Packaged drinking water", 1, "litre", 20.00),
    # Household
    ("Dishwashing Liquid", "Generic", "Household", "Dish wash gel", 500, "ml", 105.00),
    ("Laundry Detergent", "Surf Excel", "Household", "Washing powder", 1, "kg", 190.00),
    ("Floor Cleaner", "Generic", "Household", "Disinfectant surface cleaner", 1, "litre", 180.00),
    ("Tissues", "Generic", "Household", "Facial tissues box", 100, "pulls", 70.00),
    ("Garbage Bags", "Generic", "Household", "Medium trash bags", 30, "pieces", 60.00),
    # Personal Care
    ("Shampoo", "Dove", "Personal Care", "Hair fall rescue shampoo", 340, "ml", 320.00),
    ("Soap", "Dove", "Personal Care", "Beauty bathing bar", 3, "pack", 160.00),
    ("Toothpaste", "Colgate", "Personal Care", "Strong teeth toothpaste", 150, "gram", 120.00),
    ("Toothbrush", "Colgate", "Personal Care", "Soft bristle toothbrush", 1, "piece", 40.00),
    ("Hand Wash", "Generic", "Personal Care", "Liquid hand wash", 750, "ml", 115.00),
    ("Deodorant", "Generic", "Personal Care", "Body spray", 150, "ml", 200.00),
]


def seed():
    with Session(engine) as db:
        # Categories
        cat_map = {}
        for name in CATEGORIES:
            obj = db.query(Category).filter_by(name=name).first()
            if not obj:
                obj = Category(name=name)
                db.add(obj)
                db.flush()
            cat_map[name] = obj.id

        # Brands
        brand_map = {}
        for name in BRANDS:
            obj = db.query(Brand).filter_by(name=name).first()
            if not obj:
                obj = Brand(name=name)
                db.add(obj)
                db.flush()
            brand_map[name] = obj.id

        # Products
        for name, brand_name, cat_name, desc, size_val, size_unit, price in PRODUCTS:
            exists = db.query(Product).filter_by(name=name).first()
            if not exists:
                db.add(Product(
                    name=name,
                    brand_id=brand_map[brand_name],
                    category_id=cat_map[cat_name],
                    description=desc,
                    size_value=size_val,
                    size_unit=size_unit,
                    price=price,
                    currency="INR",
                    available=True,
                ))

        db.commit()
        print(f"Seeded {len(PRODUCTS)} products successfully.")


if __name__ == "__main__":
    seed()
