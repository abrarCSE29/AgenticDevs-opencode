# Architecture Document — DMTCL Online Card Recharge System

**Project Name:** DMTCL Online Card Recharge System  
**Document Version:** 1.0  
**Last Updated:** March 31, 2026  
**Prepared By:** Solution Architect  
**Status:** Draft  
**Related Documents:**  
- [BRD](brd-dmtcl-card-recharge.md)  
- [PRD](prd-dmtcl-card-recharge.md)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Pattern](#2-architecture-pattern)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [API Design](#5-api-design)
6. [Authentication & Authorization](#6-authentication--authorization)
7. [Caching Strategy](#7-caching-strategy)
8. [RBAC Model](#8-rbac-model)
9. [Scalability Strategy](#9-scalability-strategy)
10. [Data Flow](#10-data-flow)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Monitoring & Observability](#12-monitoring--observability)
13. [Security Architecture](#13-security-architecture)
14. [Internationalization (i18n)](#14-internationalization-i18n)
15. [Architecture Decision Records (ADR)](#15-architecture-decision-records-adr)
16. [Risk Mitigation](#16-risk-mitigation)

---

## 1. Executive Summary

This document defines the technical architecture for the DMTCL Online Card Recharge System — a web-based platform enabling metro rail commuters to recharge their transit cards online via bKash payment integration. The system supports real-time balance updates, card-to-account synchronization from station gates/POS terminals, transaction history, and an admin dashboard for monitoring and reconciliation.

The architecture follows a **monolithic full-stack pattern** using Next.js, PostgreSQL, and Redis, chosen for fast time-to-market, strong transaction integrity, and operational simplicity. The design supports 10,000 concurrent users and 500,000 daily transactions with 99.9% uptime.

---

## 2. Architecture Pattern

### Chosen Pattern: Monolith (Next.js Full-Stack)

**Justification:**
- Team size is expected to be small-to-medium (1-5 developers initially)
- Fast time-to-market is critical (6-month timeline)
- Clear domain boundaries exist but not enough to justify microservices overhead
- Financial transactions require strong consistency — monolith simplifies transaction management
- Can evolve to microservices later if scaling demands it (e.g., extract sync service independently)

**Architecture Style:** API-first monolith with server-side rendering

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Application                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  React UI   │  │  API Routes  │  │  Server Actions │ │
│  │  (SSR/CSR)  │  │  (REST)      │  │  (Mutations)    │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘ │
│         │                │                   │           │
│  ┌──────┴────────────────┴───────────────────┴────────┐ │
│  │              Service Layer (Business Logic)         │ │
│  │  - Auth Service  - Payment Service  - Sync Service  │ │
│  │  - Card Service  - Admin Service   - Notify Service │ │
│  └──────────────────────────┬─────────────────────────┘ │
│                             │                            │
└─────────────────────────────┼────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │PostgreSQL │  │   Redis   │  │  External │
        │  (Primary)│  │  (Cache)  │  │  APIs     │
        └───────────┘  └───────────┘  └───────────┘
```

---

## 3. Technology Stack

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Frontend** | Next.js (App Router) | 15+ | SSR for SEO, React Server Components, built-in API routes, i18n support |
| **UI Framework** | React 19 | 19+ | Component-based UI, hooks for state management |
| **Styling** | Tailwind CSS | 4+ | Utility-first, fast development, consistent design system |
| **Backend** | Next.js API Routes + Server Actions | — | Co-located with frontend, reduces deployment complexity |
| **Database** | PostgreSQL | 16+ | ACID compliance, strong transaction integrity (BRD C-006), JSONB for flexible sync payloads |
| **ORM** | Prisma | 5+ | Type-safe queries, migrations, connection pooling built-in |
| **Caching/Sessions** | Redis | 7+ | Session storage, API response caching, rate limiting, pub/sub for real-time updates |
| **Authentication** | JWT + Refresh Token Rotation | — | Stateless auth, secure token rotation, Redis-backed refresh token store |
| **Validation** | Zod | 3+ | Runtime type validation, schema inference to TypeScript types |
| **Payment Integration** | bKash API (REST) | — | Primary payment gateway (BRD C-001) |
| **SMS Gateway** | SSLWireless / GreenWeb | — | Bangladesh-based, reliable OTP delivery |
| **Email Service** | AWS SES / SendGrid | — | Transactional email delivery |
| **Hosting** | AWS (ECS Fargate or EC2) | — | Auto-scaling, VPC isolation, compliance with Bangladesh Bank regulations |
| **CDN** | CloudFront | — | Static asset delivery, edge caching |
| **CI/CD** | GitHub Actions | — | Automated testing, linting, deployment |
| **Monitoring** | OpenTelemetry + Grafana | — | APM, metrics, distributed tracing |
| **Logging** | Winston + ELK Stack | — | Structured logging, audit trail storage |
| **i18n** | next-intl | — | Bengali and English localization |

---

## 4. System Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │   Web App  │  │  Admin UI  │  │  Station   │  │  bKash     │    │
│  │  (Next.js) │  │  (Next.js) │  │  Gate API  │  │  Redirect  │    │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │
└────────┼───────────────┼───────────────┼───────────────┼────────────┘
         │               │               │               │
┌────────▼───────────────▼───────────────▼───────────────▼────────────┐
│                        API GATEWAY (Next.js)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  /api/auth │  │ /api/cards │  │ /api/pay   │  │ /api/sync  │   │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   │
│        │               │               │               │            │
│  ┌─────▼───────────────▼───────────────▼───────────────▼──────┐    │
│  │                   MIDDLEWARE LAYER                          │    │
│  │  Auth Guard → Rate Limiter → Input Validation → RBAC Check  │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                      SERVICE LAYER                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Auth    │ │  Card    │ │  Payment │ │  Sync    │ │  Admin   │ │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │ Service  │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │            │         │
│  ┌────▼────────────▼────────────▼────────────▼────────────▼─────┐  │
│  │                   DATA ACCESS LAYER (Prisma)                  │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                      DATA LAYER                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │  External Services       │  │
│  │  (Primary)   │  │  (Cache)     │  │  bKash, SMS, Email APIs  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Breakdown

| Module | Responsibility | Key Endpoints |
|--------|---------------|---------------|
| **Auth** | Registration, login, password reset, OTP, session management | `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh`, `/api/auth/forgot-password`, `/api/auth/reset-password`, `/api/auth/verify-otp` |
| **Card** | Card linking, validation, balance queries, unlinking | `/api/cards`, `/api/cards/{id}`, `/api/cards/{id}/balance` |
| **Payment** | bKash integration, recharge processing, payment callbacks | `/api/payments/initiate`, `/api/payments/callback`, `/api/payments/{id}/status` |
| **Sync** | Machine data ingestion, batch processing, conflict resolution | `/api/sync/tap`, `/api/sync/batch`, `/api/sync/status` |
| **Transaction** | Transaction history, filtering, export | `/api/transactions`, `/api/transactions/export` |
| **Admin** | User management, transaction oversight, reconciliation, balance adjustment | `/api/admin/users`, `/api/admin/transactions`, `/api/admin/reconciliation`, `/api/admin/balance-adjust` |
| **Notification** | SMS and email dispatch | Internal service (triggered by events) |

---

## 5. API Design

### API Conventions

- **Style:** RESTful with JSON request/response bodies
- **Versioning:** URL-based (`/api/v1/...`)
- **Authentication:** Bearer token (JWT) in `Authorization` header
- **Response Format:**
  ```json
  {
    "success": true,
    "data": { ... },
    "meta": { "page": 1, "total": 100 },
    "error": null
  }
  ```
- **Error Format:**
  ```json
  {
    "success": false,
    "data": null,
    "error": {
      "code": "PAYMENT_FAILED",
      "message": "Payment could not be processed",
      "details": { ... }
    }
  }
  ```
- **Pagination:** Cursor-based for transaction history, offset-based for admin lists
- **Rate Limiting:** Per-endpoint (see Scalability Strategy)

### Key API Endpoints

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| POST | `/api/v1/auth/register` | No | Guest | Register new user |
| POST | `/api/v1/auth/login` | No | Guest | Login with credentials |
| POST | `/api/v1/auth/verify-otp` | No | Guest | Verify OTP for login/registration |
| POST | `/api/v1/auth/refresh` | No | Guest | Refresh access token |
| POST | `/api/v1/auth/logout` | Yes | All | Invalidate session |
| GET | `/api/v1/cards` | Yes | User | List linked cards |
| POST | `/api/v1/cards` | Yes | User | Link a new card |
| DELETE | `/api/v1/cards/{id}` | Yes | User | Unlink a card |
| GET | `/api/v1/cards/{id}/balance` | Yes | User | Get card balance |
| POST | `/api/v1/payments/initiate` | Yes | User | Initiate bKash recharge |
| POST | `/api/v1/payments/callback` | No | System | bKash payment callback |
| GET | `/api/v1/transactions` | Yes | User | Transaction history |
| GET | `/api/v1/transactions/export` | Yes | User | Export as CSV/PDF |
| POST | `/api/v1/sync/tap` | Yes (API Key) | System | Single tap sync |
| POST | `/api/v1/sync/batch` | Yes (API Key) | System | Batch sync from offline machines |
| GET | `/api/v1/admin/users` | Yes | Admin | List/search users |
| GET | `/api/v1/admin/transactions` | Yes | Admin | All transactions |
| POST | `/api/v1/admin/balance-adjust` | Yes | Admin | Manual balance adjustment |
| GET | `/api/v1/admin/reconciliation` | Yes | Admin | Reconciliation report |
| GET | `/api/v1/admin/dashboard` | Yes | Admin | Dashboard overview |

---

## 6. Authentication & Authorization

### Authentication Flow

```
User → Login (phone/email + password)
  → Server validates credentials (bcrypt)
  → Server generates:
      - Access Token (JWT, 15min expiry)
      - Refresh Token (random, 7-day expiry, stored in Redis)
  → Refresh Token stored in HttpOnly, Secure, SameSite=Strict cookie
  → Access Token returned in response body
  → Client stores access token in memory (not localStorage)

On each request:
  → Client sends Access Token in Authorization header
  → Server validates JWT signature and expiry
  → If expired → Client calls /api/auth/refresh with cookie
  → Server validates refresh token in Redis, rotates it
  → New access token + new refresh token issued

On logout:
  → Server deletes refresh token from Redis
  → Client clears access token from memory
```

### Token Structure

**Access Token (JWT):**
```json
{
  "sub": "user-uuid",
  "role": "user",
  "phone": "+8801XXXXXXXXX",
  "iat": 1711900000,
  "exp": 1711900900
}
```

**Refresh Token:**
- Random 64-byte hex string
- Stored in Redis with key `refresh:{token_hash}` → `{ userId, expiresAt, userAgent }`
- Rotated on every use (old token invalidated)

### Security Measures
- Password hashing: bcrypt with cost factor 12 (NFR-009)
- JWT signing: RS256 (asymmetric) with key rotation
- Cookie flags: `HttpOnly`, `Secure`, `SameSite=Strict`
- Session timeout: 30 minutes of inactivity (BR-010)
- Brute force protection: Account lockout after 5 failed attempts in 15 minutes

---

## 7. Caching Strategy

### 7a. CDN/Edge Caching

| What | Technology | TTL | Invalidation |
|------|-----------|-----|--------------|
| Static assets (JS, CSS, images, fonts) | CloudFront | 1 year | Versioning (filename hash via Next.js build) |
| Landing page (public) | CloudFront | 5 min | On-demand purge on deploy |
| Bengali/English locale files | CloudFront | 1 hour | On deploy |
| bKash payment redirect page | No cache | — | Dynamic, user-specific |

**Hit rate target:** 95%+ for static assets  
**Fallback:** Serve from origin server if CDN miss  
**Why:** Reduces origin load, improves page load time (< 2s target per NFR-001)

### 7b. Application Caching (Redis)

| What | Technology | TTL | Invalidation |
|------|-----------|-----|--------------|
| User sessions (refresh tokens) | Redis | 7 days | Logout, password change |
| Access token blacklist | Redis | 15 min | Token expiry |
| Card balance (per card) | Redis | 30 seconds | On recharge, on tap sync |
| User dashboard data | Redis | 1 min | On any balance change |
| Transaction list (paginated) | Redis | 30 seconds | On new transaction |
| Rate limit counters | Redis | 1 min | Sliding window expiry |
| Admin dashboard aggregates | Redis | 5 min | Scheduled refresh |
| Configuration values (limits, thresholds) | Redis | 1 hour | On admin update or deploy |
| bKash payment session state | Redis | 30 min | On payment completion/timeout |

**Hit rate target:** 80%+ for balance queries, 70%+ for transaction lists  
**Fallback:** Query PostgreSQL directly on cache miss; never fail the request  
**Why:** Reduces database load during peak hours, ensures sub-500ms API response for sync endpoints (NFR-003)

### 7c. HTTP Caching

| Response Type | Headers | Client Cache |
|--------------|---------|--------------|
| Static assets | `Cache-Control: public, max-age=31536000, immutable` | 1 year |
| Landing page | `Cache-Control: public, max-age=300` | 5 min |
| User dashboard | `Cache-Control: private, no-store` | No cache |
| Transaction history | `Cache-Control: private, max-age=30` | 30 seconds |
| Card balance | `Cache-Control: private, no-cache` | Conditional (ETag) |
| Admin reports | `Cache-Control: private, no-store` | No cache |
| API error responses | `Cache-Control: no-store` | No cache |

**Why:** Prevents stale sensitive data on client side while allowing safe caching of public content

### Cache Invalidation Strategy

- **Write-through:** On recharge success, update DB → invalidate Redis balance cache → publish Redis pub/sub event
- **Pub/Sub:** Redis pub/sub channel `balance_updates:{cardId}` notifies all connected clients of balance changes
- **Tag-based:** Admin dashboard caches tagged with `admin:dashboard` — bulk invalidation on data changes
- **Time-based:** All caches have TTL as safety net even if invalidation fails

---

## 8. RBAC Model

### 8a. Roles and Hierarchy

```
Admin (full access)
  ├── Finance Admin (reconciliation, reports, financial data)
  └── Operations Admin (user management, sync monitoring, support)
User (own resources only)
Guest (public pages only)
```

**Role inheritance:** Admin > Finance Admin > Operations Admin > User > Guest

### 8b. API-Level Permissions

| Role | Permissions | Endpoints |
|------|-------------|-----------|
| **Admin** | Full CRUD + admin actions + balance adjustment | All endpoints |
| **Finance Admin** | Read all transactions, reconciliation reports, financial dashboards | `/api/admin/transactions`, `/api/admin/reconciliation`, `/api/admin/dashboard` (financial views) |
| **Operations Admin** | User management, sync monitoring, support actions | `/api/admin/users`, `/api/admin/transactions` (read), `/api/sync/status` |
| **User** | CRUD own resources | `/api/cards`, `/api/payments`, `/api/transactions`, `/api/auth/*` |
| **Guest** | Public pages, auth endpoints | `/api/auth/register`, `/api/auth/login`, `/api/auth/verify-otp` |

**Permission check locations:**
1. **Middleware (API route level):** Auth guard validates JWT, extracts role, checks route access
2. **Service layer:** Business logic enforces resource ownership (e.g., user can only see own transactions)
3. **Database:** Row-level security for sensitive financial data (enforced via Prisma middleware)

### 8c. UI-Level Permissions

| Role | Can See | Cannot See |
|------|---------|------------|
| **Admin** | All routes, admin panel, user management, reconciliation, system health, balance adjustment | — |
| **Finance Admin** | Financial dashboard, reconciliation reports, transaction overview | User management, balance adjustment, sync monitoring |
| **Operations Admin** | User search, support dashboard, sync status, transaction lookup | Financial reports, balance adjustment, system configuration |
| **User** | Dashboard, card management, recharge, transaction history, profile settings | Admin panel, other users' data |
| **Guest** | Landing page, registration, login, password reset | Dashboard, any authenticated content |

**Implementation:**
- Route-level guards in Next.js middleware (`middleware.ts`)
- Component-level visibility: `<RoleGuard allowedRoles={["admin"]}>` wrapper
- Features disabled (not hidden) when user lacks permission — shows "Access Denied" with explanation
- Server-side rendering checks role before rendering protected content

### 8d. Permission Matrix

| Action | Admin | Finance | Operations | User | Guest |
|--------|-------|---------|------------|------|-------|
| View all users | ✅ | ❌ | ✅ | ❌ | ❌ |
| Edit user accounts | ✅ | ❌ | ✅ | ❌ | ❌ |
| View all transactions | ✅ | ✅ | ✅ (read) | ❌ | ❌ |
| View own transactions | ✅ | ❌ | ❌ | ✅ | ❌ |
| Initiate recharge | ✅ | ❌ | ❌ | ✅ | ❌ |
| Adjust balance (dual approval) | ✅ | ❌ | ❌ | ❌ | ❌ |
| View reconciliation | ✅ | ✅ | ❌ | ❌ | ❌ |
| Monitor sync status | ✅ | ❌ | ✅ | ❌ | ❌ |
| Export transactions | ✅ | ✅ | ✅ | ✅ (own) | ❌ |
| Access admin dashboard | ✅ | ✅ (partial) | ✅ (partial) | ❌ | ❌ |

---

## 9. Scalability Strategy

### 9a. Capacity Planning

| Component | Current Target | 1-Year Target | Scaling Trigger |
|-----------|---------------|---------------|-----------------|
| API Server | 100 req/s | 1,000 req/s | CPU > 70% for 5 min |
| PostgreSQL | 500 writes/s, 2,000 reads/s | 5,000 writes/s, 20,000 reads/s | CPU > 60%, connection pool exhaustion |
| Redis | 10K ops/s | 100K ops/s | Memory > 80%, latency > 5ms |
| CDN (CloudFront) | 50 req/s | 500 req/s | Bandwidth > 80% |
| bKash API calls | 100/min | 1,000/min | Rate limit warnings from bKash |
| SMS Gateway | 50/min | 500/min | Delivery failure rate > 5% |

### 9b. Scaling Strategy

| Component | Scaling Type | Action | Max Scale |
|-----------|-------------|--------|-----------|
| API Server (Next.js) | Horizontal | Add ECS task instances behind ALB | 20 instances |
| PostgreSQL | Vertical first, then read replicas | Scale up instance, add read replicas for read-heavy queries | 1 primary + 5 replicas |
| Redis | Vertical first, then cluster | Scale up, enable cluster mode for sharding | 10 shards |
| File Storage (exports) | S3 offload | Store PDF/CSV exports in S3 with presigned URLs | Unlimited |
| CDN | Managed | CloudFront auto-scales | Unlimited |
| Sync API | Horizontal + Queue | Add workers, use Redis Streams for async batch processing | 10 workers |

### 9c. Rate Limiting

| Endpoint | Limit | Window | Response |
|----------|-------|--------|----------|
| Auth (login/register) | 5 attempts | 15 min | 429 + `Retry-After` header |
| OTP verification | 3 attempts | 15 min | 429 + `Retry-After` header |
| Payment initiation | 10 | 5 min | 429 + `Retry-After` header |
| API general (authenticated) | 100 | 1 min | 429 + `RateLimit-Reset` header |
| Sync endpoints (API key) | 1,000 | 1 min | 429 + `Retry-After` header |
| Admin export | 5 | 1 hour | 429 + `Retry-After` header |
| Password reset | 3 | 1 hour | 429 + `Retry-After` header |

**Implementation:** Redis-based sliding window counter with atomic increments

### 9d. Database Scaling

- **Connection pooling:** PgBouncer in transaction mode (max 100 connections per pool)
- **Read replicas:** Route read-heavy queries (transaction history, admin reports) to replicas
- **Partitioning:** Transaction table partitioned by month for efficient archival and query performance
- **Indexing strategy:** Composite indexes on `(card_id, created_at)`, `(user_id, created_at)`, `(type, created_at)`

---

## 10. Data Flow

### Recharge Flow

```
User → Select amount → Click "Pay with bKash"
  → Server creates pending transaction in DB
  → Server calls bKash API to create payment
  → bKash returns payment URL
  → User redirected to bKash
  → User completes payment on bKash
  → bKash calls our callback URL
  → Server verifies payment signature
  → Server updates transaction status to "completed"
  → Server updates card balance (atomic DB transaction)
  → Server invalidates Redis balance cache
  → Server publishes Redis pub/sub event
  → Server triggers SMS/email notification (async)
  → User redirected to success page with updated balance
```

### Sync Flow (Tap at Station Gate)

```
Station Gate → Detects card tap → Deducts fare locally
  → Gate sends POST /api/v1/sync/tap with { cardNumber, amount, timestamp, terminalId }
  → Server authenticates via API key
  → Server validates card exists and is linked
  → Server checks for duplicate (idempotency key)
  → Server processes balance update (atomic DB transaction)
  → Server records sync event in audit log
  → Server invalidates Redis balance cache
  → Server publishes Redis pub/sub event for real-time UI update
  → Server returns 200 OK to gate
```

### Batch Sync Flow (Offline Recovery)

```
Station Gate (reconnects) → Sends POST /api/v1/sync/batch with array of transactions
  → Server authenticates via API key
  → Server validates each transaction (card exists, not duplicate)
  → Server sorts by timestamp for correct ordering
  → Server processes in database transaction (all or nothing per batch)
  → Server records batch sync event
  → Server returns summary: { processed: N, skipped: M, errors: [...] }
```

---

## 11. Deployment Architecture

### Environment Strategy

| Environment | Purpose | Infrastructure |
|-------------|---------|---------------|
| **Development** | Local development | Docker Compose (PostgreSQL, Redis, Next.js) |
| **Staging** | Integration testing, UAT | AWS ECS (mirrors production, smaller instances) |
| **Production** | Live system | AWS ECS Fargate, RDS PostgreSQL (Multi-AZ), ElastiCache Redis (cluster mode) |

### Production Infrastructure

```
┌─────────────────────────────────────────────────────────────────┐
│                          AWS Region                              │
│  ┌─────────────┐                                                │
│  │  Route 53   │  DNS routing                                   │
│  └──────┬──────┘                                                │
│         │                                                       │
│  ┌──────▼──────┐                                                │
│  │ CloudFront  │  CDN + WAF                                     │
│  └──────┬──────┘                                                │
│         │                                                       │
│  ┌──────▼──────┐  ┌──────────────┐  ┌──────────────┐           │
│  │     ALB     │  │   WAF Rules  │  │  ACM (SSL)   │           │
│  └──────┬──────┘  └──────────────┘  └──────────────┘           │
│         │                                                       │
│  ┌──────▼──────────────────────────────────────────────┐        │
│  │                  ECS Cluster (Fargate)               │        │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │        │
│  │  │  Next.js   │  │  Next.js   │  │  Next.js   │    │        │
│  │  │  Task :1   │  │  Task :2   │  │  Task :N   │    │        │
│  │  └────────────┘  └────────────┘  └────────────┘    │        │
│  └──────────────────────┬──────────────────────────────┘        │
│                         │                                        │
│  ┌──────────────────────┼──────────────────────────────┐        │
│  │         VPC (Private Subnets)                       │        │
│  │  ┌──────────────┐  ┌──────────────┐                │        │
│  │  │ RDS PostgreSQL│  │ ElastiCache  │                │        │
│  │  │  (Multi-AZ)  │  │   Redis      │                │        │
│  │  └──────────────┘  └──────────────┘                │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   S3 Bucket  │  │  CloudWatch  │  │  Secrets     │          │
│  │  (exports)   │  │  (monitoring)│  │  Manager     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Pipeline

```
Developer → Push to feature branch
  → GitHub Actions triggered
  → Stage 1: Lint + Type Check
  → Stage 2: Unit Tests
  → Stage 3: Build
  → Stage 4: Integration Tests
  → On PR to main: E2E Tests (Playwright)
  → On merge to main: Deploy to staging
  → Manual approval → Deploy to production
  → Health check → Auto-rollback on failure
```

---

## 12. Monitoring & Observability

### Metrics

| Metric | Tool | Alert Threshold |
|--------|------|-----------------|
| API response time (p95) | CloudWatch / Grafana | > 500ms |
| Error rate (5xx) | CloudWatch | > 1% |
| Database connection pool usage | PgBouncer stats | > 80% |
| Redis memory usage | ElastiCache metrics | > 80% |
| Payment success rate | Custom metric | < 98% |
| Sync accuracy rate | Custom metric | < 99.5% |
| Active users | Analytics | — |
| Transaction volume | Custom metric | Anomaly detection |

### Logging

- **Structured JSON logs** via Winston
- **Log levels:** ERROR (production), WARN (staging), DEBUG (development)
- **Audit trail:** All financial operations logged to separate immutable audit table
- **Log aggregation:** ELK Stack (Elasticsearch, Logstash, Kibana)
- **Retention:** 90 days for application logs, 5 years for audit logs (NFR-012)

### Tracing

- **OpenTelemetry** SDK for distributed tracing
- **Trace context** propagated through all service calls
- **Key traces:** Payment flow, sync flow, authentication flow

---

## 13. Security Architecture

### Defense in Depth

| Layer | Controls |
|-------|----------|
| **Network** | VPC isolation, security groups, WAF rules, DDoS protection (AWS Shield) |
| **Application** | Input validation (Zod), CSRF protection, rate limiting, CORS restrictions |
| **Authentication** | JWT with rotation, bcrypt passwords, OTP verification, session timeout |
| **Authorization** | RBAC at middleware, service, and database levels |
| **Data** | AES-256 encryption at rest (RDS), TLS 1.3 in transit, no payment data stored |
| **Audit** | Immutable audit log, all admin actions logged, daily reconciliation |

### Specific Security Measures

- **CSRF Protection:** Double-submit cookie pattern for state-changing requests
- **CORS:** Strict origin whitelist (only DMTCL domains)
- **Content Security Policy:** Restrict script sources, prevent XSS
- **SQL Injection Prevention:** Prisma ORM (parameterized queries), no raw queries without sanitization
- **XSS Prevention:** React's built-in escaping, CSP headers, DOMPurify for any HTML content
- **Secrets Management:** AWS Secrets Manager for bKash API keys, database credentials, JWT signing keys
- **PCI-DSS Compliance:** No card/payment data stored; bKash handles all payment data
- **Bangladesh Bank Compliance:** Data residency in Bangladesh region (or approved jurisdiction), audit-ready logging

---

## 14. Internationalization (i18n)

- **Framework:** `next-intl` for Next.js App Router
- **Supported locales:** `en` (English), `bn` (Bengali)
- **Locale detection:** URL path prefix (`/en/`, `/bn/`) with cookie fallback
- **Translation files:** JSON files in `messages/en.json` and `messages/bn.json`
- **Server-side:** Locale resolved in middleware, passed to Server Components
- **Client-side:** `useTranslations` hook for client components
- **RTL support:** Not needed (Bengali is LTR)
- **Date/Number formatting:** Locale-aware via `Intl` API (BDT currency, Bengali numerals option)

---

## 15. Architecture Decision Records (ADR)

### ADR-001: Monolith Architecture Over Microservices

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** The system needs to handle financial transactions with strong consistency, serve 10K concurrent users, and launch within 6 months.

**Decision Drivers:**
- 6-month timeline constraint
- Small-to-medium team size
- Financial transaction integrity requirements
- Need for fast development iteration

**Considered Options:**
1. Monolith (Next.js full-stack) — single deployable unit
2. Microservices — separate services for auth, payment, sync, admin
3. Serverless — Lambda-based API with managed services

**Decision Outcome:**
**Chosen option:** Monolith (Next.js full-stack), because it provides the fastest path to launch while maintaining strong transaction consistency. The sync module can be extracted as a separate service later if it becomes a bottleneck.

**Consequences:**
- **Positive:** Faster development, simpler deployment, easier debugging, lower operational cost
- **Negative:** Vertical scaling limits, single deployment unit means all modules deploy together

---

### ADR-002: PostgreSQL as Primary Database

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** Financial system requiring ACID compliance, complex queries for reconciliation, and strong data integrity.

**Decision Drivers:**
- BRD C-006 mandates SQL-based RDBMS
- Financial transactions require ACID compliance
- Complex reporting and reconciliation queries
- PRD explicitly specifies PostgreSQL

**Considered Options:**
1. PostgreSQL — open-source, ACID, JSONB support, mature ecosystem
2. MySQL — widely used, but weaker JSON support
3. MongoDB — flexible schema but weaker transaction guarantees

**Decision Outcome:**
**Chosen option:** PostgreSQL, because it provides the strongest ACID guarantees, excellent JSONB support for flexible sync payloads, and mature tooling for financial applications.

---

### ADR-003: JWT Authentication with Refresh Token Rotation

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** Need secure, scalable authentication for web application with session management requirements.

**Decision Drivers:**
- Stateless auth for horizontal scaling
- Session timeout requirement (30 min inactivity, BR-010)
- Need for secure token revocation
- PRD specifies JWT-based auth

**Considered Options:**
1. JWT + Refresh Token Rotation — stateless access tokens, revocable refresh tokens
2. Session-based (server-side sessions) — simpler but harder to scale horizontally
3. NextAuth.js — full-featured but adds dependency complexity

**Decision Outcome:**
**Chosen option:** JWT with refresh token rotation stored in Redis, because it provides stateless access tokens for scalability while maintaining revocability through Redis-backed refresh tokens.

---

### ADR-004: Card Number Format Assumption

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #1 — exact card number format unknown.

**Decision:** Assume 16-digit numeric card number format (standard for transit cards). Validation: `/^\d{16}$/`. Format is configurable via environment variable for future changes.

**Consequence:** If DMTCL uses a different format, only the validation regex and environment variable need updating.

---

### ADR-005: Machine Sync Protocol Abstraction

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #2 — existing API for card reader integration unknown.

**Decision:** Design a protocol-agnostic sync API layer. The `/api/sync/tap` and `/api/sync/batch` endpoints accept a standardized JSON payload. An adapter layer translates between DMTCL's actual protocol and our internal format. This allows integration regardless of the existing protocol.

**Consequence:** Adapter layer adds initial development effort but provides flexibility for any protocol DMTCL uses.

---

### ADR-006: Recharge Cap Enforcement

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #4 — partial recharges when balance + recharge exceeds BDT 10,000 cap.

**Decision:** Reject recharges that would exceed the BDT 10,000 maximum card balance (BR-003). Display clear error: "Recharge would exceed maximum card balance of BDT 10,000. Current balance: X. Maximum allowed recharge: Y."

**Consequence:** Users must spend some balance before recharging large amounts. Simpler than partial recharge logic and prevents edge cases.

---

### ADR-007: Low Balance Alert Threshold

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #6 — configurable low-balance alerts.

**Decision:** Default threshold of BDT 20. User-configurable in profile settings (options: BDT 10, 20, 50, 100). Alert sent via SMS and in-app notification when balance drops below threshold.

---

### ADR-008: Disaster Recovery RTO/RPO

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #7 — RTO/RPO requirements not specified.

**Decision:**
- **RTO (Recovery Time Objective):** 1 hour — system must be restored within 1 hour of failure
- **RPO (Recovery Point Objective):** 15 minutes — maximum 15 minutes of data loss acceptable
- **Implementation:** RDS Multi-AZ with automated backups (5-min intervals), point-in-time recovery, cross-region backup replication

---

### ADR-009: Admin Role Sub-Division

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** PRD Open Question #8 — admin dashboard role-based views. BRD mentions "Admin, Operator, User" roles.

**Decision:** Split Admin into three sub-roles:
- **Admin (Super Admin):** Full access including balance adjustment
- **Finance Admin:** Reconciliation, reports, financial dashboards (maps to Nusrat persona)
- **Operations Admin:** User management, sync monitoring, support (maps to Mr. Hassan persona, replaces "Operator" from BRD)

**Consequence:** More granular access control aligns with organizational structure and reduces risk of unauthorized financial operations.

---

### ADR-010: Out-of-Order Sync Resolution

**Status:** Accepted  
**Date:** 2026-03-31  
**Deciders:** Solution Architect

**Context:** BRD FR-027 — system must resolve conflicts when sync data arrives out of order.

**Decision:** Use event-sourcing approach for balance calculation. Each transaction has a monotonically increasing sequence number from the terminal. Balance is calculated as: `initial_balance + sum(all_recharges) - sum(all_fare_deductions)`. The system maintains a running balance but recalculates from the transaction log when out-of-order events are detected. Online recharges take priority (BR-008).

---

## 16. Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| **bKash API downtime (R-001)** | Abstract payment layer with adapter pattern; implement retry with exponential backoff; queue failed payments for retry; maintain manual recharge fallback via admin |
| **Machine sync failures (R-002)** | Idempotent sync endpoints; batch retry mechanism; daily reconciliation job; user dispute process; alerting on sync failure rate |
| **Peak hour traffic (R-003)** | Auto-scaling ECS tasks; Redis caching for hot data; CDN for static assets; rate limiting; load testing before launch |
| **Fraudulent recharges (R-004)** | Transaction monitoring rules; velocity checks (max recharges per hour); bKash dispute integration; anomaly detection on balance changes |
| **Data breach (R-005)** | Encryption at rest and in transit; regular security audits; no payment data stored; principle of least privilege; WAF rules |
| **Legacy machine incompatibility (R-008)** | Protocol abstraction layer; early integration testing with DMTCL hardware team; mock sync API for development |

---

*End of Architecture Document*
