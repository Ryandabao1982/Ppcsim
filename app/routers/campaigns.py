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
