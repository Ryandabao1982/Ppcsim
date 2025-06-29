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

# --- Campaign CRUD operations ---
def create_campaign(db: Session, campaign: schemas.CampaignCreate, user_id: int):
    ad_groups_data = campaign.ad_groups or []
    advertised_product_ids = campaign.advertised_product_ids or []

    # Exclude fields that are handled separately or are relationships
    campaign_data = campaign.model_dump(exclude={'ad_groups', 'advertised_product_ids'})

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
        joinedload(models.Campaign.ad_groups).joinedload(models.AdGroup.keywords)
    ).filter(models.Campaign.user_id == user_id).offset(skip).limit(limit).all()

# --- AdGroup CRUD operations ---
def create_ad_group(db: Session, ad_group: schemas.AdGroupCreate, campaign_id: int):
    keywords_data = ad_group.keywords or []
    ad_group_data = ad_group.model_dump(exclude={'keywords'})

    db_ad_group = models.AdGroup(**ad_group_data, campaign_id=campaign_id)
    db.add(db_ad_group)
    db.commit() # Commit ad_group to get its ID

    created_keywords = []
    for keyword_create_schema in keywords_data:
        db_keyword = create_keyword(db=db, keyword=keyword_create_schema, ad_group_id=db_ad_group.id)
        created_keywords.append(db_keyword)

    db.refresh(db_ad_group)
    # db_ad_group.keywords = created_keywords # Similar to campaigns, may not be needed
    return db_ad_group

def get_ad_group(db: Session, ad_group_id: int, campaign_id: int): # Assuming campaign_id for ownership check
    return db.query(models.AdGroup).options(joinedload(models.AdGroup.keywords)).filter(models.AdGroup.id == ad_group_id, models.AdGroup.campaign_id == campaign_id).first()

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
