# Logging Strategy
## Amazon PPC Simulator

**Version:** 1.0  
**Date:** October 2025

---

## 1. Logging Overview

### 1.1 Purpose
The logging strategy ensures:
- Comprehensive system monitoring and debugging
- Security audit trail
- Performance tracking
- Error diagnosis and resolution
- Compliance and accountability

### 1.2 Log Types
1. **Application Logs** - Application events and errors
2. **Access Logs** - HTTP requests and responses
3. **Security Logs** - Authentication and authorization events
4. **Audit Logs** - User actions and data changes
5. **Performance Logs** - Response times and resource usage
6. **Simulation Logs** - Simulation engine operations
7. **Error Logs** - Exceptions and failures

---

## 2. Log Levels

### 2.1 Log Level Definitions

| Level | Description | Use Cases | Examples |
|-------|-------------|-----------|----------|
| **ERROR** | Critical failures | System errors, exceptions | Database connection failed, API endpoint crashed |
| **WARN** | Warning conditions | Potential issues | High API latency, approaching rate limit |
| **INFO** | Informational messages | Important events | User logged in, campaign created, simulation completed |
| **DEBUG** | Debug information | Development/troubleshooting | Function parameters, query results |
| **TRACE** | Detailed trace | Deep debugging | Step-by-step execution flow |

### 2.2 Environment-Specific Levels

**Production:**
- Default: INFO
- Errors: ERROR + WARN
- No DEBUG or TRACE logs

**Staging:**
- Default: DEBUG
- All levels enabled

**Development:**
- Default: DEBUG
- All levels enabled

---

## 3. Application Logs

### 3.1 Log Format (JSON)

```json
{
  "timestamp": "2025-10-18T17:20:35.230Z",
  "level": "INFO",
  "service": "api-server",
  "environment": "production",
  "message": "Campaign created successfully",
  "context": {
    "userId": 1,
    "campaignId": 15,
    "campaignName": "Winter Sale"
  },
  "metadata": {
    "requestId": "req-abc123",
    "sessionId": "sess-xyz789",
    "ip": "192.168.1.100",
    "userAgent": "Mozilla/5.0..."
  }
}
```

### 3.2 Required Fields

Every log entry must include:
- `timestamp`: ISO 8601 format
- `level`: Log level
- `service`: Service name (api-server, simulation-engine, etc.)
- `environment`: production, staging, development
- `message`: Human-readable description
- `requestId`: Unique request identifier (for tracing)

### 3.3 Example Log Messages

**User Registration:**
```json
{
  "timestamp": "2025-10-18T10:00:00Z",
  "level": "INFO",
  "service": "api-server",
  "message": "User registered successfully",
  "context": {
    "userId": 42,
    "email": "user@example.com",
    "role": "student"
  },
  "metadata": {
    "requestId": "req-001",
    "ip": "192.168.1.100"
  }
}
```

**Campaign Creation:**
```json
{
  "timestamp": "2025-10-18T10:05:00Z",
  "level": "INFO",
  "service": "api-server",
  "message": "Campaign created",
  "context": {
    "userId": 42,
    "campaignId": 1,
    "campaignName": "Test Campaign",
    "dailyBudget": 50.00
  },
  "metadata": {
    "requestId": "req-002"
  }
}
```

**Error Example:**
```json
{
  "timestamp": "2025-10-18T10:10:00Z",
  "level": "ERROR",
  "service": "api-server",
  "message": "Database query failed",
  "error": {
    "name": "QueryError",
    "message": "Connection timeout",
    "stack": "Error: Connection timeout\n    at Database.query..."
  },
  "context": {
    "query": "SELECT * FROM campaigns WHERE id = $1",
    "params": [1]
  },
  "metadata": {
    "requestId": "req-003"
  }
}
```

---

## 4. Access Logs (HTTP)

### 4.1 Access Log Format

```json
{
  "timestamp": "2025-10-18T17:20:35.230Z",
  "type": "access",
  "method": "POST",
  "path": "/api/campaigns",
  "statusCode": 201,
  "responseTime": 145,
  "userAgent": "Mozilla/5.0...",
  "ip": "192.168.1.100",
  "userId": 42,
  "requestId": "req-abc123",
  "requestSize": 256,
  "responseSize": 512
}
```

### 4.2 Access Log Fields

- `method`: HTTP method (GET, POST, PUT, DELETE)
- `path`: Request path
- `statusCode`: HTTP status code
- `responseTime`: Response time in milliseconds
- `userAgent`: Client user agent
- `ip`: Client IP address
- `userId`: Authenticated user ID (if applicable)
- `requestId`: Unique request identifier
- `requestSize`: Request body size in bytes
- `responseSize`: Response body size in bytes

---

## 5. Security Logs

### 5.1 Authentication Events

**Successful Login:**
```json
{
  "timestamp": "2025-10-18T10:00:00Z",
  "level": "INFO",
  "type": "security",
  "event": "login_success",
  "context": {
    "userId": 42,
    "email": "user@example.com",
    "ip": "192.168.1.100",
    "userAgent": "Mozilla/5.0..."
  }
}
```

**Failed Login:**
```json
{
  "timestamp": "2025-10-18T10:00:30Z",
  "level": "WARN",
  "type": "security",
  "event": "login_failed",
  "context": {
    "email": "user@example.com",
    "reason": "invalid_password",
    "ip": "192.168.1.100",
    "attemptCount": 1
  }
}
```

**Account Lockout:**
```json
{
  "timestamp": "2025-10-18T10:01:00Z",
  "level": "WARN",
  "type": "security",
  "event": "account_locked",
  "context": {
    "email": "user@example.com",
    "reason": "too_many_failed_attempts",
    "ip": "192.168.1.100",
    "attemptCount": 5
  }
}
```

### 5.2 Authorization Events

**Permission Denied:**
```json
{
  "timestamp": "2025-10-18T10:05:00Z",
  "level": "WARN",
  "type": "security",
  "event": "permission_denied",
  "context": {
    "userId": 42,
    "resource": "campaign",
    "resourceId": 15,
    "action": "update",
    "reason": "not_owner"
  }
}
```

---

## 6. Audit Logs

### 6.1 Data Modification Events

**Campaign Updated:**
```json
{
  "timestamp": "2025-10-18T11:00:00Z",
  "level": "INFO",
  "type": "audit",
  "event": "campaign_updated",
  "context": {
    "userId": 42,
    "campaignId": 1,
    "changes": {
      "dailyBudget": {
        "old": 50.00,
        "new": 75.00
      },
      "status": {
        "old": "active",
        "new": "paused"
      }
    }
  },
  "metadata": {
    "ip": "192.168.1.100",
    "requestId": "req-005"
  }
}
```

**Keyword Deleted:**
```json
{
  "timestamp": "2025-10-18T11:05:00Z",
  "level": "INFO",
  "type": "audit",
  "event": "keyword_deleted",
  "context": {
    "userId": 42,
    "keywordId": 25,
    "campaignId": 1,
    "keywordData": {
      "keywordText": "old keyword",
      "matchType": "phrase",
      "bid": 1.25
    }
  }
}
```

### 6.2 Audit Log Storage

Audit logs are:
- Stored in database (`audit_log` table)
- Immutable (no updates or deletes)
- Retained for 1 year minimum
- Exported to long-term storage quarterly

---

## 7. Performance Logs

### 7.1 Slow Query Log

```json
{
  "timestamp": "2025-10-18T12:00:00Z",
  "level": "WARN",
  "type": "performance",
  "event": "slow_query",
  "context": {
    "query": "SELECT * FROM performance_metrics WHERE...",
    "duration": 2500,
    "threshold": 1000,
    "table": "performance_metrics",
    "rowsReturned": 10000
  }
}
```

### 7.2 API Performance Log

```json
{
  "timestamp": "2025-10-18T12:05:00Z",
  "level": "INFO",
  "type": "performance",
  "event": "api_metrics",
  "context": {
    "endpoint": "/api/campaigns",
    "method": "GET",
    "avgResponseTime": 145,
    "p95ResponseTime": 320,
    "p99ResponseTime": 580,
    "requestCount": 1000,
    "errorRate": 0.02
  },
  "timeWindow": "1h"
}
```

---

## 8. Simulation Logs

### 8.1 Simulation Execution

```json
{
  "timestamp": "2025-10-18T13:00:00Z",
  "level": "INFO",
  "type": "simulation",
  "event": "simulation_started",
  "context": {
    "simulationId": "sim-abc123",
    "campaignCount": 150,
    "keywordCount": 2500
  }
}
```

```json
{
  "timestamp": "2025-10-18T13:00:15Z",
  "level": "INFO",
  "type": "simulation",
  "event": "simulation_completed",
  "context": {
    "simulationId": "sim-abc123",
    "duration": 15000,
    "campaignsProcessed": 150,
    "keywordsProcessed": 2500,
    "metricsGenerated": 7500
  }
}
```

### 8.2 Simulation Errors

```json
{
  "timestamp": "2025-10-18T13:00:10Z",
  "level": "ERROR",
  "type": "simulation",
  "event": "simulation_error",
  "context": {
    "simulationId": "sim-abc123",
    "campaignId": 25,
    "keywordId": 150,
    "error": "Invalid quality score"
  }
}
```

---

## 9. Error Logs

### 9.1 Application Errors

```json
{
  "timestamp": "2025-10-18T14:00:00Z",
  "level": "ERROR",
  "service": "api-server",
  "message": "Unhandled exception in API endpoint",
  "error": {
    "name": "TypeError",
    "message": "Cannot read property 'id' of undefined",
    "stack": "TypeError: Cannot read property 'id' of undefined\n    at..."
  },
  "context": {
    "endpoint": "/api/campaigns/:id",
    "method": "GET",
    "params": { "id": "invalid" },
    "userId": 42
  },
  "metadata": {
    "requestId": "req-010",
    "nodeVersion": "18.17.0"
  }
}
```

### 9.2 Database Errors

```json
{
  "timestamp": "2025-10-18T14:05:00Z",
  "level": "ERROR",
  "service": "database",
  "message": "Database connection failed",
  "error": {
    "name": "ConnectionError",
    "message": "ECONNREFUSED 127.0.0.1:5432",
    "code": "ECONNREFUSED"
  },
  "context": {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "ppcsim",
    "retryAttempt": 3
  }
}
```

---

## 10. Log Storage & Rotation

### 10.1 Storage Strategy

**Development:**
- Console output
- Local files in `/logs` directory
- Rotation: Daily, keep 7 days

**Production:**
- Centralized logging service (e.g., AWS CloudWatch, Elasticsearch)
- Structured JSON format
- Retention: 30 days for application logs, 1 year for audit logs

### 10.2 File Naming Convention

```
logs/
├── app-2025-10-18.log
├── access-2025-10-18.log
├── error-2025-10-18.log
├── security-2025-10-18.log
└── simulation-2025-10-18.log
```

### 10.3 Log Rotation Rules

- **Daily Rotation:** Rotate at midnight UTC
- **Size-based:** Rotate when file exceeds 100MB
- **Compression:** Compress rotated files (gzip)
- **Retention:** 
  - Application logs: 30 days
  - Access logs: 90 days
  - Security logs: 1 year
  - Audit logs: 1 year
  - Error logs: 90 days

---

## 11. Log Monitoring & Alerts

### 11.1 Alert Triggers

| Condition | Alert Level | Action |
|-----------|-------------|--------|
| Error rate > 5% | Critical | Page on-call engineer |
| Error rate > 1% | Warning | Send notification |
| API response time > 2s (p95) | Warning | Send notification |
| Database connection failed | Critical | Page on-call engineer |
| Disk space < 10% | Warning | Send notification |
| Failed login attempts > 5 | Warning | Security team notification |
| Simulation failed | Warning | Development team notification |

### 11.2 Monitoring Dashboards

**Application Health:**
- Request rate (requests/minute)
- Error rate (%)
- Response time (p50, p95, p99)
- Active users

**System Health:**
- CPU usage
- Memory usage
- Disk usage
- Database connections

**Business Metrics:**
- User registrations
- Campaigns created
- Simulation runs
- Active campaigns

---

## 12. Implementation

### 12.1 Logging Libraries

**Node.js Backend:**
```javascript
// Using Winston for logging
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'api-server',
    environment: process.env.NODE_ENV
  },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/app.log' }),
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

// Usage
logger.info('Campaign created', {
  context: {
    userId: 42,
    campaignId: 1,
    campaignName: 'Test Campaign'
  },
  metadata: {
    requestId: 'req-001'
  }
});
```

**HTTP Access Logging:**
```javascript
// Using Morgan for HTTP logging
const morgan = require('morgan');

morgan.token('user-id', (req) => req.user?.id);

app.use(morgan(':method :url :status :response-time ms - user: :user-id', {
  stream: {
    write: (message) => logger.info(message.trim())
  }
}));
```

### 12.2 Request ID Middleware

```javascript
const { v4: uuidv4 } = require('uuid');

function requestIdMiddleware(req, res, next) {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('x-request-id', req.id);
  next();
}

app.use(requestIdMiddleware);
```

### 12.3 Error Logging Middleware

```javascript
function errorLoggingMiddleware(err, req, res, next) {
  logger.error('Unhandled error', {
    error: {
      name: err.name,
      message: err.message,
      stack: err.stack
    },
    context: {
      endpoint: req.path,
      method: req.method,
      params: req.params,
      query: req.query,
      userId: req.user?.id
    },
    metadata: {
      requestId: req.id,
      ip: req.ip,
      userAgent: req.headers['user-agent']
    }
  });
  
  next(err);
}

app.use(errorLoggingMiddleware);
```

---

## 13. Log Analysis

### 13.1 Common Queries

**Find all errors in last hour:**
```
level:ERROR AND timestamp:[now-1h TO now]
```

**Find slow API calls:**
```
type:performance AND responseTime:>1000
```

**Find failed login attempts by IP:**
```
type:security AND event:login_failed AND ip:"192.168.1.100"
```

**Find all actions by user:**
```
userId:42 AND timestamp:[2025-10-18 TO 2025-10-19]
```

### 13.2 Log Aggregation

Use tools like:
- **Elasticsearch + Kibana** for search and visualization
- **AWS CloudWatch Logs Insights** for AWS deployments
- **Grafana Loki** for lightweight log aggregation
- **Datadog** for comprehensive monitoring

---

## 14. Privacy & Compliance

### 14.1 Sensitive Data Handling

**Never log:**
- Passwords (plain or hashed)
- Credit card numbers
- Social security numbers
- API keys or secrets
- Session tokens (log only partial: `token:abc...xyz`)

**Mask sensitive data:**
```javascript
function maskEmail(email) {
  const [name, domain] = email.split('@');
  return `${name.slice(0, 2)}***@${domain}`;
}

logger.info('User registered', {
  context: {
    email: maskEmail(user.email) // us***@example.com
  }
});
```

### 14.2 GDPR Compliance

- Include user consent for logging personal data
- Provide user data export functionality
- Implement user data deletion (right to be forgotten)
- Anonymize logs after retention period

---

## 15. Best Practices

### 15.1 Do's ✅

- Use structured logging (JSON format)
- Include request ID for tracing
- Log at appropriate levels
- Include context and metadata
- Use correlation IDs across services
- Monitor and alert on logs
- Rotate and archive logs regularly

### 15.2 Don'ts ❌

- Don't log sensitive information
- Don't use excessive DEBUG logs in production
- Don't ignore errors (always log them)
- Don't use string concatenation for log messages
- Don't log without context
- Don't use synchronous logging in production

---

## 16. Sample Log Files

### 16.1 Application Log Sample

```
logs/app-2025-10-18.log:

{"timestamp":"2025-10-18T10:00:00Z","level":"INFO","service":"api-server","message":"Server started","context":{"port":3000,"environment":"production"}}
{"timestamp":"2025-10-18T10:00:15Z","level":"INFO","service":"api-server","message":"Database connected","context":{"host":"localhost","database":"ppcsim"}}
{"timestamp":"2025-10-18T10:05:30Z","level":"INFO","service":"api-server","message":"User logged in","context":{"userId":42,"email":"user@example.com"},"metadata":{"requestId":"req-001","ip":"192.168.1.100"}}
{"timestamp":"2025-10-18T10:10:00Z","level":"INFO","service":"api-server","message":"Campaign created","context":{"userId":42,"campaignId":1,"campaignName":"Test Campaign"},"metadata":{"requestId":"req-002"}}
```

### 16.2 Error Log Sample

```
logs/error-2025-10-18.log:

{"timestamp":"2025-10-18T10:15:00Z","level":"ERROR","service":"api-server","message":"Database query failed","error":{"name":"QueryError","message":"Connection timeout","stack":"Error: Connection timeout\n at..."},"context":{"query":"SELECT * FROM campaigns","params":[]},"metadata":{"requestId":"req-003"}}
{"timestamp":"2025-10-18T10:20:00Z","level":"ERROR","service":"api-server","message":"Unhandled exception","error":{"name":"TypeError","message":"Cannot read property 'id' of undefined","stack":"TypeError: Cannot read...\n at..."},"context":{"endpoint":"/api/campaigns/:id","userId":42},"metadata":{"requestId":"req-004"}}
```

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Maintained By:** Development Team
