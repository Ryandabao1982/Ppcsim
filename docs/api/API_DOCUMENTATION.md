# API Documentation
## Amazon PPC Simulator REST API

**Version:** 1.0  
**Base URL:** `https://api.ppcsimulator.com/v1`  
**Protocol:** HTTPS  
**Authentication:** JWT Bearer Token

---

## Table of Contents
1. [Authentication](#1-authentication)
2. [Campaigns](#2-campaigns)
3. [Keywords](#3-keywords)
4. [Performance](#4-performance)
5. [Tutorial](#5-tutorial)
6. [User](#6-user)
7. [Error Handling](#7-error-handling)
8. [Rate Limiting](#8-rate-limiting)

---

## 1. Authentication

### 1.1 Register User
**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "student"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Validation:**
- Email: Valid email format, unique
- Password: Minimum 8 characters, at least one uppercase, one lowercase, one number
- First/Last Name: 2-100 characters

---

### 1.2 Login
**POST** `/api/auth/login`

Authenticate and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "student"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}
```

---

### 1.3 Refresh Token
**POST** `/api/auth/refresh`

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 3600
  }
}
```

---

### 1.4 Logout
**POST** `/api/auth/logout`

Invalidate current session.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 1.5 Forgot Password
**POST** `/api/auth/forgot-password`

Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password reset email sent"
}
```

---

### 1.6 Reset Password
**POST** `/api/auth/reset-password`

Reset password using token from email.

**Request Body:**
```json
{
  "token": "reset-token-from-email",
  "newPassword": "NewSecurePass123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

---

## 2. Campaigns

All campaign endpoints require authentication.

### 2.1 List Campaigns
**GET** `/api/campaigns`

Get all campaigns for authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `paused`, `archived`)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)
- `sort` (optional): Sort field (`name`, `created_at`, `spend`, default: `created_at`)
- `order` (optional): Sort order (`asc`, `desc`, default: `desc`)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "campaigns": [
      {
        "id": 1,
        "name": "Summer Sale Campaign",
        "campaignType": "sponsored_products",
        "targetingType": "manual",
        "dailyBudget": 50.00,
        "status": "active",
        "biddingStrategy": "manual",
        "startDate": "2025-10-01",
        "endDate": null,
        "metrics": {
          "impressions": 15420,
          "clicks": 308,
          "conversions": 31,
          "spend": 123.20,
          "sales": 775.00,
          "acos": 15.90,
          "ctr": 2.00,
          "cvr": 10.06
        },
        "createdAt": "2025-10-01T10:00:00Z",
        "updatedAt": "2025-10-18T15:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "pages": 1
    }
  }
}
```

---

### 2.2 Get Campaign
**GET** `/api/campaigns/:id`

Get detailed information for a specific campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "campaign": {
      "id": 1,
      "name": "Summer Sale Campaign",
      "campaignType": "sponsored_products",
      "targetingType": "manual",
      "dailyBudget": 50.00,
      "status": "active",
      "biddingStrategy": "manual",
      "startDate": "2025-10-01",
      "endDate": null,
      "totalBudget": null,
      "keywordCount": 15,
      "metrics": {
        "impressions": 15420,
        "clicks": 308,
        "conversions": 31,
        "spend": 123.20,
        "sales": 775.00,
        "acos": 15.90,
        "tacos": 12.50,
        "ctr": 2.00,
        "cvr": 10.06,
        "cpc": 0.40,
        "roas": 6.29
      },
      "createdAt": "2025-10-01T10:00:00Z",
      "updatedAt": "2025-10-18T15:30:00Z"
    }
  }
}
```

---

### 2.3 Create Campaign
**POST** `/api/campaigns`

Create a new campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Winter Sale Campaign",
  "campaignType": "sponsored_products",
  "targetingType": "manual",
  "dailyBudget": 50.00,
  "biddingStrategy": "manual",
  "startDate": "2025-11-01",
  "endDate": null,
  "totalBudget": null
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "campaign": {
      "id": 2,
      "name": "Winter Sale Campaign",
      "campaignType": "sponsored_products",
      "targetingType": "manual",
      "dailyBudget": 50.00,
      "status": "active",
      "biddingStrategy": "manual",
      "startDate": "2025-11-01",
      "endDate": null,
      "totalBudget": null,
      "createdAt": "2025-10-18T16:00:00Z",
      "updatedAt": "2025-10-18T16:00:00Z"
    }
  }
}
```

**Validation:**
- `name`: Required, 3-255 characters
- `dailyBudget`: Required, min 1.00, max 10000.00
- `campaignType`: One of: `sponsored_products`, `sponsored_brands`, `sponsored_display`
- `targetingType`: One of: `manual`, `automatic`
- `biddingStrategy`: One of: `manual`, `dynamic_down`, `dynamic_up_down`

---

### 2.4 Update Campaign
**PUT** `/api/campaigns/:id`

Update campaign settings.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Updated Campaign Name",
  "dailyBudget": 75.00,
  "status": "active"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "campaign": {
      "id": 1,
      "name": "Updated Campaign Name",
      "dailyBudget": 75.00,
      "status": "active",
      "updatedAt": "2025-10-18T16:15:00Z"
    }
  }
}
```

---

### 2.5 Delete Campaign
**DELETE** `/api/campaigns/:id`

Delete a campaign (soft delete - status changed to archived).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Campaign deleted successfully"
}
```

---

### 2.6 Pause/Resume Campaign
**PUT** `/api/campaigns/:id/status`

Change campaign status.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "status": "paused"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "campaign": {
      "id": 1,
      "status": "paused",
      "updatedAt": "2025-10-18T16:20:00Z"
    }
  }
}
```

---

## 3. Keywords

### 3.1 List Keywords
**GET** `/api/campaigns/:campaignId/keywords`

Get all keywords for a campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `paused`)
- `matchType` (optional): Filter by match type (`broad`, `phrase`, `exact`)
- `sort` (optional): Sort field (default: `created_at`)
- `order` (optional): Sort order (default: `desc`)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "keywords": [
      {
        "id": 1,
        "campaignId": 1,
        "keywordText": "wireless headphones",
        "matchType": "phrase",
        "bid": 1.25,
        "status": "active",
        "qualityScore": 7,
        "metrics": {
          "impressions": 1240,
          "clicks": 31,
          "conversions": 4,
          "spend": 38.75,
          "sales": 199.96,
          "acos": 19.38,
          "ctr": 2.50,
          "cvr": 12.90,
          "cpc": 1.25
        },
        "createdAt": "2025-10-01T10:30:00Z",
        "updatedAt": "2025-10-18T15:30:00Z"
      }
    ]
  }
}
```

---

### 3.2 Create Keyword
**POST** `/api/campaigns/:campaignId/keywords`

Add a new keyword to campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "keywordText": "bluetooth speakers",
  "matchType": "phrase",
  "bid": 0.85
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "keyword": {
      "id": 2,
      "campaignId": 1,
      "keywordText": "bluetooth speakers",
      "matchType": "phrase",
      "bid": 0.85,
      "status": "active",
      "qualityScore": 5,
      "createdAt": "2025-10-18T16:30:00Z"
    }
  }
}
```

**Validation:**
- `keywordText`: Required, 1-255 characters
- `matchType`: Required, one of: `broad`, `phrase`, `exact`
- `bid`: Required, min 0.20, max 100.00
- Duplicate check: Same keyword text + match type in campaign

---

### 3.3 Update Keyword
**PUT** `/api/keywords/:id`

Update keyword bid or status.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "bid": 1.50,
  "status": "active"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "keyword": {
      "id": 1,
      "bid": 1.50,
      "status": "active",
      "updatedAt": "2025-10-18T16:35:00Z"
    }
  }
}
```

---

### 3.4 Delete Keyword
**DELETE** `/api/keywords/:id`

Delete a keyword.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Keyword deleted successfully"
}
```

---

### 3.5 List Negative Keywords
**GET** `/api/campaigns/:campaignId/negative-keywords`

Get all negative keywords for a campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "negativeKeywords": [
      {
        "id": 1,
        "campaignId": 1,
        "keywordText": "cheap",
        "matchType": "phrase",
        "createdAt": "2025-10-01T11:00:00Z"
      }
    ]
  }
}
```

---

### 3.6 Add Negative Keyword
**POST** `/api/campaigns/:campaignId/negative-keywords`

Add a negative keyword to campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "keywordText": "free",
  "matchType": "phrase"
}
```

**Response:** `201 Created`
```json
{
  "success": true,
  "data": {
    "negativeKeyword": {
      "id": 2,
      "campaignId": 1,
      "keywordText": "free",
      "matchType": "phrase",
      "createdAt": "2025-10-18T16:40:00Z"
    }
  }
}
```

---

### 3.7 Delete Negative Keyword
**DELETE** `/api/negative-keywords/:id`

Delete a negative keyword.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Negative keyword deleted successfully"
}
```

---

## 4. Performance

### 4.1 Get Campaign Metrics
**GET** `/api/campaigns/:id/metrics`

Get aggregated performance metrics for a campaign.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `startDate` (optional): Start date (YYYY-MM-DD, default: 7 days ago)
- `endDate` (optional): End date (YYYY-MM-DD, default: today)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "metrics": {
      "impressions": 15420,
      "clicks": 308,
      "conversions": 31,
      "spend": 123.20,
      "sales": 775.00,
      "ctr": 2.00,
      "cvr": 10.06,
      "cpc": 0.40,
      "acos": 15.90,
      "tacos": 12.50,
      "roas": 6.29
    },
    "dateRange": {
      "startDate": "2025-10-11",
      "endDate": "2025-10-18"
    }
  }
}
```

---

### 4.2 Get Campaign Performance Timeline
**GET** `/api/campaigns/:id/performance`

Get time-series performance data for charts.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `startDate` (optional): Start date (YYYY-MM-DD)
- `endDate` (optional): End date (YYYY-MM-DD)
- `granularity` (optional): `hourly`, `daily` (default: `daily`)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "performance": [
      {
        "date": "2025-10-11",
        "impressions": 2100,
        "clicks": 42,
        "conversions": 4,
        "spend": 16.80,
        "sales": 99.96,
        "acos": 16.80,
        "ctr": 2.00,
        "cvr": 9.52
      },
      {
        "date": "2025-10-12",
        "impressions": 2250,
        "clicks": 45,
        "conversions": 5,
        "spend": 18.00,
        "sales": 124.95,
        "acos": 14.41,
        "ctr": 2.00,
        "cvr": 11.11
      }
    ]
  }
}
```

---

### 4.3 Get Keyword Metrics
**GET** `/api/keywords/:id/metrics`

Get performance metrics for a specific keyword.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `startDate` (optional): Start date (YYYY-MM-DD)
- `endDate` (optional): End date (YYYY-MM-DD)

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "keyword": {
      "id": 1,
      "keywordText": "wireless headphones",
      "matchType": "phrase",
      "bid": 1.25,
      "status": "active"
    },
    "metrics": {
      "impressions": 1240,
      "clicks": 31,
      "conversions": 4,
      "spend": 38.75,
      "sales": 199.96,
      "ctr": 2.50,
      "cvr": 12.90,
      "cpc": 1.25,
      "acos": 19.38,
      "roas": 5.16
    }
  }
}
```

---

### 4.4 Get Search Term Report
**GET** `/api/keywords/:id/search-terms`

Get search terms that triggered a keyword (future feature).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "searchTerms": [
      {
        "searchTerm": "wireless headphones bluetooth",
        "impressions": 520,
        "clicks": 13,
        "conversions": 2,
        "spend": 16.25,
        "sales": 99.98,
        "acos": 16.26
      }
    ]
  }
}
```

---

## 5. Tutorial

### 5.1 Get Tutorial Progress
**GET** `/api/tutorial/progress`

Get user's tutorial progress.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "progress": [
      {
        "tutorialId": "getting-started",
        "stepId": "create-campaign",
        "completed": true,
        "completedAt": "2025-10-18T10:00:00Z"
      },
      {
        "tutorialId": "getting-started",
        "stepId": "add-keywords",
        "completed": true,
        "completedAt": "2025-10-18T10:15:00Z"
      },
      {
        "tutorialId": "getting-started",
        "stepId": "view-performance",
        "completed": false,
        "completedAt": null
      }
    ],
    "completionRate": 66.67
  }
}
```

---

### 5.2 Update Tutorial Progress
**POST** `/api/tutorial/progress`

Mark a tutorial step as completed.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "tutorialId": "getting-started",
  "stepId": "view-performance",
  "completed": true
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "progress": {
      "tutorialId": "getting-started",
      "stepId": "view-performance",
      "completed": true,
      "completedAt": "2025-10-18T16:45:00Z"
    }
  }
}
```

---

## 6. User

### 6.1 Get Profile
**GET** `/api/user/profile`

Get current user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "role": "student",
      "emailVerified": true,
      "createdAt": "2025-10-01T09:00:00Z",
      "lastLoginAt": "2025-10-18T16:00:00Z"
    }
  }
}
```

---

### 6.2 Update Profile
**PUT** `/api/user/profile`

Update user profile information.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "email": "john.smith@example.com"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "john.smith@example.com",
      "firstName": "John",
      "lastName": "Smith",
      "updatedAt": "2025-10-18T16:50:00Z"
    }
  }
}
```

---

### 6.3 Change Password
**PUT** `/api/user/password`

Change user password.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "currentPassword": "OldPassword123!",
  "newPassword": "NewPassword123!"
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

## 7. Error Handling

### 7.1 Error Response Format

All errors follow a consistent format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email is already in use"
      }
    ]
  }
}
```

### 7.2 Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | VALIDATION_ERROR | Request validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 401 | INVALID_CREDENTIALS | Email or password incorrect |
| 401 | TOKEN_EXPIRED | Access token has expired |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource already exists |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_ERROR | Server error |

### 7.3 Validation Errors

Validation errors include field-specific details:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "dailyBudget",
        "message": "Daily budget must be at least 1.00"
      },
      {
        "field": "name",
        "message": "Campaign name is required"
      }
    ]
  }
}
```

---

## 8. Rate Limiting

### 8.1 Rate Limits

- **Authentication Endpoints:** 10 requests per minute per IP
- **API Endpoints:** 100 requests per minute per user
- **Bulk Operations:** 20 requests per minute per user

### 8.2 Rate Limit Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

### 8.3 Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retryAfter": 60
  }
}
```

---

## 9. Pagination

### 9.1 Pagination Parameters

- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

### 9.2 Pagination Response

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

---

## 10. Webhooks (Future Feature)

### 10.1 Event Types

- `campaign.created`
- `campaign.updated`
- `campaign.performance.threshold`
- `keyword.added`
- `tutorial.completed`

### 10.2 Webhook Payload

```json
{
  "event": "campaign.created",
  "timestamp": "2025-10-18T16:00:00Z",
  "data": {
    "campaignId": 1,
    "userId": 1,
    "name": "New Campaign"
  }
}
```

---

**API Version:** 1.0  
**Last Updated:** October 2025  
**Support:** api-support@ppcsimulator.com
