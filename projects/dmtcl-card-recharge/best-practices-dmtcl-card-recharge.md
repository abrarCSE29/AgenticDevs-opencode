# Best Practices Guide — DMTCL Online Card Recharge System

**Project Name:** DMTCL Online Card Recharge System  
**Document Version:** 1.0  
**Last Updated:** March 31, 2026  
**Prepared By:** Solution Architect  
**Status:** Draft  
**Related Documents:**  
- [Architecture Document](architecture-dmtcl-card-recharge.md)  
- [Database Design](database-dmtcl-card-recharge.md)  
- [BRD](brd-dmtcl-card-recharge.md)  
- [PRD](prd-dmtcl-card-recharge.md)

---

## Table of Contents

1. [Code Organization](#1-code-organization)
2. [TypeScript Standards](#2-typescript-standards)
3. [React/Next.js Standards](#3-reactnextjs-standards)
4. [API Development Standards](#4-api-development-standards)
5. [Database & Prisma Best Practices](#5-database--prisma-best-practices)
6. [Caching Implementation Guidelines](#6-caching-implementation-guidelines)
7. [RBAC Implementation Guidelines](#7-rbac-implementation-guidelines)
8. [Security Best Practices](#8-security-best-practices)
9. [Payment Integration Best Practices](#9-payment-integration-best-practices)
10. [Sync API Best Practices](#10-sync-api-best-practices)
11. [Testing Strategy](#11-testing-strategy)
12. [Performance Optimization](#12-performance-optimization)
13. [Error Handling](#13-error-handling)
14. [Logging & Monitoring](#14-logging--monitoring)
15. [Internationalization (i18n)](#15-internationalization-i18n)
16. [CI/CD Pipeline](#16-cicd-pipeline)
17. [Code Review Checklist](#17-code-review-checklist)

---

## 1. Code Organization

### Project Structure

```
dmtcl-card-recharge/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (auth)/                   # Auth route group
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── forgot-password/
│   │   │   └── reset-password/
│   │   ├── (dashboard)/              # Authenticated route group
│   │   │   ├── dashboard/
│   │   │   ├── cards/
│   │   │   ├── recharge/
│   │   │   ├── transactions/
│   │   │   └── profile/
│   │   ├── (admin)/                  # Admin route group
│   │   │   ├── dashboard/
│   │   │   ├── users/
│   │   │   ├── transactions/
│   │   │   ├── reconciliation/
│   │   │   └── settings/
│   │   ├── api/                      # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth/
│   │   │   │   ├── cards/
│   │   │   │   ├── payments/
│   │   │   │   ├── sync/
│   │   │   │   ├── transactions/
│   │   │   │   └── admin/
│   │   │   └── health/
│   │   ├── layout.tsx
│   │   ├── page.tsx                  # Landing page
│   │   └── not-found.tsx
│   ├── components/
│   │   ├── ui/                       # Primitive UI (Button, Input, Card, Modal)
│   │   ├── forms/                    # Form components (LoginForm, RegisterForm)
│   │   ├── features/                 # Feature-specific components
│   │   │   ├── card-linker/
│   │   │   ├── recharge-form/
│   │   │   ├── transaction-table/
│   │   │   └── balance-display/
│   │   └── layout/                   # Layout components (Header, Sidebar, Footer)
│   ├── lib/
│   │   ├── db.ts                     # Prisma client singleton
│   │   ├── redis.ts                  # Redis client singleton
│   │   ├── auth.ts                   # JWT utilities
│   │   ├── bkash.ts                  # bKash API client
│   │   ├── sms.ts                    # SMS gateway client
│   │   ├── email.ts                  # Email service client
│   │   ├── validation.ts             # Zod schemas
│   │   └── utils.ts                  # Shared utilities
│   ├── services/                     # Business logic layer
│   │   ├── auth.service.ts
│   │   ├── card.service.ts
│   │   ├── payment.service.ts
│   │   ├── sync.service.ts
│   │   ├── transaction.service.ts
│   │   ├── admin.service.ts
│   │   └── notification.service.ts
│   ├── middleware/                   # API middleware
│   │   ├── auth.middleware.ts
│   │   ├── rbac.middleware.ts
│   │   ├── rate-limit.middleware.ts
│   │   └── validation.middleware.ts
│   ├── hooks/                        # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useBalance.ts
│   │   ├── useTransactions.ts
│   │   └── useRole.ts
│   ├── types/                        # TypeScript type definitions
│   │   ├── user.ts
│   │   ├── card.ts
│   │   ├── transaction.ts
│   │   ├── payment.ts
│   │   └── api.ts
│   ├── constants/                    # App-wide constants
│   │   ├── limits.ts                 # Recharge limits, card limits
│   │   ├── roles.ts                  # Role definitions
│   │   └── routes.ts                 # Route constants
│   └── i18n/                         # Internationalization
│       ├── request.ts
│       ├── routing.ts
│       └── messages/
│           ├── en.json
│           └── bn.json
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── public/
├── .env.example
├── next.config.ts
├── tsconfig.json
└── package.json
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `BalanceDisplay.tsx`, `CardLinker.tsx` |
| Hooks | camelCase with `use` prefix | `useAuth.ts`, `useBalance.ts` |
| Services | camelCase with `.service.ts` suffix | `payment.service.ts` |
| API routes | kebab-case directories | `/api/v1/payments/` |
| Utilities | camelCase | `formatCurrency.ts` |
| Constants | UPPER_SNAKE_CASE | `MAX_RECHARGE_AMOUNT` |
| Types/Interfaces | PascalCase | `interface TransactionRecord` |
| Zod schemas | camelCase with `Schema` suffix | `rechargeAmountSchema` |

---

## 2. TypeScript Standards

### Strict Mode

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

### Rules

- **Never use `any`** — use `unknown` and narrow with type guards
- **Use `interface` for object shapes**, `type` for unions/intersections
- **Prefer `readonly`** for immutable properties
- **Use discriminated unions** for API response states:
  ```typescript
  type ApiResult<T> =
    | { success: true; data: T }
    | { success: false; error: ApiError };
  ```
- **Use branded types** for monetary values to prevent mixing currencies:
  ```typescript
  type BDT = number & { readonly __brand: 'BDT' };
  ```
- **Infer types from Zod schemas** — single source of truth:
  ```typescript
  const userSchema = z.object({ phone: z.string(), email: z.string().email() });
  type User = z.infer<typeof userSchema>;
  ```

---

## 3. React/Next.js Standards

### Server Components by Default

- All page components are Server Components unless they need interactivity
- Use `"use client"` directive only when needed (event handlers, hooks, state)
- Fetch data in Server Components, pass as props to Client Components

### Component Guidelines

- Keep components under **150 lines** — extract logic to hooks or sub-components
- Co-locate related files: `Component.tsx`, `Component.test.tsx`, `Component.module.css`
- Use **React Server Components** for data fetching
- Use **Server Actions** for form submissions and mutations (preferred over API routes for form handling)

### State Management

- **Server state:** React Server Components + Server Actions
- **Client state:** `useState` / `useReducer` for local state
- **Global client state:** React Context for auth state, theme
- **Data fetching:** SWR or TanStack Query for client-side caching of API data
- **Avoid:** Redux, Zustand (overkill for this project scope)

### Form Handling

- Use **React Hook Form** + **Zod** for form validation
- Server-side validation is mandatory — client validation is UX enhancement only
- Use Server Actions for form submissions with progressive enhancement

---

## 4. API Development Standards

### Request/Response Format

**Success Response:**
```json
{
  "success": true,
  "data": { "balance": 300.00, "cardNumber": "****1234" },
  "meta": { "timestamp": "2026-03-31T10:00:00Z" },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Card balance is insufficient for this transaction",
    "details": { "currentBalance": 30.00, "requiredAmount": 50.00 }
  }
}
```

### Validation

- **All API inputs validated with Zod** before processing
- Validate at the API route level, not just in services
- Use Zod's `.refine()` for cross-field validation
- Return structured validation errors:
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input",
      "details": [
        { "field": "amount", "message": "Must be between 50 and 5000" }
      ]
    }
  }
  ```

### Pagination

- **Cursor-based pagination** for transaction history (large datasets)
- **Offset-based pagination** for admin user lists (smaller datasets)
- Default page size: 20, max page size: 100
- Include pagination metadata in response:
  ```json
  {
    "meta": {
      "page": 1,
      "pageSize": 20,
      "total": 150,
      "hasNext": true,
      "cursor": "eyJpZCI6MTUwfQ=="
    }
  }
  ```

---

## 5. Database & Prisma Best Practices

### Prisma Client Singleton

```typescript
// src/lib/db.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma = globalForPrisma.prisma || new PrismaClient({
  log: process.env.NODE_ENV === 'development'
    ? ['query', 'error', 'warn']
    : ['error'],
});

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### Query Guidelines

- **Always use transactions** for multi-step financial operations:
  ```typescript
  await prisma.$transaction(async (tx) => {
    const payment = await tx.paymentSession.update({ ... });
    const card = await tx.card.update({ ... });
    const transaction = await tx.transaction.create({ ... });
    return { payment, card, transaction };
  });
  ```
- **Avoid N+1 queries** — use `include` or `select` for related data
- **Use `select` over `include`** when you don't need all fields
- **Never expose sensitive fields** (password hash, tokens) in API responses
- **Use raw SQL sparingly** — only for complex aggregation queries that Prisma can't express

### Migration Guidelines

- Always test migrations on staging before production
- Use `prisma migrate dev` for development, `prisma migrate deploy` for production
- For zero-downtime migrations: add columns as nullable first, backfill, then add constraints
- Keep migration files small and focused — one logical change per migration

---

## 6. Caching Implementation Guidelines

### Redis Client Singleton

```typescript
// src/lib/redis.ts
import Redis from 'ioredis';

const globalForRedis = globalThis as unknown as { redis: Redis };

export const redis = globalForRedis.redis || new Redis({
  host: process.env.REDIS_HOST,
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD,
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000),
});

if (process.env.NODE_ENV !== 'production') globalForRedis.redis = redis;
```

### Cache Patterns

**Cache-Aside (Read-Through):**
```typescript
async function getCardBalance(cardId: string): Promise<number> {
  const cached = await redis.get(`balance:${cardId}`);
  if (cached) return parseFloat(cached);

  const card = await prisma.card.findUnique({ where: { id: cardId } });
  if (!card) throw new Error('Card not found');

  await redis.setex(`balance:${cardId}`, 30, card.balance.toString());
  return card.balance;
}
```

**Write-Through with Invalidation:**
```typescript
async function updateBalanceAfterRecharge(cardId: string, amount: number) {
  await prisma.$transaction(async (tx) => {
    const card = await tx.card.update({
      where: { id: cardId },
      data: { balance: { increment: amount } },
    });
    await tx.transaction.create({ /* ... */ });
  });

  // Invalidate cache
  await redis.del(`balance:${cardId}`);
  await redis.del(`dashboard:${card.userId}`);

  // Notify connected clients
  await redis.publish(`balance_updates:${cardId}`, JSON.stringify({
    cardId, newBalance: card.balance,
  }));
}
```

### Rate Limiting with Redis

```typescript
async function checkRateLimit(key: string, limit: number, window: number): Promise<boolean> {
  const current = await redis.incr(key);
  if (current === 1) await redis.expire(key, window);
  return current <= limit;
}
```

### Cache Key Naming Convention

```
session:{refreshTokenHash}     — Refresh token storage
balance:{cardId}               — Card balance cache
dashboard:{userId}             — User dashboard data
txlist:{userId}:{cursor}       — Paginated transaction list
admin:dashboard                — Admin dashboard aggregates
ratelimit:auth:{ip}            — Auth rate limit counter
ratelimit:api:{userId}         — API rate limit counter
config:{key}                   — System configuration
payment:{paymentId}            — bKash payment session state
```

---

## 7. RBAC Implementation Guidelines

### Middleware-Based Route Protection

```typescript
// src/middleware.ts (Next.js middleware)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { verifyJwt } from '@/lib/auth';
import { ROLE_PERMISSIONS } from '@/constants/roles';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  if (!token) return NextResponse.redirect(new URL('/login', request.url));

  const payload = verifyJwt(token);
  if (!payload) return NextResponse.redirect(new URL('/login', request.url));

  const pathname = request.nextUrl.pathname;
  const requiredRole = getRequiredRole(pathname);

  if (!hasPermission(payload.role, requiredRole)) {
    return NextResponse.json(
      { error: { code: 'FORBIDDEN', message: 'Access denied' } },
      { status: 403 }
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*', '/api/:path*'],
};
```

### Role Guard Component

```typescript
// src/components/features/RoleGuard.tsx
import { useRole } from '@/hooks/useRole';

interface RoleGuardProps {
  allowedRoles: string[];
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function RoleGuard({ allowedRoles, children, fallback = null }: RoleGuardProps) {
  const { role } = useRole();
  if (!allowedRoles.includes(role)) return <>{fallback}</>;
  return <>{children}</>;
}
```

### Service-Level Permission Check

```typescript
// In service layer — always verify resource ownership
async function getUserTransactions(userId: string, userRole: string) {
  if (userRole === 'admin' || userRole === 'finance_admin') {
    return prisma.transaction.findMany({ /* all transactions */ });
  }
  // Regular users can only see their own transactions
  return prisma.transaction.findMany({
    where: { card: { userId } },
  });
}
```

### Role Constants

```typescript
// src/constants/roles.ts
export const ROLES = {
  ADMIN: 'admin',
  FINANCE_ADMIN: 'finance_admin',
  OPERATIONS_ADMIN: 'operations_admin',
  USER: 'user',
  GUEST: 'guest',
} as const;

export const ROLE_HIERARCHY: Record<string, number> = {
  admin: 5,
  finance_admin: 4,
  operations_admin: 3,
  user: 2,
  guest: 1,
};

export function hasPermission(userRole: string, requiredRole: string): boolean {
  return (ROLE_HIERARCHY[userRole] ?? 0) >= (ROLE_HIERARCHY[requiredRole] ?? 0);
}
```

---

## 8. Security Best Practices

### OWASP Top 10 Coverage

| Threat | Mitigation |
|--------|-----------|
| **Injection** | Prisma ORM (parameterized queries), Zod validation, no raw SQL without sanitization |
| **Broken Authentication** | JWT with rotation, bcrypt (cost 12+), OTP verification, session timeout |
| **Sensitive Data Exposure** | TLS 1.3 everywhere, AES-256 at rest, no payment data stored, HttpOnly cookies |
| **Broken Access Control** | RBAC at middleware, service, and DB levels; deny by default |
| **Security Misconfiguration** | No debug in production, remove default credentials, security headers |
| **XSS** | React's built-in escaping, CSP headers, DOMPurify for HTML content |
| **CSRF** | Double-submit cookie pattern, SameSite=Strict cookies |
| **Insecure Deserialization** | Zod schema validation on all inputs |
| **Known Vulnerabilities** | `npm audit` in CI, Dependabot, regular dependency updates |
| **Insufficient Logging** | Structured JSON logs, audit trail for all financial operations |

### Security Headers (Next.js)

```typescript
// next.config.ts
const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-XSS-Protection', value: '1; mode=block' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://*.bkash.com; frame-ancestors 'none';",
  },
  { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
];
```

### Secrets Management

- **Never commit secrets** — use `.env.local` (gitignored)
- **Production secrets:** AWS Secrets Manager
- **Required environment variables:**
  ```
  DATABASE_URL=
  REDIS_HOST=
  REDIS_PASSWORD=
  JWT_PRIVATE_KEY=
  JWT_PUBLIC_KEY=
  BKASH_APP_KEY=
  BKASH_APP_SECRET=
  BKASH_BASE_URL=
  SMS_API_KEY=
  EMAIL_API_KEY=
  NEXT_PUBLIC_APP_URL=
  ```

---

## 9. Payment Integration Best Practices

### bKash Integration Pattern

```typescript
// src/lib/bkash.ts
class BkashClient {
  private accessToken: string | null = null;
  private tokenExpiry: number = 0;

  private async getAuthToken(): Promise<string> {
    if (this.accessToken && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }
    // Request new token from bKash
    const response = await fetch(`${process.env.BKASH_BASE_URL}/tokenized/checkout/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        username: process.env.BKASH_APP_KEY!,
        password: process.env.BKASH_APP_SECRET!,
      },
    });
    const data = await response.json();
    this.accessToken = data.id_token;
    this.tokenExpiry = Date.now() + (data.expires_in - 60) * 1000; // 60s buffer
    return this.accessToken!;
  }

  async createPayment(params: CreatePaymentParams): Promise<BkashPaymentResponse> {
    const token = await this.getAuthToken();
    // ... create payment
  }

  async executePayment(paymentID: string): Promise<BkashExecuteResponse> {
    const token = await this.getAuthToken();
    // ... execute payment
  }
}
```

### Payment Flow Safety

1. **Always create a pending transaction record** before redirecting to bKash
2. **Use idempotency keys** for payment creation
3. **Verify bKash callback signature** — never trust callback data without verification
4. **Implement retry logic** for callback verification (bKash may retry callbacks)
5. **Handle partial failures:** If bKash charges but our system fails to update balance, implement a reconciliation job
6. **Log all payment events** with full request/response for audit trail
7. **Never store bKash credentials** in client-side code

### Payment State Machine

```
PENDING → INITIATED → PROCESSING → COMPLETED
                              → FAILED
                              → CANCELLED
                              → REFUNDED
```

---

## 10. Sync API Best Practices

### Idempotency

- Every sync request must include an **idempotency key** (combination of `terminalId + transactionSequenceNumber`)
- Check for duplicate before processing:
  ```typescript
  const existing = await prisma.syncEvent.findUnique({
    where: { idempotencyKey: `${terminalId}-${sequenceNumber}` },
  });
  if (existing) return { status: 'duplicate', existingTransaction: existing };
  ```

### Out-of-Order Resolution

- Each terminal transaction has a **monotonically increasing sequence number**
- Store all transactions in the `transactions` table with their original timestamp
- Calculate balance from the transaction log, not from a running total
- When batch sync arrives, sort by terminal timestamp before processing

### Batch Processing

- Process batches in a **single database transaction** per batch
- Return detailed results: `{ processed: N, skipped: M, errors: [...] }`
- Use Redis Streams for async batch processing if batches are large (>1000 transactions)
- Implement exponential backoff retry for failed batches

### API Key Authentication for Sync Endpoints

- Sync endpoints use **API key authentication** (not JWT)
- API keys are scoped to specific terminals/stations
- Rotate API keys periodically
- Log all sync requests with terminal ID and IP address

---

## 11. Testing Strategy

### Test Pyramid

```
         /  E2E  \          ~10% — Critical user flows
        /----------\
       / Integration \      ~30% — API endpoints, service layer
      /--------------\
     /    Unit Tests   \    ~60% — Functions, hooks, utilities, validators
    /__________________\
```

### Coverage Targets

| Layer | Target | Tool |
|-------|--------|------|
| Unit | 80%+ | Vitest |
| Integration | All API endpoints | Vitest + Supertest |
| E2E | Critical user journeys | Playwright |

### Critical E2E Test Scenarios

1. **User registration → card linking → recharge → balance update**
2. **Failed payment → no balance change → retry**
3. **Card tap sync → balance deduction → transaction history**
4. **Admin login → view transactions → reconciliation report**
5. **OTP login flow**
6. **Password reset flow**
7. **Rate limiting on auth endpoints**
8. **RBAC enforcement (user cannot access admin routes)**

### Test Data

- Use **seed scripts** for test data
- **Never use production data** in tests
- Mock external services (bKash, SMS, Email) with test doubles
- Use **factory functions** for creating test entities

### Mocking External Services

```typescript
// tests/mocks/bkash.mock.ts
export const mockBkashClient = {
  createPayment: vi.fn().mockResolvedValue({ paymentID: 'test-payment-123', paymentURL: 'https://mock.bkash.com/pay' }),
  executePayment: vi.fn().mockResolvedValue({ status: 'completed', amount: 200, trxID: 'TRX123' }),
};
```

---

## 12. Performance Optimization

### Frontend

- **Next.js Image component** for all images (automatic optimization, WebP conversion)
- **Lazy loading** for below-the-fold content (`loading="lazy"`)
- **Code splitting** via dynamic imports for heavy components:
  ```typescript
  const TransactionChart = dynamic(() => import('./TransactionChart'), {
    loading: () => <Skeleton />,
    ssr: false,
  });
  ```
- **Bundle analysis:** Run `@next/bundle-analyzer` periodically
- **Virtual scrolling** for transaction history tables with many rows (`@tanstack/react-virtual`)
- **Optimistic updates** for balance display after recharge (revert on failure)

### Backend

- **Database connection pooling** via PgBouncer (transaction mode)
- **Redis caching** for frequently accessed data (balance, dashboard)
- **Cursor-based pagination** for transaction history
- **Database indexes** on all foreign keys and frequently queried columns
- **Avoid N+1 queries** — use Prisma `include`/`select`
- **Debounce** rapid balance queries from the UI

### Database

- **Composite indexes** for common query patterns:
  - `(card_id, created_at DESC)` — transaction history per card
  - `(user_id, created_at DESC)` — user's transactions
  - `(type, created_at DESC)` — filtered transaction types
- **Partial indexes** for active records:
  - `CREATE INDEX idx_cards_active ON cards(user_id) WHERE deleted_at IS NULL;`
- **Monitor slow queries** — log queries > 100ms
- **Use EXPLAIN ANALYZE** for complex queries

---

## 13. Error Handling

### Error Classification

```typescript
// src/types/api.ts
export class AppError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AppError';
  }
}

// Specific error types
export class ValidationError extends AppError { /* 400 */ }
export class AuthenticationError extends AppError { /* 401 */ }
export class AuthorizationError extends AppError { /* 403 */ }
export class NotFoundError extends AppError { /* 404 */ }
export class PaymentError extends AppError { /* 402 */ }
export class RateLimitError extends AppError { /* 429 */ }
export class InternalError extends AppError { /* 500 */ }
```

### Global Error Handler

```typescript
// src/app/api/v1/[...route]/handler.ts
export async function errorHandler(error: unknown): Promise<Response> {
  if (error instanceof AppError) {
    return Response.json(
      { success: false, error: { code: error.code, message: error.message, details: error.details } },
      { status: error.statusCode }
    );
  }

  // Unexpected error — log and return generic message
  logger.error('Unhandled error', { error });
  return Response.json(
    { success: false, error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' } },
    { status: 500 }
  );
}
```

### User-Facing Error Messages

- **Never expose stack traces or internal details** to users
- Use user-friendly messages in Bengali and English
- Provide actionable guidance: "Payment failed. Please check your bKash balance and try again."
- Log full error details server-side for debugging

---

## 14. Logging & Monitoring

### Structured Logging

```typescript
// src/lib/logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'dmtcl-card-recharge' },
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/audit.log', level: 'info' }),
  ],
});
```

### Audit Logging

All financial and admin operations must be logged to the `audit_log` table:

```typescript
async function logAudit(action: string, userId: string, details: Record<string, unknown>) {
  await prisma.auditLog.create({
    data: {
      action,
      userId,
      details,
      ipAddress: getRequestIp(),
      userAgent: getRequestUserAgent(),
    },
  });
}
```

### Monitoring Alerts

| Alert | Threshold | Action |
|-------|-----------|--------|
| API error rate | > 1% over 5 min | Page on-call engineer |
| Payment failure rate | > 5% over 15 min | Alert payments team |
| Sync failure rate | > 2% over 10 min | Alert operations team |
| Response time p95 | > 500ms | Investigate, scale if needed |
| Database connections | > 80% pool | Scale up or optimize queries |
| Redis memory | > 80% | Scale up or review cache TTLs |

---

## 15. Internationalization (i18n)

### Translation File Structure

```json
// src/i18n/messages/en.json
{
  "dashboard": {
    "title": "My Dashboard",
    "balance": "Current Balance",
    "recharge": "Recharge Card",
    "lowBalance": "Your balance is low. Consider recharging.",
    "recentTransactions": "Recent Transactions"
  },
  "recharge": {
    "title": "Recharge Card",
    "selectAmount": "Select Amount",
    "customAmount": "Enter Custom Amount",
    "minAmount": "Minimum recharge amount is BDT 50",
    "maxAmount": "Maximum recharge amount is BDT 5,000",
    "payWithBkash": "Pay with bKash",
    "processing": "Processing payment..."
  },
  "errors": {
    "insufficientBalance": "Insufficient balance",
    "paymentFailed": "Payment failed. Please try again.",
    "cardAlreadyLinked": "This card is already linked to another account",
    "maxCardsReached": "Maximum 5 cards allowed per account"
  }
}
```

### Usage in Components

```typescript
// Server Component
import { getTranslations } from 'next-intl/server';

export default async function DashboardPage() {
  const t = await getTranslations('dashboard');
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('balance')}: {balance} BDT</p>
    </div>
  );
}

// Client Component
import { useTranslations } from 'next-intl';

export function RechargeForm() {
  const t = useTranslations('recharge');
  return <button>{t('payWithBkash')}</button>;
}
```

### Bengali-Specific Considerations

- Use **Bengali numerals** option in number formatting (`Intl.NumberFormat('bn-BD')`)
- Ensure fonts support Bengali script (Noto Sans Bengali)
- Test all UI components with Bengali text (longer strings may break layouts)
- Date formatting: Bengali calendar dates where appropriate

---

## 16. CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck

  unit-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run test:unit

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test }
        ports: ['5432:5432']
      redis:
        image: redis:7
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx prisma migrate deploy
      - run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request' && github.base_ref == 'main'
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e

  build:
    runs-on: ubuntu-latest
    needs: [lint-and-typecheck, unit-tests]
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [build, integration-tests]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: # Deploy to staging (ECS)

  deploy-production:
    runs-on: ubuntu-latest
    needs: [deploy-staging]
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4
      - run: # Deploy to production (ECS)
```

---

## 17. Code Review Checklist

### Before Submitting PR

- [ ] Code follows naming conventions and project structure
- [ ] TypeScript strict mode compliance (no `any`, no unchecked indexed access)
- [ ] Input validation with Zod on all API endpoints
- [ ] Error handling with appropriate user feedback (i18n messages)
- [ ] Unit tests added for new business logic
- [ ] No hardcoded values — use constants or environment variables
- [ ] Performance considered (no N+1 queries, proper caching)
- [ ] Security implications reviewed (auth, RBAC, input sanitization)
- [ ] Database migrations included if schema changed
- [ ] Audit logging for financial/admin operations
- [ ] Accessibility basics (alt text, keyboard navigation, ARIA labels)
- [ ] Bengali translations added for new user-facing strings
- [ ] No secrets or sensitive data in code or logs
- [ ] Rate limiting applied to new endpoints
- [ ] Idempotency for payment and sync operations

---

*End of Best Practices Guide*
