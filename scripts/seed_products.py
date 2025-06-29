import random
import string
from decimal import Decimal
from sqlalchemy.orm import Session
import sys
import os

# Adjust the Python path to include the root directory of the project
# This allows importing modules from the 'app' package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Product as ProductModel # Alias to avoid conflict with local Product variable
from app import schemas # For potential use with Pydantic models if needed, though direct model usage is fine here

# Predefined lists for more realistic random data
CATEGORIES = ["Electronics", "Books", "Home & Kitchen", "Sports & Outdoors", "Clothing", "Toys & Games", "Beauty"]
SUB_CATEGORIES_MAP = {
    "Electronics": ["Computers", "Smartphones", "Audio", "Cameras"],
    "Books": ["Fiction", "Non-Fiction", "Science", "Comics"],
    "Home & Kitchen": ["Appliances", "Furniture", "Decor", "Cookware"],
    "Sports & Outdoors": ["Fitness", "Camping", "Cycling", "Team Sports"],
    "Clothing": ["Men's", "Women's", "Kids'", "Shoes"],
    "Toys & Games": ["Board Games", "Action Figures", "Dolls", "Puzzles"],
    "Beauty": ["Makeup", "Skincare", "Haircare", "Fragrance"]
}
PRODUCT_NAME_PREFIXES = ["Awesome", "Ultimate", "Premium", "Eco-Friendly", "Smart", "Classic", "Modern", "Compact"]
PRODUCT_NAME_SUFFIXES = ["Device", "Gadget", "Tool", "Kit", "Set", "System", "Solution", "Appliance", "Wear", "Book"]

def generate_random_asin():
    """Generates a random 10-character ASIN-like string (uppercase letters and digits)."""
    return 'B0' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_random_products(db: Session, count: int = 10):
    """Creates a specified number of random products in the database."""
    created_products = []
    existing_asins = {p.asin for p in db.query(ProductModel.asin).all()}

    for i in range(count):
        category = random.choice(CATEGORIES)
        sub_category = random.choice(SUB_CATEGORIES_MAP[category])
        name_prefix = random.choice(PRODUCT_NAME_PREFIXES)
        name_suffix = random.choice(PRODUCT_NAME_SUFFIXES)

        product_name = f"{name_prefix} {sub_category.rstrip('s')} {name_suffix}"

        asin = generate_random_asin()
        while asin in existing_asins: # Ensure ASIN is unique
            asin = generate_random_asin()
        existing_asins.add(asin)

        avg_selling_price = Decimal(random.uniform(10.0, 300.0)).quantize(Decimal("0.01"))
        cost_of_goods_sold = (avg_selling_price * Decimal(random.uniform(0.3, 0.7))).quantize(Decimal("0.01"))
        initial_cvr_baseline = random.uniform(0.01, 0.15) # 1% to 15% CVR

        product_data = schemas.ProductCreate( # Using Pydantic schema for validation before model creation
            asin=asin,
            product_name=product_name,
            category=category,
            sub_category=sub_category,
            avg_selling_price=avg_selling_price,
            cost_of_goods_sold=cost_of_goods_sold,
            initial_cvr_baseline=initial_cvr_baseline
        )

        db_product = ProductModel(**product_data.model_dump())
        db.add(db_product)
        created_products.append(db_product)
        print(f"Generated product {i+1}/{count}: {db_product.product_name} (ASIN: {db_product.asin})")

    try:
        db.commit()
        for prod in created_products:
            db.refresh(prod) # To get IDs if needed later, though not strictly necessary here
        print(f"\nSuccessfully created and committed {len(created_products)} products.")
    except Exception as e:
        db.rollback()
        print(f"\nError creating products: {e}")
        print("Rolled back changes.")

    return created_products

if __name__ == "__main__":
    print("Starting product seeding script...")
    # Create all tables if they don't exist (useful if running script standalone without Alembic)
    # Base.metadata.create_all(bind=engine)
    # However, it's better to rely on Alembic migrations being run first.
    # If tables don't exist, this script will fail at the query for existing_asins.

    db = SessionLocal()
    try:
        # Check if product table exists, if not, inform user to run migrations
        if not engine.dialect.has_table(engine.connect(), "products"):
             print("\nERROR: 'products' table not found. Please run Alembic migrations first:")
             print("  `python -m alembic upgrade head`")
             sys.exit(1)

        # Optional: Clear existing products before seeding? For now, we just add.
        # db.query(ProductModel).delete()
        # db.commit()
        # print("Cleared existing products.")

        num_to_create = 10
        print(f"Attempting to create {num_to_create} new random products...")
        newly_created = create_random_products(db, count=num_to_create)

        if newly_created:
            print("\nSample of created products (up to 3):")
            for p in newly_created[:3]:
                print(f"  ID: {p.id}, Name: {p.product_name}, ASIN: {p.asin}, Price: {p.avg_selling_price}")
        else:
            print("No new products were created (this might be an error or count was 0).")

    finally:
        db.close()
    print("\nProduct seeding script finished.")
