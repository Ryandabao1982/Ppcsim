from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, models, schemas, auth # models for current_user
from app.database import get_db

router = APIRouter(
    prefix="/api/products",
    tags=["Product Catalog"],
    # For MVP, let's make product management available to any authenticated user.
    # In a real app, this might be restricted to admin roles or specific user permissions.
    dependencies=[Depends(auth.get_current_user)]
)

@router.post("/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_new_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
    # current_user: models.User = Depends(auth.get_current_user) # User not directly linked to product in current model
):
    # Check for existing ASIN, as it should be unique
    db_product_by_asin = crud.get_product_by_asin(db, asin=product.asin)
    if db_product_by_asin:
        raise HTTPException(status_code=400, detail=f"Product with ASIN {product.asin} already exists.")
    return crud.create_product(db=db, product=product)

@router.get("/", response_model=List[schemas.Product])
def read_all_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@router.get("/{product_id}", response_model=schemas.Product)
def read_single_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/{product_id}", response_model=schemas.Product)
def update_existing_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    # Check if new ASIN (if provided) conflicts with another product
    if product_update.asin:
        existing_product_with_new_asin = crud.get_product_by_asin(db, asin=product_update.asin)
        if existing_product_with_new_asin and existing_product_with_new_asin.id != product_id:
            raise HTTPException(status_code=400, detail=f"Another product with ASIN {product_update.asin} already exists.")

    updated_product = crud.update_product(db=db, product_id=product_id, product_update=product_update)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}", response_model=schemas.Message, status_code=status.HTTP_200_OK)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    db_product = crud.get_product(db, product_id=product_id) # Fetches the product to check existence and relationships
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if db_product.in_campaigns: # Check if the product is part of any campaigns
        campaign_names = [c.campaign_name for c in db_product.in_campaigns[:3]]
        detail_message = f"Product is currently advertised in campaigns (e.g., {', '.join(campaign_names)}{'...' if len(db_product.in_campaigns) > 3 else ''}) and cannot be deleted directly. Please remove it from campaigns first."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail_message)

    # If not in campaigns, proceed with deletion
    deleted_product_obj = crud.delete_product(db=db, product_id=product_id)
    if deleted_product_obj is None: # Should ideally not happen if first check passed, but good for safety
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found during deletion attempt.")

    return schemas.Message(detail=f"Product ID {product_id} deleted successfully.")

# Removed the alternative delete endpoint as the primary one is now updated.
