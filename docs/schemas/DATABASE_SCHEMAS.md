# Database Schemas
## Amazon PPC Simulator

**Version:** 1.0  
**Database:** PostgreSQL 15.x  
**ORM:** Prisma

---

## 1. Schema Overview

The database schema is designed to support:
- User authentication and authorization
- Campaign and keyword management
- Performance metrics tracking
- Tutorial and learning progress
- System configuration

### 1.1 Schema Diagram

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼──────────┐        ┌────────────────┐
│   campaigns     │────────│  ad_groups     │
└──────┬──────────┘  1:N   └────────┬───────┘
       │                            │
       │ 1:N                        │ 1:N
       │                            │
┌──────▼──────────┐        ┌────────▼───────┐
│    keywords     │        │   products     │
└──────┬──────────┘        └────────────────┘
       │
       │ 1:N
       │
┌──────▼──────────────────┐
│ performance_metrics     │
└─────────────────────────┘

┌─────────────┐
│    users    │
└──────┬──────┘
       │ 1:N
┌──────▼──────────────┐
│ tutorial_progress   │
└─────────────────────┘
```

---

## 2. Core Tables

### 2.1 Users Table

Stores user account information and authentication credentials.

```sql
CREATE TABLE users (
    id                  SERIAL PRIMARY KEY,
    email               VARCHAR(255) UNIQUE NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    role                VARCHAR(50) DEFAULT 'student' NOT NULL,
    email_verified      BOOLEAN DEFAULT false,
    email_verified_at   TIMESTAMP,
    status              VARCHAR(50) DEFAULT 'active' NOT NULL,
    last_login_at       TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
```

**Fields:**
- `id`: Unique identifier (auto-increment)
- `email`: User's email address (unique, used for login)
- `password_hash`: Bcrypt hashed password (minimum 10 rounds)
- `first_name`: User's first name
- `last_name`: User's last name
- `role`: User role (`student`, `instructor`, `admin`)
- `email_verified`: Whether email has been verified
- `email_verified_at`: Timestamp of email verification
- `status`: Account status (`active`, `suspended`, `deleted`)
- `last_login_at`: Timestamp of last successful login
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- Email must be unique and valid format
- Password hash must be present
- Role must be one of: `student`, `instructor`, `admin`
- Status must be one of: `active`, `suspended`, `deleted`

---

### 2.2 Campaigns Table

Stores Amazon PPC campaign configurations.

```sql
CREATE TABLE campaigns (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name                    VARCHAR(255) NOT NULL,
    campaign_type           VARCHAR(50) NOT NULL DEFAULT 'sponsored_products',
    targeting_type          VARCHAR(50) NOT NULL DEFAULT 'manual',
    daily_budget            DECIMAL(10, 2) NOT NULL,
    status                  VARCHAR(50) DEFAULT 'active' NOT NULL,
    bidding_strategy        VARCHAR(50) DEFAULT 'manual' NOT NULL,
    start_date              DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date                DATE,
    total_budget            DECIMAL(10, 2),
    
    -- Performance metrics cache (updated periodically)
    total_impressions       BIGINT DEFAULT 0,
    total_clicks            INTEGER DEFAULT 0,
    total_conversions       INTEGER DEFAULT 0,
    total_spend             DECIMAL(10, 2) DEFAULT 0.00,
    total_sales             DECIMAL(10, 2) DEFAULT 0.00,
    
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_type ON campaigns(campaign_type);
CREATE INDEX idx_campaigns_created_at ON campaigns(created_at);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: Reference to user who owns the campaign
- `name`: Campaign name (user-defined)
- `campaign_type`: Type of campaign (`sponsored_products`, `sponsored_brands`, `sponsored_display`)
- `targeting_type`: Targeting method (`manual`, `automatic`)
- `daily_budget`: Maximum spend per day (in USD)
- `status`: Campaign status (`active`, `paused`, `archived`)
- `bidding_strategy`: Bidding approach (`manual`, `dynamic_down`, `dynamic_up_down`)
- `start_date`: Campaign start date
- `end_date`: Campaign end date (optional)
- `total_budget`: Lifetime budget limit (optional)
- `total_*`: Cached aggregated performance metrics
- `created_at`: Campaign creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- `daily_budget` must be >= 1.00
- `campaign_type` must be one of: `sponsored_products`, `sponsored_brands`, `sponsored_display`
- `targeting_type` must be one of: `manual`, `automatic`
- `status` must be one of: `active`, `paused`, `archived`
- `bidding_strategy` must be one of: `manual`, `dynamic_down`, `dynamic_up_down`

---

### 2.3 Ad Groups Table

Stores ad group configurations within campaigns (for organization).

```sql
CREATE TABLE ad_groups (
    id                  SERIAL PRIMARY KEY,
    campaign_id         INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    default_bid         DECIMAL(10, 2) NOT NULL,
    status              VARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ad_groups_campaign_id ON ad_groups(campaign_id);
CREATE INDEX idx_ad_groups_status ON ad_groups(status);
```

**Fields:**
- `id`: Unique identifier
- `campaign_id`: Reference to parent campaign
- `name`: Ad group name
- `default_bid`: Default bid for keywords in this ad group
- `status`: Ad group status (`active`, `paused`)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

### 2.4 Keywords Table

Stores keyword targeting configurations.

```sql
CREATE TABLE keywords (
    id                  SERIAL PRIMARY KEY,
    campaign_id         INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    ad_group_id         INTEGER REFERENCES ad_groups(id) ON DELETE CASCADE,
    keyword_text        VARCHAR(255) NOT NULL,
    match_type          VARCHAR(50) NOT NULL,
    bid                 DECIMAL(10, 2) NOT NULL,
    status              VARCHAR(50) DEFAULT 'active' NOT NULL,
    
    -- Simulation parameters
    quality_score       INTEGER DEFAULT 5 CHECK (quality_score BETWEEN 1 AND 10),
    base_ctr            DECIMAL(5, 4) DEFAULT 0.0200,  -- 2%
    base_cvr            DECIMAL(5, 4) DEFAULT 0.1000,  -- 10%
    
    -- Performance metrics cache
    total_impressions   BIGINT DEFAULT 0,
    total_clicks        INTEGER DEFAULT 0,
    total_conversions   INTEGER DEFAULT 0,
    total_spend         DECIMAL(10, 2) DEFAULT 0.00,
    total_sales         DECIMAL(10, 2) DEFAULT 0.00,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keywords_campaign_id ON keywords(campaign_id);
CREATE INDEX idx_keywords_ad_group_id ON keywords(ad_group_id);
CREATE INDEX idx_keywords_status ON keywords(status);
CREATE INDEX idx_keywords_match_type ON keywords(match_type);
CREATE UNIQUE INDEX idx_keywords_unique ON keywords(campaign_id, keyword_text, match_type);
```

**Fields:**
- `id`: Unique identifier
- `campaign_id`: Reference to parent campaign
- `ad_group_id`: Reference to ad group (optional)
- `keyword_text`: The actual keyword or phrase
- `match_type`: Keyword match type (`broad`, `phrase`, `exact`)
- `bid`: Bid amount for this keyword (in USD)
- `status`: Keyword status (`active`, `paused`)
- `quality_score`: Simulated quality score (1-10)
- `base_ctr`: Base click-through rate for simulation
- `base_cvr`: Base conversion rate for simulation
- `total_*`: Cached aggregated performance metrics
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

**Constraints:**
- `bid` must be >= 0.20
- `match_type` must be one of: `broad`, `phrase`, `exact`
- `status` must be one of: `active`, `paused`
- `quality_score` must be between 1 and 10
- Combination of `campaign_id`, `keyword_text`, and `match_type` must be unique

---

### 2.5 Negative Keywords Table

Stores negative keywords to exclude from targeting.

```sql
CREATE TABLE negative_keywords (
    id                  SERIAL PRIMARY KEY,
    campaign_id         INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
    ad_group_id         INTEGER REFERENCES ad_groups(id) ON DELETE CASCADE,
    keyword_text        VARCHAR(255) NOT NULL,
    match_type          VARCHAR(50) NOT NULL DEFAULT 'phrase',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_negative_keywords_campaign_id ON negative_keywords(campaign_id);
CREATE INDEX idx_negative_keywords_ad_group_id ON negative_keywords(ad_group_id);
```

**Constraints:**
- Either `campaign_id` or `ad_group_id` must be set (not both null)
- `match_type` must be one of: `phrase`, `exact`

---

### 2.6 Products Table

Stores product information for campaigns.

```sql
CREATE TABLE products (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asin                VARCHAR(10) UNIQUE NOT NULL,
    title               VARCHAR(500) NOT NULL,
    price               DECIMAL(10, 2) NOT NULL,
    category            VARCHAR(255),
    image_url           TEXT,
    
    -- Simulation parameters
    quality_score       INTEGER DEFAULT 7 CHECK (quality_score BETWEEN 1 AND 10),
    base_cvr            DECIMAL(5, 4) DEFAULT 0.1000,  -- 10%
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_asin ON products(asin);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: Reference to user who owns the product
- `asin`: Amazon Standard Identification Number (simulated)
- `title`: Product title
- `price`: Product price (in USD)
- `category`: Product category
- `image_url`: URL to product image
- `quality_score`: Product quality score for simulation (1-10)
- `base_cvr`: Base conversion rate for this product
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

---

## 3. Performance & Analytics Tables

### 3.1 Performance Metrics Table

Stores hourly aggregated performance data for campaigns and keywords.

```sql
CREATE TABLE performance_metrics (
    id                  BIGSERIAL PRIMARY KEY,
    campaign_id         INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    keyword_id          INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    
    -- Time dimension
    date                DATE NOT NULL,
    hour                INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
    
    -- Performance metrics
    impressions         INTEGER DEFAULT 0,
    clicks              INTEGER DEFAULT 0,
    conversions         INTEGER DEFAULT 0,
    spend               DECIMAL(10, 2) DEFAULT 0.00,
    sales               DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Calculated metrics (can be derived but stored for performance)
    ctr                 DECIMAL(6, 4),  -- clicks / impressions
    cvr                 DECIMAL(6, 4),  -- conversions / clicks
    cpc                 DECIMAL(10, 2), -- spend / clicks
    acos                DECIMAL(6, 4),  -- spend / sales
    roas                DECIMAL(10, 2), -- sales / spend
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_perf_campaign_id ON performance_metrics(campaign_id);
CREATE INDEX idx_perf_keyword_id ON performance_metrics(keyword_id);
CREATE INDEX idx_perf_date ON performance_metrics(date);
CREATE INDEX idx_perf_campaign_date ON performance_metrics(campaign_id, date);
CREATE INDEX idx_perf_keyword_date ON performance_metrics(keyword_id, date);
CREATE UNIQUE INDEX idx_perf_unique ON performance_metrics(campaign_id, COALESCE(keyword_id, 0), date, hour);
```

**Fields:**
- `id`: Unique identifier
- `campaign_id`: Reference to campaign
- `keyword_id`: Reference to keyword (null for campaign-level metrics)
- `date`: Date of metrics
- `hour`: Hour of day (0-23)
- `impressions`: Number of ad impressions
- `clicks`: Number of ad clicks
- `conversions`: Number of sales conversions
- `spend`: Total advertising spend (in USD)
- `sales`: Total sales revenue (in USD)
- `ctr`: Click-through rate (calculated)
- `cvr`: Conversion rate (calculated)
- `cpc`: Cost per click (calculated)
- `acos`: Advertising Cost of Sale (calculated)
- `roas`: Return on Ad Spend (calculated)
- `created_at`: Record creation timestamp

**Partition Strategy:**
Consider partitioning this table by date for better performance with large datasets.

---

### 3.2 Search Terms Table

Stores customer search terms that triggered ads.

```sql
CREATE TABLE search_terms (
    id                  BIGSERIAL PRIMARY KEY,
    keyword_id          INTEGER NOT NULL REFERENCES keywords(id) ON DELETE CASCADE,
    search_term         VARCHAR(255) NOT NULL,
    
    -- Aggregated metrics (updated periodically)
    impressions         INTEGER DEFAULT 0,
    clicks              INTEGER DEFAULT 0,
    conversions         INTEGER DEFAULT 0,
    spend               DECIMAL(10, 2) DEFAULT 0.00,
    sales               DECIMAL(10, 2) DEFAULT 0.00,
    
    first_seen_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_search_terms_keyword_id ON search_terms(keyword_id);
CREATE INDEX idx_search_terms_search_term ON search_terms(search_term);
CREATE UNIQUE INDEX idx_search_terms_unique ON search_terms(keyword_id, search_term);
```

---

### 3.3 Daily Summary Table

Pre-aggregated daily metrics for faster reporting.

```sql
CREATE TABLE daily_summary (
    id                  SERIAL PRIMARY KEY,
    campaign_id         INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    keyword_id          INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    date                DATE NOT NULL,
    
    -- Aggregated metrics
    impressions         INTEGER DEFAULT 0,
    clicks              INTEGER DEFAULT 0,
    conversions         INTEGER DEFAULT 0,
    spend               DECIMAL(10, 2) DEFAULT 0.00,
    sales               DECIMAL(10, 2) DEFAULT 0.00,
    
    -- Calculated metrics
    ctr                 DECIMAL(6, 4),
    cvr                 DECIMAL(6, 4),
    cpc                 DECIMAL(10, 2),
    acos                DECIMAL(6, 4),
    roas                DECIMAL(10, 2),
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_daily_summary_unique ON daily_summary(campaign_id, COALESCE(keyword_id, 0), date);
CREATE INDEX idx_daily_summary_date ON daily_summary(date);
```

---

## 4. Learning & Progress Tables

### 4.1 Tutorial Progress Table

Tracks user progress through tutorial modules.

```sql
CREATE TABLE tutorial_progress (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tutorial_id         VARCHAR(100) NOT NULL,
    step_id             VARCHAR(100) NOT NULL,
    completed           BOOLEAN DEFAULT false,
    completed_at        TIMESTAMP,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tutorial_progress_user_id ON tutorial_progress(user_id);
CREATE UNIQUE INDEX idx_tutorial_progress_unique ON tutorial_progress(user_id, tutorial_id, step_id);
```

**Fields:**
- `id`: Unique identifier
- `user_id`: Reference to user
- `tutorial_id`: Tutorial module identifier
- `step_id`: Tutorial step identifier
- `completed`: Whether step is completed
- `completed_at`: Completion timestamp
- `created_at`: Record creation
- `updated_at`: Last update

---

### 4.2 Achievements Table

Stores user achievements and badges.

```sql
CREATE TABLE achievements (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_type    VARCHAR(100) NOT NULL,
    achievement_data    JSONB,
    earned_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_achievements_user_id ON achievements(user_id);
CREATE INDEX idx_achievements_type ON achievements(achievement_type);
```

---

### 4.3 User Settings Table

Stores user preferences and settings.

```sql
CREATE TABLE user_settings (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    timezone            VARCHAR(50) DEFAULT 'UTC',
    currency            VARCHAR(3) DEFAULT 'USD',
    notifications_email BOOLEAN DEFAULT true,
    theme               VARCHAR(20) DEFAULT 'light',
    settings_json       JSONB,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
```

---

## 5. System Tables

### 5.1 Sessions Table

Stores active user sessions for authentication.

```sql
CREATE TABLE sessions (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token               VARCHAR(500) UNIQUE NOT NULL,
    refresh_token       VARCHAR(500) UNIQUE,
    ip_address          INET,
    user_agent          TEXT,
    expires_at          TIMESTAMP NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

---

### 5.2 Audit Log Table

Tracks important system events and user actions.

```sql
CREATE TABLE audit_log (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action              VARCHAR(100) NOT NULL,
    entity_type         VARCHAR(100),
    entity_id           INTEGER,
    old_values          JSONB,
    new_values          JSONB,
    ip_address          INET,
    user_agent          TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
```

---

## 6. Views

### 6.1 Campaign Performance View

Provides aggregated campaign performance metrics.

```sql
CREATE VIEW v_campaign_performance AS
SELECT 
    c.id AS campaign_id,
    c.user_id,
    c.name AS campaign_name,
    c.status,
    c.daily_budget,
    COUNT(DISTINCT k.id) AS keyword_count,
    COALESCE(SUM(pm.impressions), 0) AS total_impressions,
    COALESCE(SUM(pm.clicks), 0) AS total_clicks,
    COALESCE(SUM(pm.conversions), 0) AS total_conversions,
    COALESCE(SUM(pm.spend), 0) AS total_spend,
    COALESCE(SUM(pm.sales), 0) AS total_sales,
    CASE 
        WHEN SUM(pm.impressions) > 0 
        THEN ROUND((SUM(pm.clicks)::DECIMAL / SUM(pm.impressions) * 100), 2)
        ELSE 0 
    END AS ctr,
    CASE 
        WHEN SUM(pm.clicks) > 0 
        THEN ROUND((SUM(pm.conversions)::DECIMAL / SUM(pm.clicks) * 100), 2)
        ELSE 0 
    END AS cvr,
    CASE 
        WHEN SUM(pm.clicks) > 0 
        THEN ROUND((SUM(pm.spend) / SUM(pm.clicks)), 2)
        ELSE 0 
    END AS cpc,
    CASE 
        WHEN SUM(pm.sales) > 0 
        THEN ROUND((SUM(pm.spend) / SUM(pm.sales) * 100), 2)
        ELSE 0 
    END AS acos,
    CASE 
        WHEN SUM(pm.spend) > 0 
        THEN ROUND((SUM(pm.sales) / SUM(pm.spend)), 2)
        ELSE 0 
    END AS roas
FROM campaigns c
LEFT JOIN keywords k ON c.id = k.campaign_id AND k.status = 'active'
LEFT JOIN performance_metrics pm ON c.id = pm.campaign_id
GROUP BY c.id, c.user_id, c.name, c.status, c.daily_budget;
```

---

## 7. Prisma Schema

```prisma
// This is your Prisma schema file

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id                Int       @id @default(autoincrement())
  email             String    @unique @db.VarChar(255)
  passwordHash      String    @map("password_hash") @db.VarChar(255)
  firstName         String    @map("first_name") @db.VarChar(100)
  lastName          String    @map("last_name") @db.VarChar(100)
  role              String    @default("student") @db.VarChar(50)
  emailVerified     Boolean   @default(false) @map("email_verified")
  emailVerifiedAt   DateTime? @map("email_verified_at")
  status            String    @default("active") @db.VarChar(50)
  lastLoginAt       DateTime? @map("last_login_at")
  createdAt         DateTime  @default(now()) @map("created_at")
  updatedAt         DateTime  @updatedAt @map("updated_at")

  campaigns         Campaign[]
  products          Product[]
  tutorialProgress  TutorialProgress[]
  achievements      Achievement[]
  userSettings      UserSettings?
  sessions          Session[]
  auditLogs         AuditLog[]

  @@index([email])
  @@index([status])
  @@index([role])
  @@map("users")
}

model Campaign {
  id                 Int       @id @default(autoincrement())
  userId             Int       @map("user_id")
  name               String    @db.VarChar(255)
  campaignType       String    @default("sponsored_products") @map("campaign_type") @db.VarChar(50)
  targetingType      String    @default("manual") @map("targeting_type") @db.VarChar(50)
  dailyBudget        Decimal   @map("daily_budget") @db.Decimal(10, 2)
  status             String    @default("active") @db.VarChar(50)
  biddingStrategy    String    @default("manual") @map("bidding_strategy") @db.VarChar(50)
  startDate          DateTime  @default(now()) @map("start_date") @db.Date
  endDate            DateTime? @map("end_date") @db.Date
  totalBudget        Decimal?  @map("total_budget") @db.Decimal(10, 2)
  totalImpressions   BigInt    @default(0) @map("total_impressions")
  totalClicks        Int       @default(0) @map("total_clicks")
  totalConversions   Int       @default(0) @map("total_conversions")
  totalSpend         Decimal   @default(0) @map("total_spend") @db.Decimal(10, 2)
  totalSales         Decimal   @default(0) @map("total_sales") @db.Decimal(10, 2)
  createdAt          DateTime  @default(now()) @map("created_at")
  updatedAt          DateTime  @updatedAt @map("updated_at")

  user               User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  adGroups           AdGroup[]
  keywords           Keyword[]
  negativeKeywords   NegativeKeyword[]
  performanceMetrics PerformanceMetric[]
  dailySummary       DailySummary[]

  @@index([userId])
  @@index([status])
  @@index([campaignType])
  @@index([createdAt])
  @@map("campaigns")
}

model AdGroup {
  id          Int      @id @default(autoincrement())
  campaignId  Int      @map("campaign_id")
  name        String   @db.VarChar(255)
  defaultBid  Decimal  @map("default_bid") @db.Decimal(10, 2)
  status      String   @default("active") @db.VarChar(50)
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  campaign    Campaign @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  keywords    Keyword[]
  negativeKeywords NegativeKeyword[]

  @@index([campaignId])
  @@index([status])
  @@map("ad_groups")
}

model Keyword {
  id                Int       @id @default(autoincrement())
  campaignId        Int       @map("campaign_id")
  adGroupId         Int?      @map("ad_group_id")
  keywordText       String    @map("keyword_text") @db.VarChar(255)
  matchType         String    @map("match_type") @db.VarChar(50)
  bid               Decimal   @db.Decimal(10, 2)
  status            String    @default("active") @db.VarChar(50)
  qualityScore      Int       @default(5) @map("quality_score")
  baseCtr           Decimal   @default(0.0200) @map("base_ctr") @db.Decimal(5, 4)
  baseCvr           Decimal   @default(0.1000) @map("base_cvr") @db.Decimal(5, 4)
  totalImpressions  BigInt    @default(0) @map("total_impressions")
  totalClicks       Int       @default(0) @map("total_clicks")
  totalConversions  Int       @default(0) @map("total_conversions")
  totalSpend        Decimal   @default(0) @map("total_spend") @db.Decimal(10, 2)
  totalSales        Decimal   @default(0) @map("total_sales") @db.Decimal(10, 2)
  createdAt         DateTime  @default(now()) @map("created_at")
  updatedAt         DateTime  @updatedAt @map("updated_at")

  campaign          Campaign  @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  adGroup           AdGroup?  @relation(fields: [adGroupId], references: [id], onDelete: Cascade)
  performanceMetrics PerformanceMetric[]
  searchTerms       SearchTerm[]
  dailySummary      DailySummary[]

  @@unique([campaignId, keywordText, matchType])
  @@index([campaignId])
  @@index([adGroupId])
  @@index([status])
  @@index([matchType])
  @@map("keywords")
}

model NegativeKeyword {
  id          Int      @id @default(autoincrement())
  campaignId  Int?     @map("campaign_id")
  adGroupId   Int?     @map("ad_group_id")
  keywordText String   @map("keyword_text") @db.VarChar(255)
  matchType   String   @default("phrase") @map("match_type") @db.VarChar(50)
  createdAt   DateTime @default(now()) @map("created_at")

  campaign    Campaign? @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  adGroup     AdGroup?  @relation(fields: [adGroupId], references: [id], onDelete: Cascade)

  @@index([campaignId])
  @@index([adGroupId])
  @@map("negative_keywords")
}

model Product {
  id            Int      @id @default(autoincrement())
  userId        Int      @map("user_id")
  asin          String   @unique @db.VarChar(10)
  title         String   @db.VarChar(500)
  price         Decimal  @db.Decimal(10, 2)
  category      String?  @db.VarChar(255)
  imageUrl      String?  @map("image_url") @db.Text
  qualityScore  Int      @default(7) @map("quality_score")
  baseCvr       Decimal  @default(0.1000) @map("base_cvr") @db.Decimal(5, 4)
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")

  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([asin])
  @@map("products")
}

model PerformanceMetric {
  id          BigInt   @id @default(autoincrement())
  campaignId  Int      @map("campaign_id")
  keywordId   Int?     @map("keyword_id")
  date        DateTime @db.Date
  hour        Int
  impressions Int      @default(0)
  clicks      Int      @default(0)
  conversions Int      @default(0)
  spend       Decimal  @default(0) @db.Decimal(10, 2)
  sales       Decimal  @default(0) @db.Decimal(10, 2)
  ctr         Decimal? @db.Decimal(6, 4)
  cvr         Decimal? @db.Decimal(6, 4)
  cpc         Decimal? @db.Decimal(10, 2)
  acos        Decimal? @db.Decimal(6, 4)
  roas        Decimal? @db.Decimal(10, 2)
  createdAt   DateTime @default(now()) @map("created_at")

  campaign    Campaign @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  keyword     Keyword? @relation(fields: [keywordId], references: [id], onDelete: Cascade)

  @@unique([campaignId, keywordId, date, hour])
  @@index([campaignId])
  @@index([keywordId])
  @@index([date])
  @@index([campaignId, date])
  @@index([keywordId, date])
  @@map("performance_metrics")
}

model SearchTerm {
  id            BigInt   @id @default(autoincrement())
  keywordId     Int      @map("keyword_id")
  searchTerm    String   @map("search_term") @db.VarChar(255)
  impressions   Int      @default(0)
  clicks        Int      @default(0)
  conversions   Int      @default(0)
  spend         Decimal  @default(0) @db.Decimal(10, 2)
  sales         Decimal  @default(0) @db.Decimal(10, 2)
  firstSeenAt   DateTime @default(now()) @map("first_seen_at")
  lastSeenAt    DateTime @default(now()) @map("last_seen_at")
  updatedAt     DateTime @updatedAt @map("updated_at")

  keyword       Keyword  @relation(fields: [keywordId], references: [id], onDelete: Cascade)

  @@unique([keywordId, searchTerm])
  @@index([keywordId])
  @@index([searchTerm])
  @@map("search_terms")
}

model DailySummary {
  id          Int      @id @default(autoincrement())
  campaignId  Int      @map("campaign_id")
  keywordId   Int?     @map("keyword_id")
  date        DateTime @db.Date
  impressions Int      @default(0)
  clicks      Int      @default(0)
  conversions Int      @default(0)
  spend       Decimal  @default(0) @db.Decimal(10, 2)
  sales       Decimal  @default(0) @db.Decimal(10, 2)
  ctr         Decimal? @db.Decimal(6, 4)
  cvr         Decimal? @db.Decimal(6, 4)
  cpc         Decimal? @db.Decimal(10, 2)
  acos        Decimal? @db.Decimal(6, 4)
  roas        Decimal? @db.Decimal(10, 2)
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")

  campaign    Campaign @relation(fields: [campaignId], references: [id], onDelete: Cascade)
  keyword     Keyword? @relation(fields: [keywordId], references: [id], onDelete: Cascade)

  @@unique([campaignId, keywordId, date])
  @@index([date])
  @@map("daily_summary")
}

model TutorialProgress {
  id          Int       @id @default(autoincrement())
  userId      Int       @map("user_id")
  tutorialId  String    @map("tutorial_id") @db.VarChar(100)
  stepId      String    @map("step_id") @db.VarChar(100)
  completed   Boolean   @default(false)
  completedAt DateTime? @map("completed_at")
  createdAt   DateTime  @default(now()) @map("created_at")
  updatedAt   DateTime  @updatedAt @map("updated_at")

  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([userId, tutorialId, stepId])
  @@index([userId])
  @@map("tutorial_progress")
}

model Achievement {
  id              Int      @id @default(autoincrement())
  userId          Int      @map("user_id")
  achievementType String   @map("achievement_type") @db.VarChar(100)
  achievementData Json?    @map("achievement_data")
  earnedAt        DateTime @default(now()) @map("earned_at")

  user            User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([achievementType])
  @@map("achievements")
}

model UserSettings {
  id                  Int      @id @default(autoincrement())
  userId              Int      @unique @map("user_id")
  timezone            String   @default("UTC") @db.VarChar(50)
  currency            String   @default("USD") @db.VarChar(3)
  notificationsEmail  Boolean  @default(true) @map("notifications_email")
  theme               String   @default("light") @db.VarChar(20)
  settingsJson        Json?    @map("settings_json")
  createdAt           DateTime @default(now()) @map("created_at")
  updatedAt           DateTime @updatedAt @map("updated_at")

  user                User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@map("user_settings")
}

model Session {
  id           Int      @id @default(autoincrement())
  userId       Int      @map("user_id")
  token        String   @unique @db.VarChar(500)
  refreshToken String?  @unique @map("refresh_token") @db.VarChar(500)
  ipAddress    String?  @map("ip_address") @db.Inet
  userAgent    String?  @map("user_agent") @db.Text
  expiresAt    DateTime @map("expires_at")
  createdAt    DateTime @default(now()) @map("created_at")

  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId])
  @@index([token])
  @@index([expiresAt])
  @@map("sessions")
}

model AuditLog {
  id          BigInt   @id @default(autoincrement())
  userId      Int?     @map("user_id")
  action      String   @db.VarChar(100)
  entityType  String?  @map("entity_type") @db.VarChar(100)
  entityId    Int?     @map("entity_id")
  oldValues   Json?    @map("old_values")
  newValues   Json?    @map("new_values")
  ipAddress   String?  @map("ip_address") @db.Inet
  userAgent   String?  @map("user_agent") @db.Text
  createdAt   DateTime @default(now()) @map("created_at")

  user        User?    @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@index([userId])
  @@index([action])
  @@index([createdAt])
  @@index([entityType, entityId])
  @@map("audit_log")
}
```

---

## 8. Data Retention & Archival

### 8.1 Retention Policy
- **Performance Metrics:** Keep hourly data for 90 days, then archive to daily summaries
- **Daily Summary:** Keep indefinitely or until user account deletion
- **Audit Logs:** Keep for 1 year, then archive
- **Sessions:** Delete expired sessions daily
- **Deleted Campaigns:** Soft delete (status = 'archived'), hard delete after 30 days

### 8.2 Archival Strategy
```sql
-- Archive old hourly metrics to daily summaries
INSERT INTO daily_summary (campaign_id, keyword_id, date, impressions, clicks, conversions, spend, sales, ctr, cvr, cpc, acos, roas)
SELECT 
    campaign_id, 
    keyword_id, 
    date, 
    SUM(impressions), 
    SUM(clicks), 
    SUM(conversions), 
    SUM(spend), 
    SUM(sales),
    CASE WHEN SUM(impressions) > 0 THEN SUM(clicks)::DECIMAL / SUM(impressions) END,
    CASE WHEN SUM(clicks) > 0 THEN SUM(conversions)::DECIMAL / SUM(clicks) END,
    CASE WHEN SUM(clicks) > 0 THEN SUM(spend) / SUM(clicks) END,
    CASE WHEN SUM(sales) > 0 THEN SUM(spend) / SUM(sales) END,
    CASE WHEN SUM(spend) > 0 THEN SUM(sales) / SUM(spend) END
FROM performance_metrics
WHERE date < CURRENT_DATE - INTERVAL '90 days'
GROUP BY campaign_id, keyword_id, date
ON CONFLICT (campaign_id, COALESCE(keyword_id, 0), date) DO UPDATE
SET 
    impressions = EXCLUDED.impressions,
    clicks = EXCLUDED.clicks,
    conversions = EXCLUDED.conversions,
    spend = EXCLUDED.spend,
    sales = EXCLUDED.sales,
    updated_at = CURRENT_TIMESTAMP;

-- Delete old hourly metrics
DELETE FROM performance_metrics
WHERE date < CURRENT_DATE - INTERVAL '90 days';
```

---

## 9. Database Optimization

### 9.1 Performance Tips
1. **Indexes:** Ensure all foreign keys are indexed
2. **Partitioning:** Consider partitioning `performance_metrics` by date
3. **Materialized Views:** Create materialized views for complex aggregations
4. **Query Optimization:** Use EXPLAIN ANALYZE to optimize slow queries
5. **Connection Pooling:** Configure appropriate connection pool size
6. **Caching:** Use Redis to cache frequently accessed data

### 9.2 Monitoring Queries
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
    schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Approved By:** _________________
