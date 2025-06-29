from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum, Date, Numeric, Table
from sqlalchemy.orm import relationship
from app.database import Base
import sqlalchemy as sa # Import sa
import datetime
import enum

# --- Enums ---
class AdTypeEnum(enum.Enum):
    SPONSORED_PRODUCTS = "sponsored_products"
    SPONSORED_BRANDS = "sponsored_brands"
    SPONSORED_DISPLAY = "sponsored_display"

class CampaignTargetingTypeEnum(enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"

class BiddingStrategyEnum(enum.Enum):
    DYNAMIC_DOWN_ONLY = "dynamic_bids_down_only"
    DYNAMIC_UP_DOWN = "dynamic_bids_up_and_down"
    FIXED_BIDS = "fixed_bids"

class MatchTypeEnum(enum.Enum):
    BROAD = "broad"
    PHRASE = "phrase"
    EXACT = "exact"

class KeywordStatusEnum(enum.Enum):
    ENABLED = "enabled"
    PAUSED = "paused"
    ARCHIVED = "archived"

class PlacementEnum(enum.Enum): # For AdPerformanceMetrics and Placement Reports
    TOP_OF_SEARCH = "top_of_search"
    PRODUCT_PAGE = "product_page"
    REST_OF_SEARCH = "rest_of_search"
    UNKNOWN = "unknown" # Default or for other types

# TargetTypeEnum removed as AdPerformanceMetric directly links to keyword_id for MVP.
# It can be re-added if polymorphic targeting is implemented.

# --- Models ---

# Association table for Many-to-Many relationship between Campaigns and Products
campaign_product_link_table = sa.Table('campaign_product_link', Base.metadata,
    sa.Column('campaign_id', sa.Integer, sa.ForeignKey('campaigns.id'), primary_key=True),
    sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    campaigns = relationship("Campaign", back_populates="owner")
    ad_performance_metrics = relationship("AdPerformanceMetric", back_populates="user")
    search_terms_performance = relationship("SearchTermPerformance", back_populates="user")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, unique=True, index=True, nullable=False)
    product_name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=True)
    sub_category = Column(String, index=True, nullable=True)
    avg_selling_price = Column(Numeric(10, 2), nullable=False)
    cost_of_goods_sold = Column(Numeric(10, 2), nullable=False)
    initial_cvr_baseline = Column(Float, nullable=False)

    # Many-to-Many relationship with Campaign
    in_campaigns = relationship(
        "Campaign",
        secondary=campaign_product_link_table,
        back_populates="advertised_products")


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    campaign_name = Column(String, index=True, nullable=False)
    ad_type = Column(SAEnum(AdTypeEnum), nullable=False, default=AdTypeEnum.SPONSORED_PRODUCTS)
    daily_budget = Column(Numeric(10, 2), nullable=False)
    start_date = Column(Date, default=datetime.date.today, nullable=False)
    end_date = Column(Date, nullable=True)
    bidding_strategy = Column(SAEnum(BiddingStrategyEnum), nullable=False, default=BiddingStrategyEnum.DYNAMIC_DOWN_ONLY)
    targeting_type = Column(SAEnum(CampaignTargetingTypeEnum), nullable=True)

    owner = relationship("User", back_populates="campaigns")
    ad_groups = relationship("AdGroup", back_populates="campaign", cascade="all, delete-orphan")
    ad_performance_metrics = relationship("AdPerformanceMetric", back_populates="campaign")
    search_terms_performance = relationship("SearchTermPerformance", back_populates="campaign")

    # Many-to-Many relationship with Product
    advertised_products = relationship(
        "Product",
        secondary=campaign_product_link_table,
        back_populates="in_campaigns")


class AdGroup(Base):
    __tablename__ = "ad_groups"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    ad_group_name = Column(String, index=True, nullable=False)
    default_bid = Column(Numeric(10, 2), nullable=True)

    campaign = relationship("Campaign", back_populates="ad_groups")
    keywords = relationship("Keyword", back_populates="ad_group", cascade="all, delete-orphan")
    ad_performance_metrics = relationship("AdPerformanceMetric", back_populates="ad_group")
    search_terms_performance = relationship("SearchTermPerformance", back_populates="ad_group")


class Keyword(Base): # Represents a targeted keyword
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    ad_group_id = Column(Integer, ForeignKey("ad_groups.id"), nullable=False)
    keyword_text = Column(String, index=True, nullable=False)
    match_type = Column(SAEnum(MatchTypeEnum), nullable=False)
    bid = Column(Numeric(10, 2), nullable=False)
    status = Column(SAEnum(KeywordStatusEnum), default=KeywordStatusEnum.ENABLED, nullable=False)

    ad_group = relationship("AdGroup", back_populates="keywords")
    ad_performance_metrics = relationship("AdPerformanceMetric", back_populates="keyword_target")


class AdPerformanceMetric(Base):
    __tablename__ = "ad_performance_metrics"
    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(Date, nullable=False, index=True, default=datetime.date.today)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    ad_group_id = Column(Integer, ForeignKey("ad_groups.id"), nullable=True, index=True) # Nullable if metric is campaign-level

    # Targeting context - simplified for MVP: direct link to Keyword
    # For full design, target_type and target_id (polymorphic) would be more flexible
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=True, index=True) # For keyword-level performance
    # product_target_id for ASIN/Category targets later

    placement = Column(SAEnum(PlacementEnum), nullable=True, default=PlacementEnum.UNKNOWN) # Can be null if not applicable

    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    orders = Column(Integer, default=0)
    sales = Column(Numeric(10, 2), default=0.0)

    # Calculated fields (can also be calculated on-the-fly or stored)
    acos = Column(Float, default=0.0) # (spend / sales) * 100
    roas = Column(Float, default=0.0) # sales / spend
    cpc = Column(Float, default=0.0)  # spend / clicks
    ctr = Column(Float, default=0.0)  # (clicks / impressions) * 100
    cvr = Column(Float, default=0.0)  # (orders / clicks) * 100

    user = relationship("User", back_populates="ad_performance_metrics")
    campaign = relationship("Campaign", back_populates="ad_performance_metrics")
    ad_group = relationship("AdGroup", back_populates="ad_performance_metrics")
    keyword_target = relationship("Keyword", back_populates="ad_performance_metrics")


class SearchTermPerformance(Base): # Stores performance of specific search terms discovered
    __tablename__ = "search_terms_performance"
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, index=True, default=datetime.date.today)
    search_term_text = Column(String, index=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    ad_group_id = Column(Integer, ForeignKey("ad_groups.id"), nullable=False, index=True)

    # Link to the keyword that this search term matched to (if applicable, e.g., for manual campaigns)
    # For auto campaigns, this might be null or point to an "auto-target" concept.
    matched_keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=True, index=True)
    # Or, if it's an auto-target match:
    # matched_product_target_id = Column(Integer, ForeignKey("product_targets.id"), nullable=True, index=True)


    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Numeric(10, 2), default=0.0)
    orders = Column(Integer, default=0)
    sales = Column(Numeric(10, 2), default=0.0)

    acos = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)
    cvr = Column(Float, default=0.0)

    user = relationship("User", back_populates="search_terms_performance")
    campaign = relationship("Campaign", back_populates="search_terms_performance")
    ad_group = relationship("AdGroup", back_populates="search_terms_performance")
    matched_keyword_target = relationship("Keyword", back_populates="matched_search_terms")

# TODO: ProductTarget model for ASIN/Category targeting
# TODO: NegativeKeyword and NegativeProductTarget models
# TODO: CampaignProductLink association table implementation for M2M between Campaigns and Products (if needed for advertised products)
