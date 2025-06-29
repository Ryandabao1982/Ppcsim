from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from decimal import Decimal
import datetime

# Import enums from models to use in schemas
from app.models import AdTypeEnum, CampaignTargetingTypeEnum, BiddingStrategyEnum, MatchTypeEnum, KeywordStatusEnum

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

class AdGroup(AdGroupBase):
    id: int
    campaign_id: int
    keywords: List[Keyword] = []
    class Config:
        from_attributes = True

# Campaign Schemas
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
