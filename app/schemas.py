from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
import datetime

# Import enums from models to use in schemas
from app.models import (
    AdTypeEnum, CampaignTargetingTypeEnum, BiddingStrategyEnum,
    MatchTypeEnum, KeywordStatusEnum,
    ProductTargetingTypeEnum, ProductTargetStatusEnum,
    NegativeMatchTypeEnum, NegativeProductTargetStatusEnum # Added Enums for Negative Product Targets
)

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# Generic Message Schema
class Message(BaseModel):
    detail: str

# Product Schemas
class ProductBase(BaseModel):
    asin: str
    product_name: str
    category: Optional[str] = None
    avg_selling_price: Decimal = Field(..., max_digits=10, decimal_places=2)
    cost_of_goods_sold: Decimal = Field(..., max_digits=10, decimal_places=2)
    initial_cvr_baseline: float

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True

class ProductUpdate(BaseModel): # All fields optional for PATCH-like behavior
    asin: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    avg_selling_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    cost_of_goods_sold: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    initial_cvr_baseline: Optional[float] = None

# Keyword Schemas
class KeywordBase(BaseModel):
    keyword_text: str
    match_type: MatchTypeEnum
    bid: Decimal = Field(..., max_digits=10, decimal_places=2)
    status: Optional[KeywordStatusEnum] = KeywordStatusEnum.ENABLED

class KeywordCreate(KeywordBase):
    pass

class Keyword(KeywordBase):
    id: int
    ad_group_id: int
    class Config:
        from_attributes = True

# AdGroup Schemas
class AdGroupBase(BaseModel):
    ad_group_name: str
    default_bid: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)

class AdGroupCreate(AdGroupBase):
    keywords: Optional[List[KeywordCreate]] = [] # Allow creating keywords when creating adgroup
    product_targets: Optional[List['ProductTargetCreate']] = [] # Added for product targets

class AdGroup(AdGroupBase):
    id: int
    campaign_id: int
    keywords: List[Keyword] = []
    product_targets: List['ProductTarget'] = [] # Added for product targets
    class Config:
        from_attributes = True

# ProductTarget Schemas
class ProductTargetBase(BaseModel):
    targeting_type: ProductTargetingTypeEnum
    target_value: str # ASIN or Category ID/Name
    bid: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2)
    status: Optional[ProductTargetStatusEnum] = ProductTargetStatusEnum.ENABLED

class ProductTargetCreate(ProductTargetBase):
    pass

class ProductTarget(ProductTargetBase):
    id: int
    ad_group_id: int
    class Config:
        from_attributes = True

# Forward references update for AdGroupCreate and AdGroup
# AdGroupCreate.model_rebuild()
# AdGroup.model_rebuild()

# NegativeKeyword Schemas
class NegativeKeywordBase(BaseModel):
    keyword_text: str
    match_type: NegativeMatchTypeEnum
    status: Optional[KeywordStatusEnum] = KeywordStatusEnum.ENABLED # Reusing KeywordStatusEnum

class NegativeKeywordCreate(NegativeKeywordBase):
    # Must be linked to EITHER a campaign OR an ad group, handled by API logic/validation
    campaign_id: Optional[int] = None
    ad_group_id: Optional[int] = None

    # Pydantic validator to ensure one of campaign_id or ad_group_id is provided
    # This can also be handled at the API endpoint level more explicitly.
    # from pydantic import root_validator
    # @root_validator(pre=False, skip_on_failure=True) # Using pre=False to work on validated fields
    # def check_scope_present(cls, values):
    #     if values.get('campaign_id') is None and values.get('ad_group_id') is None:
    #         raise ValueError('Either campaign_id or ad_group_id must be provided for NegativeKeyword')
    #     if values.get('campaign_id') is not None and values.get('ad_group_id') is not None:
    #         raise ValueError('NegativeKeyword cannot be linked to both campaign_id and ad_group_id')
    #     return values


class NegativeKeyword(NegativeKeywordBase):
    id: int
    campaign_id: Optional[int] = None # Reflects DB model
    ad_group_id: Optional[int] = None # Reflects DB model
    class Config:
        from_attributes = True


# Update Campaign and AdGroup schemas to include negative keywords
class CampaignCreate(CampaignBase):
    ad_groups: Optional[List[AdGroupCreate]] = []
    advertised_product_ids: Optional[List[int]] = []
    negative_keywords: Optional[List[NegativeKeywordCreate]] = [] # Campaign-level negatives

class Campaign(CampaignBase):
    id: int
    user_id: int
    ad_groups: List[AdGroup] = []
    advertised_products: List[Product] = []
    negative_keywords: List[NegativeKeyword] = [] # Campaign-level negatives
    class Config:
        from_attributes = True

class AdGroupCreate(AdGroupBase):
    keywords: Optional[List[KeywordCreate]] = []
    product_targets: Optional[List[ProductTargetCreate]] = []
    negative_keywords: Optional[List[NegativeKeywordCreate]] = [] # AdGroup-level negatives

class AdGroup(AdGroupBase):
    id: int
    campaign_id: int
    keywords: List[Keyword] = []
    product_targets: List[ProductTarget] = []
    negative_keywords: List[NegativeKeyword] = [] # AdGroup-level negatives
    class Config:
        from_attributes = True

# Campaign Schemas
# Forward references might need to be resolved for Pydantic v1 or complex v2 cases
# AdGroupCreate.model_rebuild() # If AdGroupCreate refers to something defined later (it does: NegativeKeywordCreate)
# AdGroup.model_rebuild()       # If AdGroup refers to something defined later (it does: NegativeKeyword)
# CampaignCreate.model_rebuild()# If CampaignCreate refers to something defined later (it does: NegativeKeywordCreate)
# Campaign.model_rebuild()      # If Campaign refers to something defined later (it does: NegativeKeyword)
# This is usually more critical if types are imported across modules with circular deps.
# For a single file, Pydantic often resolves it, but explicit calls don't hurt if issues arise.
# Pydantic V2 generally handles forward references more robustly.
# For now, I'll rely on Pydantic's default behavior. If parsing fails, these can be added.

# NegativeProductTarget Schemas
class NegativeProductTargetBase(BaseModel):
    target_asin: str
    status: Optional[NegativeProductTargetStatusEnum] = NegativeProductTargetStatusEnum.ENABLED # Reusing for consistency

class NegativeProductTargetCreate(NegativeProductTargetBase):
    campaign_id: Optional[int] = None
    ad_group_id: Optional[int] = None
    # Similar to NegativeKeywordCreate, validation for one scope ID needed at API/CRUD level

class NegativeProductTarget(NegativeProductTargetBase):
    id: int
    campaign_id: Optional[int] = None
    ad_group_id: Optional[int] = None
    class Config:
        from_attributes = True

# Update Campaign and AdGroup schemas for Negative Product Targets
class CampaignCreate(CampaignBase):
    ad_groups: Optional[List[AdGroupCreate]] = []
    advertised_product_ids: Optional[List[int]] = []
    negative_keywords: Optional[List[NegativeKeywordCreate]] = []
    negative_product_targets: Optional[List[NegativeProductTargetCreate]] = [] # Campaign-level

class Campaign(CampaignBase):
    id: int
    user_id: int
    ad_groups: List[AdGroup] = []
    advertised_products: List[Product] = []
    negative_keywords: List[NegativeKeyword] = []
    negative_product_targets: List[NegativeProductTarget] = [] # Campaign-level
    class Config:
        from_attributes = True

class AdGroupCreate(AdGroupBase):
    keywords: Optional[List[KeywordCreate]] = []
    product_targets: Optional[List[ProductTargetCreate]] = []
    negative_keywords: Optional[List[NegativeKeywordCreate]] = []
    negative_product_targets: Optional[List[NegativeProductTargetCreate]] = [] # AdGroup-level

class AdGroup(AdGroupBase):
    id: int
    campaign_id: int
    keywords: List[Keyword] = []
    product_targets: List[ProductTarget] = []
    negative_keywords: List[NegativeKeyword] = []
    negative_product_targets: List[NegativeProductTarget] = [] # AdGroup-level
    class Config:
        from_attributes = True


class CampaignBase(BaseModel):
    campaign_name: str
    ad_type: Optional[AdTypeEnum] = AdTypeEnum.SPONSORED_PRODUCTS
    daily_budget: Decimal = Field(..., max_digits=10, decimal_places=2)
    start_date: Optional[datetime.date] = datetime.date.today()
    end_date: Optional[datetime.date] = None
    bidding_strategy: Optional[BiddingStrategyEnum] = BiddingStrategyEnum.DYNAMIC_DOWN_ONLY
    targeting_type: Optional[CampaignTargetingTypeEnum] = None # e.g. AUTO/MANUAL for SP

class CampaignCreate(CampaignBase):
    ad_groups: Optional[List[AdGroupCreate]] = [] # Allow creating adgroups when creating campaign
    advertised_product_ids: Optional[List[int]] = [] # List of Product IDs to associate

class Campaign(CampaignBase):
    id: int
    user_id: int
    ad_groups: List[AdGroup] = []
    advertised_products: List[Product] = [] # Will hold Product objects
    class Config:
        from_attributes = True

# Dashboard Schemas
class DashboardMetrics(BaseModel):
    total_sales: Decimal = Field(default=0.0, max_digits=12, decimal_places=2)
    total_spend: Decimal = Field(default=0.0, max_digits=12, decimal_places=2)
    acos: float = 0.0
    roas: float = 0.0
    impressions: int = 0
    clicks: int = 0
    orders: int = 0
    # Optional: Add fields for trends or period
    period_description: Optional[str] = "Overall" # e.g., "Last 7 days"

# Search Term Report Schemas
class SearchTermReportItem(BaseModel):
    report_date: datetime.date # Or consider making this optional if aggregating over time
    search_term_text: str
    campaign_name: Optional[str] = None # Denormalized for easier display
    ad_group_name: Optional[str] = None # Denormalized for easier display
    matched_keyword_text: Optional[str] = None # Denormalized

    impressions: int
    clicks: int
    spend: Decimal = Field(..., max_digits=10, decimal_places=2)
    orders: int
    sales: Decimal = Field(..., max_digits=10, decimal_places=2)
    acos: float
    roas: float
    cpc: float
    ctr: float
    cvr: float

    # IDs for drill-down or further linking if needed by frontend
    campaign_id: int
    ad_group_id: int
    matched_keyword_id: Optional[int] = None


    class Config:
        from_attributes = True
