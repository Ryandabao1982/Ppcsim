from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app import crud, models, schemas, auth
from app.database import get_db

router = APIRouter(
    prefix="/api/campaigns",
    tags=["Campaign Management"],
    dependencies=[Depends(auth.get_current_user)] # All routes here require authentication
)

# --- Campaign Endpoints ---
@router.post("/", response_model=schemas.Campaign, status_code=status.HTTP_201_CREATED)
def create_new_campaign(
    campaign: schemas.CampaignCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.create_campaign(db=db, campaign=campaign, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Campaign])
def read_user_campaigns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    campaigns = crud.get_campaigns_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return campaigns

@router.get("/{campaign_id}", response_model=schemas.Campaign)
def read_single_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign

# --- AdGroup Endpoints ---
@router.post("/{campaign_id}/adgroups", response_model=schemas.AdGroup, status_code=status.HTTP_201_CREATED)
def create_new_ad_group_for_campaign(
    campaign_id: int,
    ad_group: schemas.AdGroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # First, verify the campaign belongs to the current user
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    return crud.create_ad_group(db=db, ad_group=ad_group, campaign_id=campaign_id)

@router.get("/{campaign_id}/adgroups/{ad_group_id}", response_model=schemas.AdGroup)
def read_single_ad_group(
    campaign_id: int,
    ad_group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify campaign ownership
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")

    db_ad_group = crud.get_ad_group(db, ad_group_id=ad_group_id, campaign_id=campaign_id)
    if db_ad_group is None:
        raise HTTPException(status_code=404, detail="Ad Group not found")
    return db_ad_group


# --- Keyword Endpoints ---
@router.post("/{campaign_id}/adgroups/{ad_group_id}/keywords", response_model=schemas.Keyword, status_code=status.HTTP_201_CREATED)
def add_keyword_to_ad_group(
    campaign_id: int,
    ad_group_id: int,
    keyword: schemas.KeywordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify campaign and ad group ownership/existence
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")

    db_ad_group = crud.get_ad_group(db, ad_group_id=ad_group_id, campaign_id=campaign_id)
    if db_ad_group is None:
        raise HTTPException(status_code=404, detail="Ad Group not found in the specified campaign")

    return crud.create_keyword(db=db, keyword=keyword, ad_group_id=ad_group_id)

@router.put("/{campaign_id}/adgroups/{ad_group_id}/keywords/{keyword_id}/bid", response_model=schemas.Keyword)
def update_keyword_bid_route(
    campaign_id: int,
    ad_group_id: int,
    keyword_id: int,
    bid_update: schemas.KeywordCreate, # TODO: For bid update, ideally accept a simpler schema like {"bid": new_bid}
                                      # Currently, the frontend sends a KeywordCreate-like object.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify campaign and ad group ownership
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")

    db_ad_group = crud.get_ad_group(db, ad_group_id=ad_group_id, campaign_id=campaign_id)
    if db_ad_group is None:
        raise HTTPException(status_code=404, detail="Ad Group not found in the specified campaign")

    # The CRUD function get_keyword itself also checks if keyword_id belongs to ad_group_id
    updated_keyword = crud.update_keyword_bid(db=db, keyword_id=keyword_id, new_bid=bid_update.bid, ad_group_id=ad_group_id)
    if updated_keyword is None:
        raise HTTPException(status_code=404, detail="Keyword not found in the specified ad group")
    return updated_keyword

# TODO: Add endpoints for:
# - Updating campaign settings (PUT /api/campaigns/{id}/settings)
# - Getting ad groups within a campaign (GET /api/campaigns/{id}/adgroups) - (Covered by GET /{campaign_id} if Campaign schema nests AdGroups)
# - Getting keywords within an ad group (GET /api/campaigns/{id}/adgroups/{ad_group_id}/keywords) - (Covered by GET /{campaign_id}/adgroups/{ad_group_id} if AdGroup schema nests Keywords)
# - Updating AdGroup (e.g. default_bid)
# - Updating Keyword (e.g. status)

# --- ProductTarget Endpoints ---
@router.post("/{campaign_id}/adgroups/{ad_group_id}/product-targets", response_model=schemas.ProductTarget, status_code=status.HTTP_201_CREATED)
def add_product_target_to_ad_group(
    campaign_id: int,
    ad_group_id: int,
    product_target: schemas.ProductTargetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Required for initial auth check by router
):
    # Verify campaign and ad group ownership/existence
    # This logic is repeated; could be a dependency
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    # Ensure ad_group belongs to the campaign
    db_ad_group = db.query(models.AdGroup).filter(
        models.AdGroup.id == ad_group_id,
        models.AdGroup.campaign_id == campaign_id
    ).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")

    return crud.create_product_target(db=db, product_target=product_target, ad_group_id=ad_group_id)

@router.get("/{campaign_id}/adgroups/{ad_group_id}/product-targets", response_model=List[schemas.ProductTarget])
def list_product_targets_in_ad_group(
    campaign_id: int,
    ad_group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    db_ad_group = db.query(models.AdGroup).filter(
        models.AdGroup.id == ad_group_id,
        models.AdGroup.campaign_id == campaign_id
    ).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")

    return crud.get_product_targets_by_ad_group(db=db, ad_group_id=ad_group_id)

@router.put("/{campaign_id}/adgroups/{ad_group_id}/product-targets/{product_target_id}", response_model=schemas.ProductTarget)
def update_ad_group_product_target(
    campaign_id: int,
    ad_group_id: int,
    product_target_id: int,
    product_target_update: schemas.ProductTargetCreate, # Reusing Create schema for updates
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    # Ad group check is implicitly handled by crud.update_product_target if it uses get_product_target
    # which checks ad_group_id.
    updated_pt = crud.update_product_target(
        db=db,
        product_target_id=product_target_id,
        product_target_update=product_target_update,
        ad_group_id=ad_group_id # This ensures the target belongs to the ad_group
    )
    if updated_pt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product target not found or ad group mismatch")
    return updated_pt

@router.delete("/{campaign_id}/adgroups/{ad_group_id}/product-targets/{product_target_id}", response_model=schemas.Message)
def delete_ad_group_product_target(
    campaign_id: int,
    ad_group_id: int,
    product_target_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    deleted_pt = crud.delete_product_target(db=db, product_target_id=product_target_id, ad_group_id=ad_group_id)
    if deleted_pt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product target not found or ad group mismatch")
    return schemas.Message(detail=f"Product target ID {product_target_id} deleted successfully.")

# --- NegativeKeyword Endpoints ---

# Campaign-level Negative Keywords
@router.post("/{campaign_id}/negative-keywords", response_model=schemas.NegativeKeyword, status_code=status.HTTP_201_CREATED)
def add_campaign_negative_keyword(
    campaign_id: int,
    negative_keyword: schemas.NegativeKeywordCreate, # Schema should not require ad_group_id here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    if negative_keyword.ad_group_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ad_group_id should not be provided for campaign-level negative keywords.")

    return crud.create_negative_keyword(db=db, negative_keyword=negative_keyword, campaign_id=campaign_id, ad_group_id=None)

@router.get("/{campaign_id}/negative-keywords", response_model=List[schemas.NegativeKeyword])
def list_campaign_negative_keywords(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    return crud.get_negative_keywords_by_campaign(db=db, campaign_id=campaign_id)

# AdGroup-level Negative Keywords
@router.post("/{campaign_id}/adgroups/{ad_group_id}/negative-keywords", response_model=schemas.NegativeKeyword, status_code=status.HTTP_201_CREATED)
def add_ad_group_negative_keyword(
    campaign_id: int, # Used for auth check
    ad_group_id: int,
    negative_keyword: schemas.NegativeKeywordCreate, # Schema should not require campaign_id here
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    db_ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")

    if negative_keyword.campaign_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="campaign_id should not be provided for adgroup-level negative keywords.")

    return crud.create_negative_keyword(db=db, negative_keyword=negative_keyword, ad_group_id=ad_group_id, campaign_id=None)

@router.get("/{campaign_id}/adgroups/{ad_group_id}/negative-keywords", response_model=List[schemas.NegativeKeyword])
def list_ad_group_negative_keywords(
    campaign_id: int, # Used for auth check
    ad_group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")

    db_ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")

    return crud.get_negative_keywords_by_ad_group(db=db, ad_group_id=ad_group_id)

# Generic Negative Keyword Update (can update text, match_type, status) - ID is the source of truth for scope
@router.put("/negative-keywords/{negative_keyword_id}", response_model=schemas.NegativeKeyword)
def update_negative_keyword_generic(
    negative_keyword_id: int,
    negative_keyword_update: schemas.NegativeKeywordCreate, # Using Create for update, not ideal for scope.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Ensure the user owns the campaign/adgroup this negative keyword belongs to.
    # This requires fetching the negative keyword first, then its parent campaign/adgroup.
    db_neg_kw = crud.get_negative_keyword(db, negative_keyword_id)
    if not db_neg_kw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative keyword not found")

    parent_campaign_id_to_check = None
    if db_neg_kw.campaign_id:
        parent_campaign_id_to_check = db_neg_kw.campaign_id
    elif db_neg_kw.ad_group_id:
        ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == db_neg_kw.ad_group_id).first()
        if not ad_group: # Should not happen if DB is consistent
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent ad group not found for negative keyword")
        parent_campaign_id_to_check = ad_group.campaign_id

    if not parent_campaign_id_to_check:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Negative keyword scope indeterminate")

    # Check ownership of the parent campaign
    owner_campaign = crud.get_campaign(db, campaign_id=parent_campaign_id_to_check, user_id=current_user.id)
    if not owner_campaign:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not own the campaign associated with this negative keyword")

    # Scope (campaign_id, ad_group_id) should not be changed via this update.
    # The NegativeKeywordCreate schema having optional campaign_id/ad_group_id is problematic here if they are set.
    # We should ignore any campaign_id/ad_group_id passed in negative_keyword_update for this PUT.
    updated_neg_kw = crud.update_negative_keyword(db, negative_keyword_id, negative_keyword_update)
    if updated_neg_kw is None: # Should be caught by initial fetch, but good for safety
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative keyword not found during update")
    return updated_neg_kw

@router.delete("/negative-keywords/{negative_keyword_id}", response_model=schemas.Message)
def delete_negative_keyword_generic(
    negative_keyword_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Similar ownership check as in PUT
    db_neg_kw = crud.get_negative_keyword(db, negative_keyword_id)
    if not db_neg_kw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative keyword not found")

    parent_campaign_id_to_check = None
    if db_neg_kw.campaign_id:
        parent_campaign_id_to_check = db_neg_kw.campaign_id
    elif db_neg_kw.ad_group_id:
        ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == db_neg_kw.ad_group_id).first()
        if not ad_group:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent ad group not found")
        parent_campaign_id_to_check = ad_group.campaign_id

    if not parent_campaign_id_to_check:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Negative keyword scope indeterminate")

    owner_campaign = crud.get_campaign(db, campaign_id=parent_campaign_id_to_check, user_id=current_user.id)
    if not owner_campaign:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not own the campaign for this negative keyword")

    deleted_nk = crud.delete_negative_keyword(db, negative_keyword_id)
    if deleted_nk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative keyword not found during deletion")
    return schemas.Message(detail=f"Negative keyword ID {negative_keyword_id} deleted successfully.")

# --- NegativeProductTarget Endpoints ---

# Campaign-level Negative Product Targets
@router.post("/{campaign_id}/negative-product-targets", response_model=schemas.NegativeProductTarget, status_code=status.HTTP_201_CREATED)
def add_campaign_negative_product_target(
    campaign_id: int,
    negative_product_target: schemas.NegativeProductTargetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    if negative_product_target.ad_group_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ad_group_id should not be provided for campaign-level negative product targets.")
    return crud.create_negative_product_target(db=db, negative_product_target=negative_product_target, campaign_id=campaign_id, ad_group_id=None)

@router.get("/{campaign_id}/negative-product-targets", response_model=List[schemas.NegativeProductTarget])
def list_campaign_negative_product_targets(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    return crud.get_negative_product_targets_by_campaign(db=db, campaign_id=campaign_id)

# AdGroup-level Negative Product Targets
@router.post("/{campaign_id}/adgroups/{ad_group_id}/negative-product-targets", response_model=schemas.NegativeProductTarget, status_code=status.HTTP_201_CREATED)
def add_ad_group_negative_product_target(
    campaign_id: int,
    ad_group_id: int,
    negative_product_target: schemas.NegativeProductTargetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    db_ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")
    if negative_product_target.campaign_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="campaign_id should not be provided for adgroup-level negative product targets.")
    return crud.create_negative_product_target(db=db, negative_product_target=negative_product_target, ad_group_id=ad_group_id, campaign_id=None)

@router.get("/{campaign_id}/adgroups/{ad_group_id}/negative-product-targets", response_model=List[schemas.NegativeProductTarget])
def list_ad_group_negative_product_targets(
    campaign_id: int,
    ad_group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_campaign = crud.get_campaign(db, campaign_id=campaign_id, user_id=current_user.id)
    if db_campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found or not owned by user")
    db_ad_group = db.query(models.AdGroup).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()
    if db_ad_group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad Group not found in the specified campaign")
    return crud.get_negative_product_targets_by_ad_group(db=db, ad_group_id=ad_group_id)

# Generic Negative Product Target Update & Delete (similar to negative keywords)
@router.put("/negative-product-targets/{negative_product_target_id}", response_model=schemas.NegativeProductTarget)
def update_negative_product_target_generic(
    negative_product_target_id: int,
    negative_product_target_update: schemas.NegativeProductTargetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_neg_pt = crud.get_negative_product_target(db, negative_product_target_id)
    if not db_neg_pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative product target not found")

    parent_campaign_id_to_check = db_neg_pt.campaign_id or (db_neg_pt.ad_group.campaign_id if db_neg_pt.ad_group else None)
    if not parent_campaign_id_to_check:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Negative product target scope indeterminate")

    owner_campaign = crud.get_campaign(db, campaign_id=parent_campaign_id_to_check, user_id=current_user.id)
    if not owner_campaign:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not own the campaign for this negative product target")

    updated_neg_pt = crud.update_negative_product_target(db, negative_product_target_id, negative_product_target_update)
    if updated_neg_pt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative product target not found during update")
    return updated_neg_pt

@router.delete("/negative-product-targets/{negative_product_target_id}", response_model=schemas.Message)
def delete_negative_product_target_generic(
    negative_product_target_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_neg_pt = crud.get_negative_product_target(db, negative_product_target_id)
    if not db_neg_pt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative product target not found")

    parent_campaign_id_to_check = db_neg_pt.campaign_id or (db_neg_pt.ad_group.campaign_id if db_neg_pt.ad_group else None)
    if not parent_campaign_id_to_check:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Negative product target scope indeterminate")

    owner_campaign = crud.get_campaign(db, campaign_id=parent_campaign_id_to_check, user_id=current_user.id)
    if not owner_campaign:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User does not own the campaign for this negative product target")

    deleted_npt = crud.delete_negative_product_target(db, negative_product_target_id)
    if deleted_npt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negative product target not found for deletion")
    return schemas.Message(detail=f"Negative product target ID {negative_product_target_id} deleted successfully.")
