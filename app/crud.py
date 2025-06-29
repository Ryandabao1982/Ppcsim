from sqlalchemy.orm import Session, joinedload
from app import models, schemas, auth # auth for hashing password

# --- User CRUD operations ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Product CRUD operations ---
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_product_by_asin(db: Session, asin: str):
    return db.query(models.Product).filter(models.Product.asin == asin).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    update_data = product_update.model_dump(exclude_unset=True) # Get only fields that were provided
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.add(db_product) # or db.merge(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None # Or False

    # Check for relationships: if this product is part of any campaigns,
    # we might want to prevent deletion or handle it gracefully (e.g., disassociate).
    # For now, basic delete. SQLAlchemy's M2M relationship should handle the link table.
    # If there are direct FKs from other tables to Product that are restrictive, this might fail.
    # Current setup: CampaignProductLink is an association table. Deleting a product
    # should ideally lead to deletion of links in campaign_product_link_table.
    # The relationship on Campaign model for `advertised_products` might need `cascade="all, delete"`
    # on the association object if we were using an association object model.
    # With a simple table, SQLAlchemy usually handles this if `ondelete="CASCADE"` is on FKs in the assoc table,
    # or the links need to be manually removed if `ondelete` is not set or is RESTRICT.
    # For simplicity in MVP, we'll assume direct deletion is fine.
    # If issues arise, we'd need to manually clear `db_product.in_campaigns` or adjust FKs.

    db.delete(db_product)
    db.commit()
    return db_product # Return the deleted object (now detached) or True

# --- Campaign CRUD operations ---
def create_campaign(db: Session, campaign: schemas.CampaignCreate, user_id: int):
    ad_groups_data = campaign.ad_groups or []
    advertised_product_ids = campaign.advertised_product_ids or []

    # Exclude fields that are handled separately or are relationships
    negative_keywords_data = campaign.negative_keywords or []
    negative_product_targets_data = campaign.negative_product_targets or [] # Get neg product targets
    campaign_data = campaign.model_dump(exclude={'ad_groups', 'advertised_product_ids', 'negative_keywords', 'negative_product_targets'})

    db_campaign = models.Campaign(**campaign_data, user_id=user_id)

    # Fetch and associate products
    if advertised_product_ids:
        products_to_associate = db.query(models.Product).filter(models.Product.id.in_(advertised_product_ids)).all()
        # Basic check if all requested product IDs were found (optional)
        if len(products_to_associate) != len(set(advertised_product_ids)):
            # Handle error: some product IDs not found. For now, just associate found ones.
            # Or raise HTTPException - this might be better done in the router.
            pass
        db_campaign.advertised_products.extend(products_to_associate)

    db.add(db_campaign)
    # It's often better to commit once after all related objects are added to the session,
    # but for nested creates that depend on parent ID, intermediate commits are sometimes used.
    # Here, we can add campaign, then ad_groups, then commit.

    created_ad_groups = []
    if ad_groups_data:
        # Add campaign to session first so it can be flushed for ID if ad_groups need it immediately
        # However, SQLAlchemy handles this with relationships if objects are added to session before commit.
        for ad_group_create_schema in ad_groups_data:
            # Create AdGroup, keywords will be handled by create_ad_group
            db_ad_group = create_ad_group(db=db, ad_group=ad_group_create_schema, campaign_id=None) # Pass None for campaign_id initially
            db_campaign.ad_groups.append(db_ad_group) # Associate with campaign
            created_ad_groups.append(db_ad_group) # Keep track if needed

    # Handle campaign-level negative keywords
    # Note: NegativeKeywordCreate schema has optional campaign_id and ad_group_id.
    # Here, we are sure it's for this campaign.
    created_neg_keywords_campaign = []
    if negative_keywords_data:
        for neg_kw_create_schema in negative_keywords_data:
            # Ensure ad_group_id is None if it's a campaign-level negative from this list
            if neg_kw_create_schema.ad_group_id is not None:
                # This indicates a schema usage error or data issue if campaign-level neg_kws are expected here
                # For now, we'll assume the list here is purely for campaign-level
                # A robust solution might involve validation or specific schemas for campaign-level list
                pass # Or raise an error, or clear ad_group_id

            neg_kw_create_schema.campaign_id = None # Will be set by db_campaign relationship or explicitly
            neg_kw_create_schema.ad_group_id = None # Explicitly ensure this is None for campaign level

            # db_neg_kw = create_negative_keyword(db=db, negative_keyword=neg_kw_create_schema, campaign_id=db_campaign.id, ad_group_id=None)
            # Simpler: let SQLAlchemy handle campaign_id via relationship append
            temp_neg_kw_data = neg_kw_create_schema.model_dump(exclude={'campaign_id', 'ad_group_id'})
            db_neg_kw_obj = models.NegativeKeyword(**temp_neg_kw_data)
            db_campaign.negative_keywords.append(db_neg_kw_obj)
            # db.add(db_neg_kw_obj) # Adding through relationship should suffice if cascade is right
            created_neg_keywords_campaign.append(db_neg_kw_obj)

    # Handle campaign-level negative product targets
    created_neg_prod_targets_campaign = []
    if negative_product_targets_data:
        for neg_pt_create_schema in negative_product_targets_data:
            if neg_pt_create_schema.ad_group_id is not None: # Ensure it's for campaign
                pass
            neg_pt_create_schema.campaign_id = None # Will be set by relationship
            neg_pt_create_schema.ad_group_id = None
            temp_neg_pt_data = neg_pt_create_schema.model_dump(exclude={'campaign_id', 'ad_group_id'})
            db_neg_pt_obj = models.NegativeProductTarget(**temp_neg_pt_data)
            db_campaign.negative_product_targets.append(db_neg_pt_obj)
            created_neg_prod_targets_campaign.append(db_neg_pt_obj)

    db.commit()
    db.refresh(db_campaign)

    # Ensure nested objects are also refreshed if accessed immediately
    # for ag in db_campaign.ad_groups:
    #     db.refresh(ag)
    #     for kw in ag.keywords:
    #         db.refresh(kw)

    return db_campaign


def get_campaign(db: Session, campaign_id: int, user_id: int):
    return db.query(models.Campaign).options(
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.keywords),
        joinedload(models.Campaign.advertised_products)
    ).filter(models.Campaign.id == campaign_id, models.Campaign.user_id == user_id).first()

def get_campaigns_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Eager load advertised_products and ad_groups with their keywords for the list view
    return db.query(models.Campaign).options(
        joinedload(models.Campaign.advertised_products),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.keywords),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.product_targets),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.negative_keywords),
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.negative_product_targets), # Load adgroup negative_product_targets
        joinedload(models.Campaign.negative_keywords),
        joinedload(models.Campaign.negative_product_targets) # Load campaign-level negative_product_targets
    ).filter(models.Campaign.user_id == user_id).offset(skip).limit(limit).all()

# --- AdGroup CRUD operations ---
def create_ad_group(db: Session, ad_group: schemas.AdGroupCreate, campaign_id: int):
    keywords_data = ad_group.keywords or []
    product_targets_data = ad_group.product_targets or []
    negative_keywords_data = ad_group.negative_keywords or []
    negative_product_targets_data = ad_group.negative_product_targets or [] # Get neg product targets for ad group

    ad_group_data = ad_group.model_dump(exclude={'keywords', 'product_targets', 'negative_keywords', 'negative_product_targets'})

    db_ad_group = models.AdGroup(**ad_group_data, campaign_id=campaign_id)
    db.add(db_ad_group)
    # Commit ad_group first to get its ID if sub-creations need it explicitly,
    # but appending to relationships before parent commit can also work.
    # Let's try to append children then commit parent (AdGroup).
    # db.commit()

    created_keywords = []
    for keyword_create_schema in keywords_data:
        db_keyword = create_keyword(db=db, keyword=keyword_create_schema, ad_group_id=db_ad_group.id)
        created_keywords.append(db_keyword)

    db.refresh(db_ad_group)
    # db_ad_group.keywords = created_keywords
    # Handle product targets
    product_targets_data = ad_group.product_targets or []
    created_product_targets = []
    for pt_create_schema in product_targets_data:
        # db_pt = create_product_target(db=db, product_target=pt_create_schema, ad_group_id=db_ad_group.id)
        # Simpler: let SQLAlchemy handle ad_group_id via relationship append
        temp_pt_data = pt_create_schema.model_dump(exclude={'ad_group_id'}) # ad_group_id will be set by relationship
        db_pt_obj = models.ProductTarget(**temp_pt_data)
        db_ad_group.product_targets.append(db_pt_obj)
        created_product_targets.append(db_pt_obj)

    # Handle adgroup-level negative keywords
    created_neg_keywords_adgroup = []
    if negative_keywords_data:
        for neg_kw_create_schema in negative_keywords_data:
            if neg_kw_create_schema.campaign_id is not None:
                # This list should only contain adgroup-level negatives
                pass # Or raise error
            neg_kw_create_schema.campaign_id = None # Explicitly None
            neg_kw_create_schema.ad_group_id = None # Will be set by relationship
            temp_neg_kw_data = neg_kw_create_schema.model_dump(exclude={'campaign_id', 'ad_group_id'})
            db_neg_kw_obj = models.NegativeKeyword(**temp_neg_kw_data)
            db_ad_group.negative_keywords.append(db_neg_kw_obj)
            created_neg_keywords_adgroup.append(db_neg_kw_obj)

    # Handle adgroup-level negative product targets
    created_neg_prod_targets_adgroup = []
    if negative_product_targets_data:
        for neg_pt_create_schema in negative_product_targets_data:
            if neg_pt_create_schema.campaign_id is not None:
                pass # Or raise error
            neg_pt_create_schema.campaign_id = None
            neg_pt_create_schema.ad_group_id = None # Will be set by relationship
            temp_neg_pt_data = neg_pt_create_schema.model_dump(exclude={'campaign_id', 'ad_group_id'})
            db_neg_pt_obj = models.NegativeProductTarget(**temp_neg_pt_data)
            db_ad_group.negative_product_targets.append(db_neg_pt_obj)
            created_neg_prod_targets_adgroup.append(db_neg_pt_obj)

    db.commit() # Commit AdGroup and all its cascaded children
    db.refresh(db_ad_group)
    return db_ad_group

def get_ad_group(db: Session, ad_group_id: int, campaign_id: int): # Assuming campaign_id for ownership check
    return db.query(models.AdGroup).options(
        joinedload(models.AdGroup.keywords),
        joinedload(models.AdGroup.product_targets),
        joinedload(models.AdGroup.negative_keywords),
        joinedload(models.AdGroup.negative_product_targets) # Eager load adgroup negative_product_targets
    ).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()


# --- Keyword CRUD operations ---
def create_keyword(db: Session, keyword: schemas.KeywordCreate, ad_group_id: int):
    db_keyword = models.Keyword(**keyword.model_dump(), ad_group_id=ad_group_id)
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword

def get_keyword(db: Session, keyword_id: int, ad_group_id: int): # Assuming ad_group_id for ownership check
    return db.query(models.Keyword).filter(models.Keyword.id == keyword_id, models.Keyword.ad_group_id == ad_group_id).first()

def update_keyword_bid(db: Session, keyword_id: int, new_bid: schemas.Decimal, ad_group_id: int):
    db_keyword = get_keyword(db=db, keyword_id=keyword_id, ad_group_id=ad_group_id) # ad_group_id for authz
    if db_keyword:
        db_keyword.bid = new_bid
        db.commit()
        db.refresh(db_keyword)
    return db_keyword

# --- ProductTarget CRUD operations ---
def create_product_target(db: Session, product_target: schemas.ProductTargetCreate, ad_group_id: int):
    db_product_target = models.ProductTarget(**product_target.model_dump(), ad_group_id=ad_group_id)
    db.add(db_product_target)
    db.commit()
    db.refresh(db_product_target)
    return db_product_target

def get_product_target(db: Session, product_target_id: int, ad_group_id: int):
    # Ensure product target belongs to the specified ad_group for authorization context
    return db.query(models.ProductTarget).filter(
        models.ProductTarget.id == product_target_id,
        models.ProductTarget.ad_group_id == ad_group_id
    ).first()

def get_product_targets_by_ad_group(db: Session, ad_group_id: int):
    return db.query(models.ProductTarget).filter(models.ProductTarget.ad_group_id == ad_group_id).all()

def update_product_target(db: Session, product_target_id: int, product_target_update: schemas.ProductTargetCreate, ad_group_id: int):
    # Reusing ProductTargetCreate for update; a ProductTargetUpdate schema would be more precise
    db_product_target = get_product_target(db, product_target_id, ad_group_id)
    if not db_product_target:
        return None

    update_data = product_target_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product_target, key, value)

    db.add(db_product_target)
    db.commit()
    db.refresh(db_product_target)
    return db_product_target

def delete_product_target(db: Session, product_target_id: int, ad_group_id: int):
    db_product_target = get_product_target(db, product_target_id, ad_group_id)
    if not db_product_target:
        return None # Or False

    db.delete(db_product_target)
    db.commit()
    return db_product_target # Or True

# --- NegativeKeyword CRUD operations ---
def create_negative_keyword(db: Session, negative_keyword: schemas.NegativeKeywordCreate,
                            campaign_id: Optional[int] = None, ad_group_id: Optional[int] = None):
    if not (campaign_id or ad_group_id) or (campaign_id and ad_group_id):
        # This validation should ideally be in the API layer or Pydantic schema if possible
        raise ValueError("NegativeKeyword must be associated with exactly one of campaign_id or ad_group_id.")

    db_negative_keyword = models.NegativeKeyword(
        **negative_keyword.model_dump(exclude={'campaign_id', 'ad_group_id'}), # Exclude IDs that are passed directly
        campaign_id=campaign_id,
        ad_group_id=ad_group_id
    )
    db.add(db_negative_keyword)
    db.commit()
    db.refresh(db_negative_keyword)
    return db_negative_keyword

def get_negative_keyword(db: Session, negative_keyword_id: int):
    return db.query(models.NegativeKeyword).filter(models.NegativeKeyword.id == negative_keyword_id).first()

def get_negative_keywords_by_campaign(db: Session, campaign_id: int):
    return db.query(models.NegativeKeyword).filter(models.NegativeKeyword.campaign_id == campaign_id).all()

def get_negative_keywords_by_ad_group(db: Session, ad_group_id: int):
    return db.query(models.NegativeKeyword).filter(models.NegativeKeyword.ad_group_id == ad_group_id).all()

def update_negative_keyword(db: Session, negative_keyword_id: int,
                            negative_keyword_update: schemas.NegativeKeywordCreate):
                            # Reusing Create schema; an Update schema would be better.
    db_negative_keyword = get_negative_keyword(db, negative_keyword_id)
    if not db_negative_keyword:
        return None

    update_data = negative_keyword_update.model_dump(exclude_unset=True, exclude={'campaign_id', 'ad_group_id'})
    # Scope (campaign_id, ad_group_id) should not be changed during an update.
    # If scope change is needed, it's typically a delete and recreate.
    for key, value in update_data.items():
        setattr(db_negative_keyword, key, value)

    db.add(db_negative_keyword)
    db.commit()
    db.refresh(db_negative_keyword)
    return db_negative_keyword

def delete_negative_keyword(db: Session, negative_keyword_id: int):
    db_negative_keyword = get_negative_keyword(db, negative_keyword_id)
    if not db_negative_keyword:
        return None
    db.delete(db_negative_keyword)
    db.commit()
    return db_negative_keyword

# --- NegativeProductTarget CRUD operations ---
def create_negative_product_target(db: Session, negative_product_target: schemas.NegativeProductTargetCreate,
                                   campaign_id: Optional[int] = None, ad_group_id: Optional[int] = None):
    if not (campaign_id or ad_group_id) or (campaign_id and ad_group_id):
        raise ValueError("NegativeProductTarget must be associated with exactly one of campaign_id or ad_group_id.")

    db_negative_pt = models.NegativeProductTarget(
        **negative_product_target.model_dump(exclude={'campaign_id', 'ad_group_id'}),
        campaign_id=campaign_id,
        ad_group_id=ad_group_id
    )
    db.add(db_negative_pt)
    db.commit()
    db.refresh(db_negative_pt)
    return db_negative_pt

def get_negative_product_target(db: Session, negative_product_target_id: int):
    return db.query(models.NegativeProductTarget).filter(models.NegativeProductTarget.id == negative_product_target_id).first()

def get_negative_product_targets_by_campaign(db: Session, campaign_id: int):
    return db.query(models.NegativeProductTarget).filter(models.NegativeProductTarget.campaign_id == campaign_id).all()

def get_negative_product_targets_by_ad_group(db: Session, ad_group_id: int):
    return db.query(models.NegativeProductTarget).filter(models.NegativeProductTarget.ad_group_id == ad_group_id).all()

def update_negative_product_target(db: Session, negative_product_target_id: int,
                                   negative_product_target_update: schemas.NegativeProductTargetCreate):
    db_negative_pt = get_negative_product_target(db, negative_product_target_id)
    if not db_negative_pt:
        return None

    update_data = negative_product_target_update.model_dump(exclude_unset=True, exclude={'campaign_id', 'ad_group_id'})
    for key, value in update_data.items():
        setattr(db_negative_pt, key, value)

    db.add(db_negative_pt)
    db.commit()
    db.refresh(db_negative_pt)
    return db_negative_pt

def delete_negative_product_target(db: Session, negative_product_target_id: int):
    db_negative_pt = get_negative_product_target(db, negative_product_target_id)
    if not db_negative_pt:
        return None
    db.delete(db_negative_pt)
    db.commit()
    return db_negative_pt
