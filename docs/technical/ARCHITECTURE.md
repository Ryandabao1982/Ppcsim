# System Architecture
## Amazon PPC Simulator

**Version:** 1.0  
**Date:** October 2025

---

## 1. Architecture Overview

The Amazon PPC Simulator follows a modern three-tier architecture with clear separation of concerns.

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React SPA (Single Page Application)                      │  │
│  │  - Redux State Management                                 │  │
│  │  - Material-UI Components                                 │  │
│  │  - React Router for Navigation                            │  │
│  │  - Axios for HTTP Requests                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/WebSocket
                            │ REST API / JSON
┌───────────────────────────▼─────────────────────────────────────┐
│                     Application Layer                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Node.js + Express API Server                            │  │
│  │  ┌────────────┬────────────┬───────────┬──────────────┐ │  │
│  │  │    Auth    │  Campaign  │Simulation │   Analytics  │ │  │
│  │  │  Service   │  Service   │  Engine   │   Service    │ │  │
│  │  └────────────┴────────────┴───────────┴──────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │         Middleware (Auth, Validation, Logging)       │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Prisma ORM / SQL
┌───────────────────────────▼─────────────────────────────────────┐
│                         Data Layer                               │
│  ┌────────────────────┐         ┌──────────────────────────┐   │
│  │   PostgreSQL       │         │        Redis             │   │
│  │  - User Data       │         │  - Session Storage       │   │
│  │  - Campaigns       │         │  - Cache Layer           │   │
│  │  - Performance     │         │  - Rate Limiting         │   │
│  │  - Analytics       │         │  - Real-time Data        │   │
│  └────────────────────┘         └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      React Application                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Pages/Routes                           │ │
│  │  ┌──────────┬──────────┬──────────┬─────────┬─────────┐ │ │
│  │  │   Home   │Dashboard │Campaigns │Keywords │Tutorial │ │ │
│  │  └──────────┴──────────┴──────────┴─────────┴─────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                    Components                            │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │ Campaign │  Keyword   │  Chart   │  Table         │ │ │
│  │  │   Card   │   Table    │Components│ Components     │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │              Redux Store (State Management)              │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │   Auth   │  Campaign  │ Keyword  │   Analytics    │ │ │
│  │  │  Slice   │   Slice    │  Slice   │     Slice      │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                   API Service Layer                      │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │ authAPI  │campaignAPI │keywordAPI│  analyticsAPI  │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 Backend Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Express Application                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Routes Layer                           │ │
│  │  ┌──────────┬──────────┬──────────┬──────────┬────────┐ │ │
│  │  │   Auth   │ Campaign │ Keyword  │Analytics │Tutorial│ │ │
│  │  │  Routes  │  Routes  │  Routes  │  Routes  │ Routes │ │ │
│  │  └──────────┴──────────┴──────────┴──────────┴────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                 Middleware Layer                         │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │   Auth   │ Validation │  Error   │    Logging     │ │ │
│  │  │Middleware│ Middleware │ Handler  │   Middleware   │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                 Controllers Layer                        │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │   Auth   │  Campaign  │ Keyword  │   Analytics    │ │ │
│  │  │Controller│ Controller │Controller│   Controller   │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                  Services Layer                          │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │   Auth   │  Campaign  │Simulation│   Analytics    │ │ │
│  │  │ Service  │  Service   │  Engine  │    Service     │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐ │
│  │                Data Access Layer (Prisma)                │ │
│  │  ┌──────────┬────────────┬──────────┬────────────────┐ │ │
│  │  │   User   │  Campaign  │ Keyword  │  Performance   │ │ │
│  │  │  Model   │   Model    │  Model   │     Model      │ │ │
│  │  └──────────┴────────────┴──────────┴────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow

### 3.1 User Authentication Flow

```
User                  Frontend              Backend               Database
 │                       │                     │                      │
 │  1. Enter Credentials│                     │                      │
 ├──────────────────────>│                     │                      │
 │                       │ 2. POST /api/auth/login                   │
 │                       ├────────────────────>│                      │
 │                       │                     │ 3. Query User        │
 │                       │                     ├─────────────────────>│
 │                       │                     │<─────────────────────┤
 │                       │                     │ 4. Verify Password   │
 │                       │                     │                      │
 │                       │                     │ 5. Generate JWT      │
 │                       │                     │                      │
 │                       │ 6. Return Token     │                      │
 │                       │<────────────────────┤                      │
 │  7. Store Token       │                     │                      │
 │<──────────────────────┤                     │                      │
 │                       │                     │                      │
```

### 3.2 Campaign Creation Flow

```
User                  Frontend              Backend               Simulation
 │                       │                     │                      │
 │  1. Create Campaign   │                     │                      │
 ├──────────────────────>│                     │                      │
 │                       │ 2. POST /api/campaigns                    │
 │                       ├────────────────────>│                      │
 │                       │                     │ 3. Validate Data     │
 │                       │                     │                      │
 │                       │                     │ 4. Create DB Record  │
 │                       │                     ├─────────────────────>│
 │                       │                     │<─────────────────────┤
 │                       │                     │ 5. Queue Simulation  │
 │                       │                     ├─────────────────────>│
 │                       │ 6. Return Campaign  │                      │
 │                       │<────────────────────┤                      │
 │  7. Display Success   │                     │                      │
 │<──────────────────────┤                     │                      │
 │                       │                     │  8. Run Simulation   │
 │                       │                     │<─────────────────────┤
```

### 3.3 Simulation Engine Flow

```
Scheduler             Simulation Engine      Campaign Service      Database
 │                           │                      │                  │
 │  1. Trigger (Hourly)      │                      │                  │
 ├──────────────────────────>│                      │                  │
 │                           │ 2. Get Active Campaigns                 │
 │                           ├─────────────────────>│                  │
 │                           │                      │ 3. Query DB      │
 │                           │                      ├─────────────────>│
 │                           │                      │<─────────────────┤
 │                           │<─────────────────────┤                  │
 │                           │                      │                  │
 │                           │ 4. For Each Campaign │                  │
 │                           │    - Calculate Impressions              │
 │                           │    - Calculate Clicks                   │
 │                           │    - Calculate Conversions              │
 │                           │    - Calculate Costs                    │
 │                           │                      │                  │
 │                           │ 5. Save Metrics      │                  │
 │                           ├──────────────────────────────────────>  │
 │                           │<─────────────────────────────────────── │
 │                           │                      │                  │
 │  6. Complete              │                      │                  │
 │<──────────────────────────┤                      │                  │
```

---

## 4. Database Architecture

### 4.1 Entity Relationship Diagram

```
┌─────────────┐
│    Users    │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────▼──────────┐        ┌────────────────┐
│   Campaigns     │────────│  Ad Groups     │
└──────┬──────────┘  1:N   └────────┬───────┘
       │ 1                          │ 1
       │                            │
       │ N                          │ N
┌──────▼──────────┐        ┌────────▼───────┐
│    Keywords     │        │   Products     │
└──────┬──────────┘        └────────────────┘
       │ 1
       │
       │ N
┌──────▼──────────────────┐
│ Performance Metrics     │
└─────────────────────────┘

Other Tables:
- Negative Keywords (N:1 with Campaigns)
- Search Terms (N:1 with Keywords)
- Tutorial Progress (N:1 with Users)
- Achievements (N:1 with Users)
- Sessions (N:1 with Users)
- Audit Log (N:1 with Users)
```

### 4.2 Database Optimization

**Indexing Strategy:**
- Primary keys (automatic)
- Foreign keys (all relations)
- Frequently queried columns (status, date, user_id)
- Composite indexes for common query patterns

**Partitioning:**
- Partition `performance_metrics` by date (monthly)
- Partition `audit_log` by date (monthly)

**Caching:**
- Redis cache for frequently accessed data
- Campaign metrics cached for 5 minutes
- User sessions stored in Redis

---

## 5. Security Architecture

### 5.1 Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 1: Transport Security (HTTPS/TLS)            │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │  Layer 2: Authentication (JWT Tokens)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │  Layer 3: Authorization (RBAC)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │  Layer 4: Input Validation (Joi/Yup)                │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │  Layer 5: Data Protection (Encryption, Hashing)     │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────▼───────────────────────────┐   │
│  │  Layer 6: Rate Limiting & DoS Protection            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Authentication Flow

```
1. User submits credentials
2. Backend verifies credentials
3. Backend generates JWT token with:
   - User ID
   - Email
   - Role
   - Expiration (1 hour)
4. Token stored in HTTP-only cookie or local storage
5. Subsequent requests include token in Authorization header
6. Middleware validates token on each request
7. Token refreshed before expiration
```

---

## 6. API Architecture

### 6.1 RESTful API Design

**Resource-Based URLs:**
```
/api/campaigns              - Collection
/api/campaigns/:id          - Single resource
/api/campaigns/:id/keywords - Nested collection
```

**HTTP Methods:**
- GET - Retrieve resources
- POST - Create resources
- PUT - Update resources (full)
- PATCH - Update resources (partial)
- DELETE - Delete resources

**Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "pagination": { ... },
  "meta": { ... }
}
```

### 6.2 API Versioning

- Version in URL: `/api/v1/campaigns`
- Backwards compatibility maintained
- Deprecation notices for old versions

---

## 7. Simulation Engine Architecture

### 7.1 Simulation Algorithm

```
For each active campaign:
  For each active keyword:
    1. Calculate Base Impressions
       baseImpressions = calculateImpressions(budget, bid, competition)
    
    2. Calculate Click-Through Rate (CTR)
       ctr = baseCTR * qualityScoreMultiplier * bidPositionMultiplier
    
    3. Calculate Clicks
       clicks = impressions * ctr
    
    4. Calculate Conversion Rate (CVR)
       cvr = baseCVR * productQualityMultiplier
    
    5. Calculate Conversions
       conversions = clicks * cvr
    
    6. Calculate Costs
       cpc = calculateCPC(bid, qualityScore, competition)
       spend = clicks * cpc
    
    7. Calculate Sales
       sales = conversions * averageOrderValue
    
    8. Calculate Metrics
       acos = (spend / sales) * 100
       roas = sales / spend
    
    9. Save Performance Metrics to Database
```

### 7.2 Simulation Parameters

**Quality Score (1-10):**
- Affects CTR and CPC
- Based on relevance, landing page quality, historical performance

**Competition Level:**
- Low, Medium, High
- Affects CPC and impression share

**Time-Based Factors:**
- Hour of day multiplier (traffic patterns)
- Day of week multiplier
- Seasonal trends (future)

---

## 8. Scaling Strategy

### 8.1 Horizontal Scaling

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐   ┌──────▼────┐   ┌──────▼────┐
    │ API Server│   │ API Server│   │ API Server│
    │  Instance │   │ Instance  │   │ Instance  │
    └─────┬─────┘   └──────┬────┘   └──────┬────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼───────┐
                    │   Database   │
                    │  (Primary)   │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   Database   │
                    │  (Replica)   │
                    └──────────────┘
```

### 8.2 Caching Strategy

**Cache Layers:**
1. **Browser Cache:** Static assets (CSS, JS, images)
2. **CDN Cache:** Global content delivery
3. **Application Cache (Redis):**
   - User sessions
   - Frequently accessed data
   - Campaign metrics (5-minute TTL)
4. **Database Query Cache:** PostgreSQL query cache

---

## 9. Monitoring & Observability

### 9.1 Monitoring Stack

```
┌────────────────────────────────────────────────────────┐
│                  Application Layer                      │
│  ┌──────────┬────────────┬──────────┬──────────────┐  │
│  │  Logs    │  Metrics   │  Traces  │   Events     │  │
│  └────┬─────┴──────┬─────┴─────┬────┴──────┬───────┘  │
└───────┼────────────┼───────────┼───────────┼──────────┘
        │            │           │           │
        │            │           │           │
┌───────▼────────────▼───────────▼───────────▼──────────┐
│              Aggregation & Storage                     │
│  ┌──────────┬────────────┬──────────┬──────────────┐  │
│  │ Winston  │Prometheus  │  Jaeger  │  EventBus    │  │
│  └────┬─────┴──────┬─────┴─────┬────┴──────┬───────┘  │
└───────┼────────────┼───────────┼───────────┼──────────┘
        │            │           │           │
┌───────▼────────────▼───────────▼───────────▼──────────┐
│              Visualization & Alerting                  │
│  ┌──────────┬────────────┬──────────┬──────────────┐  │
│  │ Kibana   │  Grafana   │  Jaeger  │ PagerDuty    │  │
│  └──────────┴────────────┴──────────┴──────────────┘  │
└────────────────────────────────────────────────────────┘
```

### 9.2 Health Checks

**Liveness Probe:**
- Endpoint: `/health/live`
- Checks: Application is running

**Readiness Probe:**
- Endpoint: `/health/ready`
- Checks: Database connection, Redis connection

**Metrics Endpoint:**
- Endpoint: `/metrics`
- Format: Prometheus format

---

## 10. Deployment Architecture

### 10.1 Production Environment

```
┌──────────────────────────────────────────────────────────┐
│                    Cloud Provider (AWS)                   │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │                Application Layer                    │  │
│  │  ┌──────────┬──────────┬──────────┬──────────────┐ │  │
│  │  │    ECS   │   ECS    │   ECS    │     ECS      │ │  │
│  │  │Container │Container │Container │  Container   │ │  │
│  │  │(Frontend)│(Backend) │(Backend) │  (Workers)   │ │  │
│  │  └──────────┴──────────┴──────────┴──────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │                 Data Layer                          │  │
│  │  ┌──────────┬──────────────────┬─────────────────┐ │  │
│  │  │   RDS    │  ElastiCache     │       S3        │ │  │
│  │  │PostgreSQL│     Redis        │  Static Assets  │ │  │
│  │  └──────────┴──────────────────┴─────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Supporting Services                    │  │
│  │  ┌──────────┬──────────────────┬─────────────────┐ │  │
│  │  │CloudWatch│  CloudFront CDN  │   Route 53      │ │  │
│  │  │  Logs    │                  │      DNS        │ │  │
│  │  └──────────┴──────────────────┴─────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## 11. Technology Decisions

### 11.1 Why These Technologies?

**React:**
- Component-based architecture
- Large ecosystem and community
- Excellent performance with virtual DOM
- Easy state management with Redux

**Node.js + Express:**
- JavaScript across full stack
- High performance for I/O operations
- Large package ecosystem (npm)
- Easy to scale

**PostgreSQL:**
- ACID compliance
- Complex query support
- JSON support for flexibility
- Mature and reliable

**Prisma:**
- Type-safe database access
- Automatic migrations
- Great developer experience
- Modern ORM approach

**Redis:**
- Fast in-memory storage
- Ideal for caching and sessions
- Pub/sub for real-time features
- Low latency

---

## 12. Future Architecture Considerations

### 12.1 Microservices Migration

Consider breaking into microservices:
- **Auth Service:** User authentication and authorization
- **Campaign Service:** Campaign management
- **Simulation Service:** Performance simulation
- **Analytics Service:** Reporting and analytics
- **Notification Service:** Email and push notifications

### 12.2 Event-Driven Architecture

Implement event bus for:
- Campaign created → Trigger simulation
- Performance updated → Update dashboard
- Achievement unlocked → Send notification

### 12.3 Real-Time Features

WebSocket implementation for:
- Live campaign updates
- Real-time notifications
- Collaborative features

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Maintained By:** Architecture Team
