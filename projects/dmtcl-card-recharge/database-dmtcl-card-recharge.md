# DMTCL Online Card Recharge System — Database Architecture

**Database**: PostgreSQL 16+  
**ORM**: Prisma  
**Last Updated**: 2026-03-31  
**Related Docs**: BRD, PRD, Architecture (Dhaka Mass Transit Company Limited)

---

## Table of Contents

1. [Database Overview](#1-database-overview)
2. [Entity Relationship Diagram](#2-entity-relationship-diagram)
3. [Table Definitions](#3-table-definitions)
4. [Indexing Strategy](#4-indexing-strategy)
5. [Partitioning Strategy](#5-partitioning-strategy)
6. [Constraints & Business Rules Enforcement](#6-constraints--business-rules-enforcement)
7. [Data Retention & Archival](#7-data-retention--archival)
8. [Security at Database Level](#8-security-at-database-level)
9. [Performance Considerations](#9-performance-considerations)
10. [Migration Strategy](#10-migration-strategy)
11. [Sample Prisma Schema](#11-sample-prisma-schema)

---

## 1. Database Overview

### 1.1 Database Configuration

| Setting | Value | Justification |
|---------|-------|---------------|
| **Engine** | PostgreSQL 16+ | ACID compliance, native partitioning, JSONB, RLS, mature ecosystem |
| **Character Set** | UTF-8 | Required for Bengali (বাংলা) language support |
| **Collation** | `en_US.UTF-8` | Standard English collation; Bengali text stored as UTF-8 strings |
| **Timezone** | `Asia/Dhaka` (UTC+6) | All timestamps stored as `TIMESTAMPTZ` (UTC internally), displayed in local TZ |
| **Default Schema** | `public` | Single-schema monolith; logical separation via table prefixes if needed |
| **Primary Key Type** | UUID v7 (`gen_random_uuid()`) | Distributed-safe, time-ordered for better index locality than UUID v4 |

### 1.2 Connection Pooling (PgBouncer)

| Setting | Value | Justification |
|---------|-------|---------------|
| **Pool Mode** | Transaction | Optimal for Next.js/Prisma; connections released after each transaction |
| **Default Pool Size** | 50 | Supports 10,000 concurrent users with ~200 active DB connections at peak |
| **Max Pool Size** | 100 | Burst capacity for peak hours (morning/evening commute) |
| **Min Pool Size** | 10 | Warm connections for baseline traffic |
| **Pool Timeout** | 30s | Matches session timeout; prevents indefinite queuing |
| **Idle Timeout** | 600s (10 min) | Releases idle connections during off-peak hours |
| **Server Lifetime** | 3600s (1 hr) | Periodic connection recycling to prevent memory leaks |
| **Max Client Connections** | 500 | Caps application-side connection attempts |
| **Max DB Connections** | 200 | PostgreSQL `max_connections` set to 250 (reserve 50 for superuser/maintenance) |

**Architecture**:
```
Next.js App (Prisma) ──▶ PgBouncer (Transaction Mode) ──▶ PostgreSQL Primary (RDS)
                                                          └──▶ Read Replica 1 (async)
                                                          └──▶ Read Replica 2 (async, sync queries)
```

### 1.3 Schema Organization

Single `public` schema with logical grouping by domain:

| Domain | Tables | Purpose |
|--------|--------|---------|
| **Identity** | `users`, `user_roles`, `sessions` | Authentication, authorization, session management |
| **Cards** | `cards` | Transit card registry and linking |
| **Payments** | `transactions`, `payment_sessions`, `balance_adjustments` | Financial operations |
| **Sync** | `sync_events`, `sync_batches` | Machine-to-system data synchronization |
| **Audit** | `audit_log` | Immutable operation trail |
| **Notifications** | `notifications` | SMS/email delivery tracking |
| **System** | `config` | Runtime configuration |

---

## 2. Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐
│     users       │       │    user_roles     │
│─────────────────│       │──────────────────│
│ id (PK)         │──┐    │ id (PK)          │
│ phone           │  │    │ user_id (FK)     │◀──┐
│ email           │  │    │ role             │   │
│ password_hash   │  │    │ granted_by (FK)  │   │
│ status          │  │    │ granted_at       │   │
│ deleted_at      │  │    └──────────────────┘   │
│ created_at      │  │                           │
│ updated_at      │  │    ┌──────────────────┐   │
└────────┬────────┘  │    │     users        │   │
         │           │    │──────────────────│   │
         │ 1         │    │ id (PK)     ◀────┘   │
         │           │    └──────────────────┘
         │ N
         ▼
┌─────────────────┐
│     cards       │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │──┐
│ card_number     │  │  (16-digit, unique)
│ card_status     │  │
│ balance         │  │  (NUMERIC 12,2)
│ last_sync_seq   │  │  (sequence number for sync)
│ deleted_at      │  │
│ created_at      │  │
│ updated_at      │  │
└────────┬────────┘  │
         │           │
         │ 1         │
         │           │
         ▼           │
┌─────────────────┐  │
│  transactions   │  │  (PARTITIONED BY MONTH)
│─────────────────│  │
│ id (PK)         │  │
│ card_id (FK)    │◀─┘
│ user_id (FK)    │──┐
│ type            │  │
│ amount          │  │
│ balance_before  │  │
│ balance_after   │  │
│ status          │  │
│ reference       │  │
│ idempotency_key │  │
│ created_at      │  │
│ updated_at      │  │
└────────┬────────┘  │
         │           │
         │ N         │
         │           │
         ▼           │
┌─────────────────┐  │
│payment_sessions │  │
│─────────────────│  │
│ id (PK)         │  │
│ card_id (FK)    │◀─┘
│ user_id (FK)    │
│ bkash_payment_id│
│ amount          │
│ status          │
│ idempotency_key │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌─────────────────┐       ┌──────────────────┐
│  sync_batches   │       │   sync_events    │
│─────────────────│       │──────────────────│
│ id (PK)         │       │ id (PK)          │
│ terminal_id     │       │ batch_id (FK)    │──▶ sync_batches
│ terminal_type   │       │ card_id (FK)     │
│ batch_status    │       │ event_type       │
│ total_events    │       │ sequence_number  │  (out-of-order
│ processed_count │       │ balance_delta    │   resolution)
│ created_at      │       │ raw_payload      │  (JSONB)
│ updated_at      │       │ idempotency_key  │
└─────────────────┘       │ created_at       │
                          └──────────────────┘

┌──────────────────────┐
│ balance_adjustments  │
│──────────────────────│
│ id (PK)              │
│ card_id (FK)         │
│ user_id (FK)         │
│ amount               │
│ reason               │
│ requested_by (FK)    │──▶ users (Operations Admin)
│ approved_by_1 (FK)   │──▶ users (Finance Admin)
│ approved_by_2 (FK)   │──▶ users (Finance Admin, different)
│ approval_status      │
│ created_at           │
│ updated_at           │
└──────────────────────┘

┌─────────────────┐       ┌──────────────────┐
│    audit_log    │       │  notifications   │
│─────────────────│       │──────────────────│
│ id (PK)         │       │ id (PK)          │
│ actor_id (FK)   │       │ user_id (FK)     │
│ action          │       │ card_id (FK)     │
│ entity_type     │       │ type             │
│ entity_id       │       │ channel          │
│ old_values      │       │ recipient        │
│ new_values      │       │ template         │
│ ip_address      │       │ status           │
│ user_agent      │       │ sent_at          │
│ created_at      │       │ created_at       │
└─────────────────┘       └──────────────────┘

┌─────────────────┐
│    sessions     │
│─────────────────│
│ id (PK)         │
│ user_id (FK)    │
│ token_hash      │
│ expires_at      │
│ ip_address      │
│ user_agent      │
│ created_at      │
│ last_active_at  │
└─────────────────┘

┌─────────────────┐
│     config      │
│─────────────────│
│ id (PK)         │
│ key (UNIQUE)    │
│ value (JSONB)   │
│ description     │
│ updated_by (FK) │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### Relationship Summary

| Parent | Child | Cardinality | Constraint |
|--------|-------|-------------|------------|
| `users` | `user_roles` | 1:N | CASCADE delete |
| `users` | `cards` | 1:N | SET NULL on delete (soft delete) |
| `users` | `transactions` | 1:N | SET NULL on delete |
| `users` | `payment_sessions` | 1:N | SET NULL on delete |
| `users` | `balance_adjustments` | 1:N | SET NULL on delete |
| `users` | `audit_log` | 1:N | SET NULL on delete |
| `users` | `notifications` | 1:N | SET NULL on delete |
| `users` | `sessions` | 1:N | CASCADE delete |
| `cards` | `transactions` | 1:N | SET NULL on delete |
| `cards` | `payment_sessions` | 1:N | SET NULL on delete |
| `cards` | `sync_events` | 1:N | SET NULL on delete |
| `cards` | `balance_adjustments` | 1:N | SET NULL on delete |
| `cards` | `notifications` | 1:N | SET NULL on delete |
| `sync_batches` | `sync_events` | 1:N | CASCADE delete |

---

## 3. Table Definitions

### 3.1 `users` — User Accounts

**Purpose**: Stores registered user accounts with phone/email authentication.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | UUID v7 for time-ordering |
| `phone` | `VARCHAR(15)` | UNIQUE, NOT NULL | — | Bangladeshi phone (+880XXXXXXXXXX) |
| `email` | `VARCHAR(255)` | UNIQUE | NULL | Optional email address |
| `password_hash` | `VARCHAR(255)` | NOT NULL | — | bcrypt, cost factor ≥ 12 |
| `full_name_bn` | `VARCHAR(100)` | — | NULL | Bengali name |
| `full_name_en` | `VARCHAR(100)` | — | NULL | English name |
| `nid_number` | `VARCHAR(20)` | UNIQUE | NULL | National ID (optional, for verification) |
| `status` | `VARCHAR(20)` | NOT NULL, CHECK | `'active'` | `active`, `suspended`, `pending_verification` |
| `last_login_at` | `TIMESTAMPTZ` | — | NULL | Last successful login |
| `failed_login_attempts` | `SMALLINT` | NOT NULL | `0` | Lockout after 5 failures |
| `locked_until` | `TIMESTAMPTZ` | — | NULL | Temporary lockout timestamp |
| `deleted_at` | `TIMESTAMPTZ` | — | NULL | Soft delete timestamp |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | Record creation |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | Last modification |

**Indexes**:
- PK: `users_pkey` on `(id)`
- Unique: `users_phone_key` on `(phone)` WHERE `deleted_at IS NULL`
- Unique: `users_email_key` on `(email)` WHERE `email IS NOT NULL AND deleted_at IS NULL`
- Unique: `users_nid_number_key` on `(nid_number)` WHERE `nid_number IS NOT NULL AND deleted_at IS NULL`
- Partial: `idx_users_active` on `(id, phone)` WHERE `deleted_at IS NULL AND status = 'active'`

**Check Constraints**:
```sql
CHECK (status IN ('active', 'suspended', 'pending_verification'))
CHECK (failed_login_attempts >= 0 AND failed_login_attempts <= 10)
```

---

### 3.2 `user_roles` — Role Assignments

**Purpose**: RBAC role assignments for users. Supports multiple roles per user.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `user_id` | `UUID` | FK → `users.id`, NOT NULL | — | |
| `role` | `VARCHAR(30)` | NOT NULL | — | `super_admin`, `finance_admin`, `operations_admin`, `user`, `guest` |
| `granted_by` | `UUID` | FK → `users.id` | NULL | Admin who granted the role |
| `granted_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `revoked_at` | `TIMESTAMPTZ` | — | NULL | Soft revoke (NULL = active) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `user_roles_pkey` on `(id)`
- Composite: `idx_user_roles_user_active` on `(user_id, role)` WHERE `revoked_at IS NULL`
- FK: `idx_user_roles_user_id` on `(user_id)`
- FK: `idx_user_roles_granted_by` on `(granted_by)`

**Check Constraints**:
```sql
CHECK (role IN ('super_admin', 'finance_admin', 'operations_admin', 'user', 'guest'))
CHECK (granted_by IS NULL OR granted_by != user_id)
```

**Unique Constraints**:
```sql
UNIQUE (user_id, role) WHERE revoked_at IS NULL  -- One active role assignment per type
```

---

### 3.3 `cards` — Transit Cards

**Purpose**: Transit smart cards linked to user accounts. Max 5 per user, 16-digit card numbers.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `user_id` | `UUID` | FK → `users.id`, NOT NULL | — | Owning user |
| `card_number` | `CHAR(16)` | UNIQUE, NOT NULL | — | 16-digit card number (padded) |
| `card_status` | `VARCHAR(20)` | NOT NULL, CHECK | `'active'` | `active`, `blocked`, `lost`, `expired` |
| `balance` | `NUMERIC(12,2)` | NOT NULL, CHECK | `0.00` | Current balance in BDT |
| `last_sync_seq` | `BIGINT` | NOT NULL | `0` | Latest sequence number from terminal sync |
| `last_synced_at` | `TIMESTAMPTZ` | — | NULL | Last successful sync timestamp |
| `issued_at` | `TIMESTAMPTZ` | — | NULL | Card issuance date |
| `expires_at` | `TIMESTAMPTZ` | — | NULL | Card expiry date |
| `deleted_at` | `TIMESTAMPTZ` | — | NULL | Soft delete (unlink from user) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `cards_pkey` on `(id)`
- Unique: `cards_card_number_key` on `(card_number)` WHERE `deleted_at IS NULL`
- Composite: `idx_cards_user_active` on `(user_id, id)` WHERE `deleted_at IS NULL`
- FK: `idx_cards_user_id` on `(user_id)`
- Partial: `idx_cards_active_lookup` on `(card_number, balance, last_sync_seq)` WHERE `deleted_at IS NULL AND card_status = 'active'`

**Check Constraints**:
```sql
CHECK (card_status IN ('active', 'blocked', 'lost', 'expired'))
CHECK (balance >= 0.00 AND balance <= 10000.00)
CHECK (card_number ~ '^[0-9]{16}$')
```

**Max 5 Cards Per User** — Enforced via application logic + database trigger:
```sql
CREATE OR REPLACE FUNCTION check_max_cards_per_user()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT COUNT(*) FROM cards
      WHERE user_id = NEW.user_id AND deleted_at IS NULL) >= 5 THEN
    RAISE EXCEPTION 'Maximum 5 cards per user account';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_max_cards
  BEFORE INSERT ON cards
  FOR EACH ROW
  EXECUTE FUNCTION check_max_cards_per_user();
```

---

### 3.4 `transactions` — Financial Transactions (Partitioned)

**Purpose**: All financial transactions — recharges, fare deductions, admin adjustments, reversals. Partitioned by month for performance.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | UUID v7 for time-ordering within partition |
| `card_id` | `UUID` | FK → `cards.id` | NULL | Related card (NULL for system-level) |
| `user_id` | `UUID` | FK → `users.id` | NULL | Related user |
| `type` | `VARCHAR(30)` | NOT NULL, CHECK | — | See type enum below |
| `amount` | `NUMERIC(12,2)` | NOT NULL, CHECK | — | Transaction amount (always positive) |
| `balance_before` | `NUMERIC(12,2)` | NOT NULL | — | Balance before transaction |
| `balance_after` | `NUMERIC(12,2)` | NOT NULL, CHECK | — | Balance after (must be >= 0, <= 10000) |
| `status` | `VARCHAR(20)` | NOT NULL, CHECK | `'pending'` | `pending`, `completed`, `failed`, `reversed` |
| `reference` | `VARCHAR(100)` | — | NULL | External reference (bKash trxID, terminal ID) |
| `description` | `VARCHAR(500)` | — | NULL | Human-readable description |
| `idempotency_key` | `VARCHAR(128)` | — | NULL | Prevents duplicate processing |
| `metadata` | `JSONB` | — | `'{}'` | Flexible metadata (terminal info, location, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | **Partition key** |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Transaction Types**:
| Type | Direction | Description |
|------|-----------|-------------|
| `recharge` | Credit | Online recharge via bKash |
| `recharge_failed_refund` | Credit | Auto-refund for failed payment |
| `fare_deduction` | Debit | Tap-in/tap-out fare |
| `fare_reversal` | Credit | Reversed fare (admin approved) |
| `admin_credit` | Credit | Admin balance adjustment (credit) |
| `admin_debit` | Debit | Admin balance adjustment (debit) |
| `card_issue_bonus` | Credit | Initial card issuance bonus |
| `sync_correction` | Credit/Debit | Balance correction from sync |

**Indexes**:
- PK: `transactions_pkey` on `(id, created_at)` — includes partition key
- Composite: `idx_transactions_card_date` on `(card_id, created_at DESC)` — card history
- Composite: `idx_transactions_user_date` on `(user_id, created_at DESC)` — user history
- Composite: `idx_transactions_type_status` on `(type, status, created_at DESC)` — admin queries
- Partial: `idx_transactions_pending` on `(card_id, id)` WHERE `status = 'pending'` — pending processing
- Covering: `idx_transactions_card_balance` on `(card_id, created_at DESC) INCLUDE (amount, balance_after, type, status)` — balance history without table lookup
- Partial: `idx_transactions_idempotency` on `(idempotency_key)` WHERE `idempotency_key IS NOT NULL` — idempotency check

**Check Constraints**:
```sql
CHECK (type IN ('recharge', 'recharge_failed_refund', 'fare_deduction', 'fare_reversal',
                 'admin_credit', 'admin_debit', 'card_issue_bonus', 'sync_correction'))
CHECK (status IN ('pending', 'completed', 'failed', 'reversed'))
CHECK (amount > 0)
CHECK (balance_after >= 0 AND balance_after <= 10000.00)
CHECK (balance_after = balance_before + amount OR balance_after = balance_before - amount)
```

**Partitioning** (detailed in Section 5):
```sql
CREATE TABLE transactions (
  -- columns as above
) PARTITION BY RANGE (created_at);
```

---

### 3.5 `payment_sessions` — bKash Payment Session Tracking

**Purpose**: Tracks bKash payment sessions from initiation to completion/failure. Enables idempotent payment processing.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `card_id` | `UUID` | FK → `cards.id`, NOT NULL | — | Card being recharged |
| `user_id` | `UUID` | FK → `users.id`, NOT NULL | — | Initiating user |
| `bkash_payment_id` | `VARCHAR(100)` | UNIQUE | NULL | bKash payment identifier |
| `bkash_trx_id` | `VARCHAR(100)` | UNIQUE | NULL | bKash transaction ID (set on completion) |
| `amount` | `NUMERIC(12,2)` | NOT NULL, CHECK | — | Recharge amount |
| `status` | `VARCHAR(20)` | NOT NULL, CHECK | `'initiated'` | See status enum |
| `idempotency_key` | `VARCHAR(128)` | UNIQUE, NOT NULL | — | Prevents duplicate payment creation |
| `bkash_callback_payload` | `JSONB` | — | NULL | Raw callback from bKash |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | `NOW() + interval '15 minutes'` | Session expiry |
| `completed_at` | `TIMESTAMPTZ` | — | NULL | Payment completion time |
| `failure_reason` | `VARCHAR(500)` | — | NULL | Reason for failure |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Payment Session Statuses**:
| Status | Description |
|--------|-------------|
| `initiated` | Session created, awaiting bKash payment |
| `processing` | bKash payment in progress |
| `completed` | Payment successful, balance credited |
| `failed` | Payment failed |
| `expired` | Session expired without payment |
| `refunded` | Auto-refund issued for failed payment |

**Indexes**:
- PK: `payment_sessions_pkey` on `(id)`
- Unique: `payment_sessions_idempotency_key_key` on `(idempotency_key)`
- Unique: `payment_sessions_bkash_payment_id_key` on `(bkash_payment_id)` WHERE `bkash_payment_id IS NOT NULL`
- Unique: `payment_sessions_bkash_trx_id_key` on `(bkash_trx_id)` WHERE `bkash_trx_id IS NOT NULL`
- Composite: `idx_payment_sessions_card_status` on `(card_id, status, created_at DESC)`
- Composite: `idx_payment_sessions_user_status` on `(user_id, status, created_at DESC)`
- Partial: `idx_payment_sessions_pending` on `(id, card_id, amount)` WHERE `status IN ('initiated', 'processing')`

**Check Constraints**:
```sql
CHECK (status IN ('initiated', 'processing', 'completed', 'failed', 'expired', 'refunded'))
CHECK (amount >= 50.00 AND amount <= 5000.00)
```

---

### 3.6 `sync_events` — Machine Sync Event Log

**Purpose**: Individual sync events from station gates and POS terminals. Supports out-of-order sync resolution via sequence numbers.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `batch_id` | `UUID` | FK → `sync_batches.id`, NOT NULL | — | Parent batch |
| `card_id` | `UUID` | FK → `cards.id` | NULL | Affected card |
| `terminal_id` | `VARCHAR(50)` | NOT NULL | — | Gate/POS terminal identifier |
| `terminal_type` | `VARCHAR(20)` | NOT NULL, CHECK | — | `gate`, `pos`, `tvm` |
| `event_type` | `VARCHAR(30)` | NOT NULL, CHECK | — | `tap_in`, `tap_out`, `recharge`, `balance_inquiry` |
| `sequence_number` | `BIGINT` | NOT NULL | — | Terminal-assigned sequence (for ordering) |
| `balance_delta` | `NUMERIC(12,2)` | — | NULL | Balance change from this event |
| `event_timestamp` | `TIMESTAMPTZ` | NOT NULL | — | When event occurred at terminal |
| `raw_payload` | `JSONB` | NOT NULL | `'{}'` | Raw event data from terminal |
| `idempotency_key` | `VARCHAR(128)` | NOT NULL | — | `terminal_id:sequence_number` composite |
| `processing_status` | `VARCHAR(20)` | NOT NULL, CHECK | `'pending'` | `pending`, `processed`, `duplicate`, `error` |
| `error_message` | `VARCHAR(500)` | — | NULL | Error details if processing failed |
| `processed_at` | `TIMESTAMPTZ` | — | NULL | When event was processed |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | When received by server |

**Indexes**:
- PK: `sync_events_pkey` on `(id)`
- Unique: `idx_sync_events_idempotency` on `(idempotency_key)` — prevents duplicate processing
- Composite: `idx_sync_events_batch_seq` on `(batch_id, sequence_number)` — ordered batch processing
- Composite: `idx_sync_events_card_seq` on `(card_id, sequence_number DESC)` — card sync history
- Composite: `idx_sync_events_terminal_pending` on `(terminal_id, sequence_number)` WHERE `processing_status = 'pending'`
- FK: `idx_sync_events_batch_id` on `(batch_id)`
- FK: `idx_sync_events_card_id` on `(card_id)`

**Check Constraints**:
```sql
CHECK (terminal_type IN ('gate', 'pos', 'tvm'))
CHECK (event_type IN ('tap_in', 'tap_out', 'recharge', 'balance_inquiry'))
CHECK (processing_status IN ('pending', 'processed', 'duplicate', 'error'))
```

---

### 3.7 `sync_batches` — Batch Sync Tracking

**Purpose**: Tracks batches of sync events from terminals. Enables offline recovery when terminals reconnect.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `terminal_id` | `VARCHAR(50)` | NOT NULL | — | Source terminal |
| `terminal_type` | `VARCHAR(20)` | NOT NULL, CHECK | — | `gate`, `pos`, `tvm` |
| `station_id` | `VARCHAR(50)` | NOT NULL | — | Station identifier |
| `batch_status` | `VARCHAR(20)` | NOT NULL, CHECK | `'received'` | `received`, `processing`, `completed`, `partial_error` |
| `total_events` | `INTEGER` | NOT NULL, CHECK | — | Expected event count |
| `processed_count` | `INTEGER` | NOT NULL | `0` | Successfully processed |
| `error_count` | `INTEGER` | NOT NULL | `0` | Failed events |
| `first_sequence` | `BIGINT` | NOT NULL | — | First sequence number in batch |
| `last_sequence` | `BIGINT` | NOT NULL | — | Last sequence number in batch |
| `raw_batch_payload` | `JSONB` | — | NULL | Full batch payload for replay |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `sync_batches_pkey` on `(id)`
- Composite: `idx_sync_batches_terminal_status` on `(terminal_id, batch_status, created_at DESC)`
- Composite: `idx_sync_batches_station_date` on `(station_id, created_at DESC)`
- Partial: `idx_sync_batches_processing` on `(terminal_id, id)` WHERE `batch_status IN ('received', 'processing')`

**Check Constraints**:
```sql
CHECK (terminal_type IN ('gate', 'pos', 'tvm'))
CHECK (batch_status IN ('received', 'processing', 'completed', 'partial_error'))
CHECK (total_events > 0)
CHECK (processed_count >= 0 AND processed_count <= total_events)
CHECK (error_count >= 0 AND error_count <= total_events)
CHECK (processed_count + error_count <= total_events)
CHECK (last_sequence >= first_sequence)
```

---

### 3.8 `audit_log` — Immutable Audit Trail

**Purpose**: Append-only audit log for all financial and admin operations. Never updated or deleted.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `actor_id` | `UUID` | FK → `users.id` | NULL | User who performed action (NULL for system) |
| `action` | `VARCHAR(50)` | NOT NULL | — | `login`, `logout`, `recharge`, `adjustment`, `card_link`, `card_unlink`, `role_change`, `sync_batch_process` |
| `entity_type` | `VARCHAR(50)` | NOT NULL | — | `user`, `card`, `transaction`, `payment_session`, `balance_adjustment`, `sync_batch` |
| `entity_id` | `UUID` | NOT NULL | — | Target entity UUID |
| `old_values` | `JSONB` | — | NULL | State before change |
| `new_values` | `JSONB` | — | NULL | State after change |
| `ip_address` | `INET` | — | NULL | Client IP |
| `user_agent` | `VARCHAR(500)` | — | NULL | Client user agent |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `audit_log_pkey` on `(id)`
- Composite: `idx_audit_log_entity` on `(entity_type, entity_id, created_at DESC)` — entity history
- Composite: `idx_audit_log_actor` on `(actor_id, created_at DESC)` — user activity
- Composite: `idx_audit_log_action_date` on `(action, created_at DESC)` — action filtering
- Covering: `idx_audit_log_entity_covering` on `(entity_type, entity_id, created_at DESC) INCLUDE (action, actor_id)` — entity timeline without table lookup

**Note**: No `updated_at` or `deleted_at` — this table is append-only.

---

### 3.9 `balance_adjustments` — Admin Balance Adjustments

**Purpose**: Tracks admin-initiated balance adjustments requiring dual approval (two different Finance Admins).

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `card_id` | `UUID` | FK → `cards.id`, NOT NULL | — | Target card |
| `user_id` | `UUID` | FK → `users.id` | NULL | Card owner |
| `amount` | `NUMERIC(12,2)` | NOT NULL, CHECK | — | Adjustment amount (positive=credit, negative=debit) |
| `reason` | `VARCHAR(500)` | NOT NULL | — | Business reason |
| `requested_by` | `UUID` | FK → `users.id`, NOT NULL | — | Operations Admin who requested |
| `approved_by_1` | `UUID` | FK → `users.id` | NULL | First Finance Admin approver |
| `approved_by_2` | `UUID` | FK → `users.id` | NULL | Second Finance Admin approver |
| `approved_at_1` | `TIMESTAMPTZ` | — | NULL | First approval timestamp |
| `approved_at_2` | `TIMESTAMPTZ` | — | NULL | Second approval timestamp |
| `approval_status` | `VARCHAR(20)` | NOT NULL, CHECK | `'pending'` | `pending`, `approved`, `rejected`, `executed` |
| `rejection_reason` | `VARCHAR(500)` | — | NULL | If rejected |
| `executed_at` | `TIMESTAMPTZ` | — | NULL | When adjustment was applied |
| `transaction_id` | `UUID` | FK → `transactions.id` | NULL | Linked transaction after execution |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `balance_adjustments_pkey` on `(id)`
- Composite: `idx_balance_adj_card_status` on `(card_id, approval_status, created_at DESC)`
- Composite: `idx_balance_adj_requested_by` on `(requested_by, approval_status, created_at DESC)`
- Partial: `idx_balance_adj_pending` on `(id, card_id, amount)` WHERE `approval_status = 'pending'`
- FK: `idx_balance_adj_transaction` on `(transaction_id)` WHERE `transaction_id IS NOT NULL`

**Check Constraints**:
```sql
CHECK (approval_status IN ('pending', 'approved', 'rejected', 'executed'))
CHECK (amount != 0)
CHECK (ABS(amount) <= 10000.00)
CHECK (approved_by_1 IS NULL OR approved_by_1 != approved_by_2)  -- Different approvers
CHECK (approved_by_1 IS NULL OR approved_by_1 != requested_by)  -- Approver != requester
CHECK (approved_by_2 IS NULL OR approved_by_2 != requested_by)
```

---

### 3.10 `notifications` — SMS/Email Notification Log

**Purpose**: Tracks outbound notifications (SMS, email) for delivery status and retry logic.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `user_id` | `UUID` | FK → `users.id` | NULL | Recipient user |
| `card_id` | `UUID` | FK → `cards.id` | NULL | Related card |
| `type` | `VARCHAR(30)` | NOT NULL, CHECK | — | `recharge_success`, `recharge_failed`, `low_balance`, `card_linked`, `adjustment_applied`, `sync_complete` |
| `channel` | `VARCHAR(20)` | NOT NULL, CHECK | — | `sms`, `email`, `push` |
| `recipient` | `VARCHAR(255)` | NOT NULL | — | Phone number or email |
| `template` | `VARCHAR(100)` | NOT NULL | — | Template identifier |
| `template_vars` | `JSONB` | — | `'{}'` | Template substitution variables |
| `language` | `VARCHAR(5)` | NOT NULL | `'en'` | `en`, `bn` |
| `status` | `VARCHAR(20)` | NOT NULL, CHECK | `'queued'` | `queued`, `sent`, `delivered`, `failed`, `bounced` |
| `provider_ref` | `VARCHAR(100)` | — | NULL | SMS/email provider reference |
| `error_message` | `VARCHAR(500)` | — | NULL | Failure reason |
| `retry_count` | `SMALLINT` | NOT NULL | `0` | |
| `sent_at` | `TIMESTAMPTZ` | — | NULL | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `notifications_pkey` on `(id)`
- Composite: `idx_notifications_user_date` on `(user_id, created_at DESC)`
- Composite: `idx_notifications_status_retry` on `(status, retry_count, created_at)` WHERE `status IN ('queued', 'failed')` — retry queue
- FK: `idx_notifications_card_id` on `(card_id)`

**Check Constraints**:
```sql
CHECK (type IN ('recharge_success', 'recharge_failed', 'low_balance', 'card_linked', 'adjustment_applied', 'sync_complete'))
CHECK (channel IN ('sms', 'email', 'push'))
CHECK (status IN ('queued', 'sent', 'delivered', 'failed', 'bounced'))
CHECK (language IN ('en', 'bn'))
CHECK (retry_count >= 0 AND retry_count <= 5)
```

---

### 3.11 `sessions` — Active Session Tracking

**Purpose**: Server-side session tracking. Redis handles hot session data; this table provides persistence and audit capability.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `user_id` | `UUID` | FK → `users.id`, NOT NULL | — | |
| `token_hash` | `VARCHAR(128)` | NOT NULL | — | SHA-256 hash of session token |
| `expires_at` | `TIMESTAMPTZ` | NOT NULL | — | Session expiry (30 min from last activity) |
| `ip_address` | `INET` | — | NULL | |
| `user_agent` | `VARCHAR(500)` | — | NULL | |
| `device_info` | `JSONB` | — | `'{}'` | Device fingerprint |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `last_active_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Indexes**:
- PK: `sessions_pkey` on `(id)`
- Unique: `idx_sessions_token_hash` on `(token_hash)`
- Composite: `idx_sessions_user_active` on `(user_id, expires_at)` WHERE `expires_at > NOW()`
- FK: `idx_sessions_user_id` on `(user_id)`

**Note**: Redis is the primary session store for performance. This table is written asynchronously for audit and multi-device management. A periodic cleanup job removes expired sessions.

---

### 3.12 `config` — System Configuration

**Purpose**: Runtime configuration values managed by admins. Avoids code deployments for parameter changes.

| Column | Type | Constraints | Default | Comment |
|--------|------|-------------|---------|---------|
| `id` | `UUID` | PK, NOT NULL | `gen_random_uuid()` | |
| `key` | `VARCHAR(100)` | UNIQUE, NOT NULL | — | Configuration key |
| `value` | `JSONB` | NOT NULL | — | Configuration value |
| `description` | `VARCHAR(500)` | — | NULL | Human-readable description |
| `updated_by` | `UUID` | FK → `users.id` | NULL | Last modifier |
| `created_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL | `NOW()` | |

**Default Configuration Values**:

| Key | Value | Description |
|-----|-------|-------------|
| `recharge.min_amount` | `50` | Minimum recharge amount (BDT) |
| `recharge.max_amount` | `5000` | Maximum per transaction (BDT) |
| `card.max_balance` | `10000` | Maximum card balance (BDT) |
| `card.max_per_user` | `5` | Maximum cards per user |
| `session.timeout_minutes` | `30` | Session inactivity timeout |
| `data.retention_years` | `5` | Transaction data retention |
| `sync.accuracy_threshold` | `0.995` | Minimum sync accuracy (99.5%) |
| `login.max_failed_attempts` | `5` | Account lockout threshold |
| `notification.low_balance_threshold` | `100` | Low balance alert threshold (BDT) |

**Indexes**:
- PK: `config_pkey` on `(id)`
- Unique: `config_key_key` on `(key)`

---

## 4. Indexing Strategy

### 4.1 Index Inventory

| Table | Index | Type | Columns | Justification |
|-------|-------|------|---------|---------------|
| `users` | `users_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `users` | `users_phone_key` | B-tree (Unique) | `(phone)` WHERE `deleted_at IS NULL` | Login by phone; partial avoids deleted duplicates |
| `users` | `users_email_key` | B-tree (Unique) | `(email)` WHERE `email IS NOT NULL AND deleted_at IS NULL` | Login by email; partial for nullable |
| `users` | `idx_users_active` | B-tree (Partial) | `(id, phone)` WHERE `deleted_at IS NULL AND status = 'active'` | Active user queries |
| `user_roles` | `user_roles_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `user_roles` | `idx_user_roles_user_active` | B-tree (Partial) | `(user_id, role)` WHERE `revoked_at IS NULL` | Active role check per user |
| `cards` | `cards_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `cards` | `cards_card_number_key` | B-tree (Unique) | `(card_number)` WHERE `deleted_at IS NULL` | Card lookup by number; partial for soft deletes |
| `cards` | `idx_cards_user_active` | B-tree (Composite) | `(user_id, id)` WHERE `deleted_at IS NULL` | List user's cards |
| `cards` | `idx_cards_active_lookup` | B-tree (Covering) | `(card_number, balance, last_sync_seq)` WHERE `deleted_at IS NULL AND card_status = 'active'` | Sync endpoint: lookup card + balance + seq in one index scan |
| `transactions` | `transactions_pkey` | B-tree (PK) | `(id, created_at)` | Partitioned PK includes partition key |
| `transactions` | `idx_transactions_card_date` | B-tree (Composite) | `(card_id, created_at DESC)` | Card transaction history (most common query) |
| `transactions` | `idx_transactions_user_date` | B-tree (Composite) | `(user_id, created_at DESC)` | User transaction history |
| `transactions` | `idx_transactions_type_status` | B-tree (Composite) | `(type, status, created_at DESC)` | Admin reconciliation queries |
| `transactions` | `idx_transactions_pending` | B-tree (Partial) | `(card_id, id)` WHERE `status = 'pending'` | Pending transaction processing queue |
| `transactions` | `idx_transactions_card_balance` | B-tree (Covering) | `(card_id, created_at DESC) INCLUDE (amount, balance_after, type, status)` | Balance history without heap lookup |
| `transactions` | `idx_transactions_idempotency` | B-tree (Partial) | `(idempotency_key)` WHERE `idempotency_key IS NOT NULL` | Idempotency check for sync |
| `payment_sessions` | `payment_sessions_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `payment_sessions` | `payment_sessions_idempotency_key_key` | B-tree (Unique) | `(idempotency_key)` | Prevents duplicate payment creation |
| `payment_sessions` | `idx_payment_sessions_card_status` | B-tree (Composite) | `(card_id, status, created_at DESC)` | Card payment history |
| `payment_sessions` | `idx_payment_sessions_pending` | B-tree (Partial) | `(id, card_id, amount)` WHERE `status IN ('initiated', 'processing')` | Active payment monitoring |
| `sync_events` | `sync_events_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `sync_events` | `idx_sync_events_idempotency` | B-tree (Unique) | `(idempotency_key)` | Prevents duplicate event processing |
| `sync_events` | `idx_sync_events_batch_seq` | B-tree (Composite) | `(batch_id, sequence_number)` | Ordered batch processing |
| `sync_events` | `idx_sync_events_card_seq` | B-tree (Composite) | `(card_id, sequence_number DESC)` | Card sync history |
| `sync_events` | `idx_sync_events_terminal_pending` | B-tree (Partial) | `(terminal_id, sequence_number)` WHERE `processing_status = 'pending'` | Pending events per terminal |
| `sync_batches` | `sync_batches_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `sync_batches` | `idx_sync_batches_terminal_status` | B-tree (Composite) | `(terminal_id, batch_status, created_at DESC)` | Terminal batch history |
| `sync_batches` | `idx_sync_batches_processing` | B-tree (Partial) | `(terminal_id, id)` WHERE `batch_status IN ('received', 'processing')` | Active batch processing |
| `audit_log` | `audit_log_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `audit_log` | `idx_audit_log_entity` | B-tree (Composite) | `(entity_type, entity_id, created_at DESC)` | Entity audit trail |
| `audit_log` | `idx_audit_log_actor` | B-tree (Composite) | `(actor_id, created_at DESC)` | User activity log |
| `audit_log` | `idx_audit_log_entity_covering` | B-tree (Covering) | `(entity_type, entity_id, created_at DESC) INCLUDE (action, actor_id)` | Entity timeline without heap lookup |
| `balance_adjustments` | `balance_adjustments_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `balance_adjustments` | `idx_balance_adj_card_status` | B-tree (Composite) | `(card_id, approval_status, created_at DESC)` | Card adjustment history |
| `balance_adjustments` | `idx_balance_adj_pending` | B-tree (Partial) | `(id, card_id, amount)` WHERE `approval_status = 'pending'` | Pending approval queue |
| `notifications` | `notifications_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `notifications` | `idx_notifications_status_retry` | B-tree (Partial) | `(status, retry_count, created_at)` WHERE `status IN ('queued', 'failed')` | Notification retry queue |
| `sessions` | `sessions_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `sessions` | `idx_sessions_token_hash` | B-tree (Unique) | `(token_hash)` | Session token lookup |
| `sessions` | `idx_sessions_user_active` | B-tree (Partial) | `(user_id, expires_at)` WHERE `expires_at > NOW()` | Active sessions per user |
| `config` | `config_pkey` | B-tree (PK) | `(id)` | Primary lookup |
| `config` | `config_key_key` | B-tree (Unique) | `(key)` | Config lookup by key |

### 4.2 Indexes to AVOID

| Column | Reason |
|--------|--------|
| `users.status` alone | Low cardinality (3 values); use partial index instead |
| `transactions.status` alone | Low cardinality (4 values); use partial index for `pending` |
| `notifications.channel` alone | Low cardinality (3 values); composite with status is sufficient |
| `sync_events.event_type` alone | Low cardinality; composite with terminal/card is better |
| Frequently updated columns | Index maintenance overhead exceeds benefit |
| `cards.card_status` alone | Low cardinality; use partial index for `active` cards |

### 4.3 Index Maintenance

```sql
-- Monitor index usage (run weekly)
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY relname, indexrelname;

-- Rebuild indexes monthly during maintenance window
REINDEX TABLE CONCURRENTLY transactions;
REINDEX TABLE CONCURRENTLY sync_events;
```

---

## 5. Partitioning Strategy

### 5.1 Transaction Table Partitioning

The `transactions` table is partitioned by **RANGE** on `created_at` (monthly partitions).

**Rationale**:
- 500,000 transactions/day × 30 days ≈ 15M rows/month
- Monthly partitions keep each partition at ~2-5GB (manageable size)
- Natural query pattern: "show transactions for this month"
- Enables efficient archival and deletion after 5-year retention
- Partition pruning eliminates scanning irrelevant months for date-range queries

**Partition Schema**:
```sql
CREATE TABLE transactions (
  id UUID NOT NULL DEFAULT gen_random_uuid(),
  card_id UUID,
  user_id UUID,
  type VARCHAR(30) NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  balance_before NUMERIC(12,2) NOT NULL,
  balance_after NUMERIC(12,2) NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  reference VARCHAR(100),
  description VARCHAR(500),
  idempotency_key VARCHAR(128),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id, created_at),
  CHECK (type IN ('recharge', 'recharge_failed_refund', 'fare_deduction', 'fare_reversal',
                   'admin_credit', 'admin_debit', 'card_issue_bonus', 'sync_correction')),
  CHECK (status IN ('pending', 'completed', 'failed', 'reversed')),
  CHECK (amount > 0),
  CHECK (balance_after >= 0 AND balance_after <= 10000.00)
) PARTITION BY RANGE (created_at);
```

**Monthly Partition Creation** (automated via pg_partman or cron job):
```sql
-- Example partitions
CREATE TABLE transactions_y2026m01 PARTITION OF transactions
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE transactions_y2026m02 PARTITION OF transactions
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- ... continue for each month

-- Default partition as safety net
CREATE TABLE transactions_default PARTITION OF transactions DEFAULT;
```

### 5.2 Partition Management Automation

**Pre-creation** (create 3 months ahead):
```sql
-- Run monthly via cron or pg_partman
CREATE OR REPLACE FUNCTION create_transaction_partitions()
RETURNS void AS $$
DECLARE
  start_date DATE;
  end_date DATE;
  partition_name TEXT;
  i INTEGER;
BEGIN
  FOR i IN 1..3 LOOP
    start_date := DATE_TRUNC('month', CURRENT_DATE + (i || ' months')::INTERVAL);
    end_date := start_date + INTERVAL '1 month';
    partition_name := 'transactions_y' || TO_CHAR(start_date, 'YYYY') || 'm' || TO_CHAR(start_date, 'MM');

    EXECUTE FORMAT(
      'CREATE TABLE IF NOT EXISTS %I PARTITION OF transactions FOR VALUES FROM (%L) TO (%L)',
      partition_name, start_date, end_date
    );
  END LOOP;
END;
$$ LANGUAGE plpgsql;
```

**Archival** (detach partitions older than 5 years):
```sql
-- Detach partition (makes it a standalone table)
ALTER TABLE transactions DETACH PARTITION transactions_y2021m01;

-- Export to cold storage (S3 via pg_dump or COPY)
-- Then drop the detached table
DROP TABLE transactions_y2021m01;
```

**Deletion Schedule**:
```
Month 1-60: Active partitions (queryable)
Month 61: Detached, exported to S3 Glacier
Month 62: Dropped from database
```

### 5.3 Partition Pruning Query Patterns

These queries benefit from automatic partition pruning:

```sql
-- ✅ Prunes to single partition
SELECT * FROM transactions WHERE card_id = ? AND created_at >= '2026-03-01' AND created_at < '2026-04-01';

-- ✅ Prunes to 3 partitions
SELECT * FROM transactions WHERE created_at >= '2026-01-15' AND created_at < '2026-04-15';

-- ✅ Prunes to current month
SELECT SUM(amount) FROM transactions WHERE type = 'recharge' AND status = 'completed'
  AND created_at >= DATE_TRUNC('month', NOW());

-- ❌ No pruning (scans all partitions)
SELECT * FROM transactions WHERE card_id = ?;  -- Missing date filter
```

**Rule**: All application queries against `transactions` MUST include a `created_at` range filter. Enforce via Prisma middleware or application-level validation.

---

## 6. Constraints & Business Rules Enforcement

### 6.1 Database-Level Check Constraints

| Rule | Constraint | Table |
|------|-----------|-------|
| Min recharge BDT 50 | `CHECK (amount >= 50.00)` | `payment_sessions` |
| Max recharge BDT 5,000 | `CHECK (amount <= 5000.00)` | `payment_sessions` |
| Max card balance BDT 10,000 | `CHECK (balance >= 0 AND balance <= 10000.00)` | `cards`, `transactions` |
| Balance never negative | `CHECK (balance_after >= 0)` | `transactions` |
| 16-digit card number | `CHECK (card_number ~ '^[0-9]{16}$')` | `cards` |
| Valid transaction types | `CHECK (type IN (...))` | `transactions` |
| Valid payment statuses | `CHECK (status IN (...))` | `payment_sessions` |
| Dual approval (different approvers) | `CHECK (approved_by_1 != approved_by_2)` | `balance_adjustments` |
| Approver ≠ requester | `CHECK (approved_by_1 != requested_by)` | `balance_adjustments` |
| Max 5 retry attempts | `CHECK (retry_count <= 5)` | `notifications` |
| Card number format | `CHECK (card_number ~ '^[0-9]{16}$')` | `cards` |

### 6.2 Foreign Key Constraints

All foreign keys use `ON DELETE SET NULL` for operational tables (cards, transactions, payment sessions) to preserve data integrity when users are soft-deleted. Session and role tables use `ON DELETE CASCADE` since they have no independent meaning without the user.

| FK Column | References | ON DELETE | Justification |
|-----------|-----------|-----------|---------------|
| `user_roles.user_id` | `users.id` | CASCADE | Roles meaningless without user |
| `cards.user_id` | `users.id` | SET NULL | Preserve card record for audit |
| `transactions.card_id` | `cards.id` | SET NULL | Preserve transaction for audit |
| `transactions.user_id` | `users.id` | SET NULL | Preserve transaction for audit |
| `payment_sessions.card_id` | `cards.id` | SET NULL | Preserve payment record for audit |
| `payment_sessions.user_id` | `users.id` | SET NULL | Preserve payment record for audit |
| `sync_events.card_id` | `cards.id` | SET NULL | Preserve sync event for audit |
| `balance_adjustments.card_id` | `cards.id` | SET NULL | Preserve adjustment record |
| `balance_adjustments.user_id` | `users.id` | SET NULL | Preserve adjustment record |
| `notifications.user_id` | `users.id` | SET NULL | Preserve notification record |
| `notifications.card_id` | `cards.id` | SET NULL | Preserve notification record |
| `sessions.user_id` | `users.id` | CASCADE | Sessions meaningless without user |
| `audit_log.actor_id` | `users.id` | SET NULL | Preserve audit trail |

### 6.3 Unique Constraints

| Constraint | Columns | Condition | Purpose |
|------------|---------|-----------|---------|
| `users_phone_key` | `(phone)` | `WHERE deleted_at IS NULL` | One active account per phone |
| `users_email_key` | `(email)` | `WHERE email IS NOT NULL AND deleted_at IS NULL` | One active account per email |
| `cards_card_number_key` | `(card_number)` | `WHERE deleted_at IS NULL` | Card linked to one active account |
| `payment_sessions_idempotency_key_key` | `(idempotency_key)` | — | Prevent duplicate payment creation |
| `payment_sessions_bkash_trx_id_key` | `(bkash_trx_id)` | `WHERE bkash_trx_id IS NOT NULL` | One transaction per bKash trxID |
| `sync_events_idempotency_key` | `(idempotency_key)` | — | Prevent duplicate sync event processing |
| `config_key_key` | `(key)` | — | One value per config key |

### 6.4 Triggers

#### 6.4.1 Max Cards Per User
```sql
CREATE OR REPLACE FUNCTION check_max_cards_per_user()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT COUNT(*) FROM cards
      WHERE user_id = NEW.user_id AND deleted_at IS NULL) >= 5 THEN
    RAISE EXCEPTION 'Maximum 5 cards per user account (user_id: %)', NEW.user_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_max_cards
  BEFORE INSERT ON cards
  FOR EACH ROW
  EXECUTE FUNCTION check_max_cards_per_user();
```

#### 6.4.2 Auto-Update `updated_at`
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_cards_updated_at BEFORE UPDATE ON cards
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_transactions_updated_at BEFORE UPDATE ON transactions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ... (all tables with updated_at)
```

#### 6.4.3 Audit Log Trigger (for financial tables)
```sql
CREATE OR REPLACE FUNCTION audit_financial_changes()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (actor_id, action, entity_type, entity_id, old_values, new_values, ip_address, user_agent)
  VALUES (
    COALESCE(current_setting('app.current_user_id', true)::UUID, NULL),
    CASE WHEN TG_OP = 'INSERT' THEN 'create' WHEN TG_OP = 'UPDATE' THEN 'update' ELSE 'delete' END,
    TG_TABLE_NAME,
    COALESCE(NEW.id, OLD.id),
    CASE WHEN TG_OP = 'DELETE' THEN to_jsonb(OLD) ELSE to_jsonb(OLD) END,
    CASE WHEN TG_OP = 'INSERT' THEN to_jsonb(NEW) ELSE to_jsonb(NEW) END,
    COALESCE(current_setting('app.client_ip', true)::INET, NULL),
    COALESCE(current_setting('app.user_agent', true), NULL)
  );
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_balance_adjustments
  AFTER INSERT OR UPDATE OR DELETE ON balance_adjustments
  FOR EACH ROW EXECUTE FUNCTION audit_financial_changes();
```

---

## 7. Data Retention & Archival

### 7.1 Retention Policy

| Data Type | Retention | Method |
|-----------|-----------|--------|
| Transactions | 5 years | Partition detachment + S3 archival |
| Payment sessions | 5 years | Same as transactions (linked) |
| Sync events | 2 years | Partition by month, detach after 24 months |
| Sync batches | 2 years | Same as sync events |
| Audit log | 7 years | Regulatory requirement; archive to cold storage |
| Notifications | 1 year | DELETE old records monthly |
| Sessions | 30 days | Expired session cleanup job |
| Balance adjustments | 7 years | Same as audit log |

### 7.2 Soft Delete Pattern

Tables with `deleted_at` column:
- `users` — Account deactivation (preserves all linked data)
- `cards` — Card unlinking (preserves transaction history)

**Query Pattern**:
```sql
-- Always filter soft-deleted records
SELECT * FROM users WHERE deleted_at IS NULL AND phone = ?;
SELECT * FROM cards WHERE deleted_at IS NULL AND user_id = ?;
```

**Partial Indexes** ensure soft-deleted records don't bloat active query indexes.

### 7.3 Archival Workflow

```
Monthly Cron Job:
1. Identify partitions older than retention period
2. DETACH partition from parent table
3. Export partition data to S3 (Parquet format for analytics)
4. Verify export integrity (row count, checksum)
5. DROP detached partition table
6. Log archival in audit_log
```

**S3 Archive Structure**:
```
s3://dmtcl-data-archive/
  transactions/
    2021/01/transactions_2021_01.parquet
    2021/02/transactions_2021_02.parquet
  sync_events/
    2024/01/sync_events_2024_01.parquet
```

### 7.4 Cleanup Jobs

```sql
-- Expired sessions cleanup (daily)
DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '7 days';

-- Old notifications cleanup (monthly)
DELETE FROM notifications WHERE created_at < NOW() - INTERVAL '1 year';

-- Expired payment sessions cleanup (daily)
UPDATE payment_sessions SET status = 'expired'
WHERE status = 'initiated' AND expires_at < NOW();
```

---

## 8. Security at Database Level

### 8.1 Row-Level Security (RLS)

RLS policies ensure data isolation at the database level, providing defense-in-depth beyond application-level checks.

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cards ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE balance_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY user_isolation ON users
  FOR ALL USING (id = current_setting('app.current_user_id')::UUID);

CREATE POLICY card_isolation ON cards
  FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID OR
                 current_setting('app.current_role') IN ('super_admin', 'operations_admin'));

CREATE POLICY transaction_isolation ON transactions
  FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID OR
                    current_setting('app.current_role') IN ('super_admin', 'finance_admin'));

CREATE POLICY payment_session_isolation ON payment_sessions
  FOR ALL USING (user_id = current_setting('app.current_user_id')::UUID OR
                 current_setting('app.current_role') IN ('super_admin', 'finance_admin'));

-- Admins can see all balance adjustments
CREATE POLICY balance_adj_admin_only ON balance_adjustments
  FOR ALL USING (current_setting('app.current_role') IN ('super_admin', 'finance_admin', 'operations_admin'));

-- Notifications: users see their own, admins see all
CREATE POLICY notification_isolation ON notifications
  FOR SELECT USING (user_id = current_setting('app.current_user_id')::UUID OR
                    current_setting('app.current_role') IN ('super_admin', 'operations_admin'));
```

**RLS Bypass for Admin Operations**:
Application sets `app.current_role` via `SET LOCAL` at the start of each transaction. Admin roles bypass user-level isolation.

### 8.2 Database Roles & Access Control

```sql
-- Application role (Prisma/Next.js)
CREATE ROLE dmtcl_app WITH LOGIN PASSWORD '...';
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO dmtcl_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO dmtcl_app;

-- Read-only role (analytics, reporting)
CREATE ROLE dmtcl_readonly WITH LOGIN PASSWORD '...';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dmtcl_readonly;

-- Migration role (Prisma migrate)
CREATE ROLE dmtcl_migrate WITH LOGIN PASSWORD '...';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dmtcl_migrate;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dmtcl_migrate;

-- Revoke public access
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

### 8.3 Encryption

| Layer | Method | Details |
|-------|--------|---------|
| **At Rest** | AWS RDS AES-256 | Enabled via RDS encryption (uses AWS KMS) |
| **In Transit** | TLS 1.3 | `sslmode=require` in connection string |
| **Passwords** | bcrypt (cost 12+) | Application-level hashing before storage |
| **Sensitive Fields** | pgcrypto `pgp_sym_encrypt` | Optional: encrypt `nid_number` if PII regulations require |
| **Backups** | AWS RDS encrypted snapshots | Automatic encryption via KMS |

### 8.4 Audit Logging Approach

- **Financial operations**: Trigger-based audit on `balance_adjustments` table
- **Admin actions**: Application-level audit writes to `audit_log`
- **Login attempts**: Application-level logging to `audit_log`
- **Schema changes**: PostgreSQL `log_statement = 'ddl'` in RDS parameter group
- **Connection logging**: `log_connections = on`, `log_disconnections = on`

---

## 9. Performance Considerations

### 9.1 Connection Pooling Configuration (PgBouncer)

```ini
[databases]
dmtcl = host=<rds-endpoint> port=5432 dbname=dmtcl

[pgbouncer]
listen_port = 6432
listen_addr = *
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 500
default_pool_size = 50
min_pool_size = 10
reserve_pool_size = 20
reserve_pool_timeout = 3
server_lifetime = 3600
server_idle_timeout = 600
server_connect_timeout = 15
server_login_retry = 5
query_timeout = 30
query_wait_timeout = 30
client_idle_timeout = 600
idle_transaction_timeout = 300
```

### 9.2 Query Optimization

**Critical Query Patterns**:

```sql
-- 1. Card balance lookup (sync endpoint, < 500ms requirement)
-- Uses: idx_cards_active_lookup (covering index)
SELECT card_number, balance, last_sync_seq
FROM cards
WHERE card_number = $1 AND deleted_at IS NULL AND card_status = 'active';

-- 2. User transaction history (paginated)
-- Uses: idx_transactions_user_date, partition pruning
SELECT id, type, amount, balance_after, status, created_at
FROM transactions
WHERE user_id = $1 AND created_at >= $2 AND created_at < $3
ORDER BY created_at DESC
LIMIT 50 OFFSET 0;

-- 3. Pending payment sessions (monitoring)
-- Uses: idx_payment_sessions_pending (partial index)
SELECT id, card_id, amount, created_at
FROM payment_sessions
WHERE status IN ('initiated', 'processing') AND expires_at > NOW()
ORDER BY created_at ASC;

-- 4. Pending sync events per terminal
-- Uses: idx_sync_events_terminal_pending (partial index)
SELECT id, sequence_number, event_type, raw_payload
FROM sync_events
WHERE terminal_id = $1 AND processing_status = 'pending'
ORDER BY sequence_number ASC;

-- 5. Daily reconciliation report
-- Uses: idx_transactions_type_status, partition pruning
SELECT type, status, COUNT(*), SUM(amount)
FROM transactions
WHERE created_at >= $1 AND created_at < $2
GROUP BY type, status;
```

### 9.3 Slow Query Monitoring

```sql
-- Enable slow query logging in RDS parameter group
log_min_duration_statement = 500  -- Log queries > 500ms
log_statement = 'none'
log_duration = off

-- Monitor with pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 slowest queries
SELECT query, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### 9.4 Read Replica Routing Strategy

| Query Type | Target | Justification |
|------------|--------|---------------|
| Card balance lookup | Primary | Must be strongly consistent for sync |
| Payment processing | Primary | Write operation |
| Transaction history | Read Replica 1 | Read-only, eventual consistency acceptable |
| Admin reports | Read Replica 2 | Heavy aggregation, isolate from user traffic |
| Dashboard metrics | Read Replica 2 | Materialized views refreshed every 5 min |
| Sync event processing | Primary | Write operation |
| Config lookups | Read Replica 1 | Read-only, cached in Redis |

**Prisma Configuration**:
```typescript
// Use read replica for read queries
const prismaRead = new PrismaClient({
  datasources: { db: { url: process.env.DATABASE_READ_URL } }
});

// Use primary for writes
const prismaWrite = new PrismaClient({
  datasources: { db: { url: process.env.DATABASE_WRITE_URL } }
});
```

### 9.5 Materialized Views for Reporting

```sql
-- Daily transaction summary (refreshed every 5 minutes)
CREATE MATERIALIZED VIEW mv_daily_transaction_summary AS
SELECT
  DATE(created_at) AS transaction_date,
  type,
  status,
  COUNT(*) AS transaction_count,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount
FROM transactions
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(created_at), type, status;

CREATE UNIQUE INDEX idx_mv_daily_summary_date_type_status
  ON mv_daily_transaction_summary (transaction_date, type, status);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_transaction_summary;
```

---

## 10. Migration Strategy

### 10.1 Prisma Migration Approach

```bash
# Development
npx prisma migrate dev --name init

# Production (zero-downtime)
npx prisma migrate deploy
```

**Migration Order** (respecting foreign key dependencies):

| Step | Table | Dependencies |
|------|-------|-------------|
| 1 | `users` | None |
| 2 | `user_roles` | `users` |
| 3 | `cards` | `users` |
| 4 | `config` | `users` (updated_by) |
| 5 | `sessions` | `users` |
| 6 | `transactions` (partitioned) | `cards`, `users` |
| 7 | `payment_sessions` | `cards`, `users` |
| 8 | `sync_batches` | None |
| 9 | `sync_events` | `sync_batches`, `cards` |
| 10 | `balance_adjustments` | `cards`, `users`, `transactions` |
| 11 | `audit_log` | `users` |
| 12 | `notifications` | `users`, `cards` |
| 13 | Indexes | All tables |
| 14 | Triggers | All tables |
| 15 | RLS Policies | All tables |
| 16 | Seed data | `config`, `users` (admin) |

### 10.2 Zero-Downtime Migration Rules

| Operation | Strategy |
|-----------|----------|
| Add column | Add as nullable, backfill, then add NOT NULL constraint |
| Remove column | Remove from application first, then drop column in next migration |
| Rename column | Add new column, dual-write, backfill, switch reads, drop old |
| Add index | `CREATE INDEX CONCURRENTLY` (Prisma does this automatically) |
| Change column type | Add new column, dual-write, backfill, switch, drop old |
| Add foreign key | Add as `NOT VALID`, then `VALIDATE CONSTRAINT` |
| Partition existing table | Create new partitioned table, dual-write, backfill, cutover |

### 10.3 Rollback Strategy

```bash
# Prisma does not support automatic rollback of applied migrations.
# Strategy:
# 1. Each migration is version-controlled in git
# 2. Rollback migration is a new migration that reverses changes
# 3. For critical failures: restore from RDS snapshot (automated daily)

# Create rollback migration
npx prisma migrate dev --name rollback_<feature>

# RDS snapshot restore (last resort)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier dmtcl-restored \
  --db-snapshot-identifier dmtcl-snapshot-<timestamp>
```

### 10.4 Partition Migration (if adding to existing table)

```sql
-- Step 1: Create new partitioned table
CREATE TABLE transactions_new (LIKE transactions INCLUDING ALL)
  PARTITION BY RANGE (created_at);

-- Step 2: Create initial partitions
CREATE TABLE transactions_new_y2026m01 PARTITION OF transactions_new
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

-- Step 3: Dual-write (application writes to both)
-- Step 4: Backfill historical data
INSERT INTO transactions_new SELECT * FROM transactions;

-- Step 5: Cutover (atomic rename)
BEGIN;
  ALTER TABLE transactions RENAME TO transactions_old;
  ALTER TABLE transactions_new RENAME TO transactions;
COMMIT;

-- Step 6: Drop old table after verification
DROP TABLE transactions_old;
```

---

## 11. Sample Prisma Schema

```prisma
// schema.prisma
// DMTCL Online Card Recharge System — Prisma Schema
// PostgreSQL 16+ with partitioning support

generator client {
  provider = "prisma-client-js"
  previewFeatures = ["postgresqlExtensions"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  extensions = [pgcrypto, pg_stat_statements]
}

// ============================================
// ENUMS
// ============================================

enum UserRole {
  SUPER_ADMIN
  FINANCE_ADMIN
  OPERATIONS_ADMIN
  USER
  GUEST
}

enum UserStatus {
  ACTIVE
  SUSPENDED
  PENDING_VERIFICATION
}

enum CardStatus {
  ACTIVE
  BLOCKED
  LOST
  EXPIRED
}

enum TransactionType {
  RECHARGE
  RECHARGE_FAILED_REFUND
  FARE_DEDUCTION
  FARE_REVERSAL
  ADMIN_CREDIT
  ADMIN_DEBIT
  CARD_ISSUE_BONUS
  SYNC_CORRECTION
}

enum TransactionStatus {
  PENDING
  COMPLETED
  FAILED
  REVERSED
}

enum PaymentSessionStatus {
  INITIATED
  PROCESSING
  COMPLETED
  FAILED
  EXPIRED
  REFUNDED
}

enum TerminalType {
  GATE
  POS
  TVM
}

enum SyncEventType {
  TAP_IN
  TAP_OUT
  RECHARGE
  BALANCE_INQUIRY
}

enum SyncProcessingStatus {
  PENDING
  PROCESSED
  DUPLICATE
  ERROR
}

enum BatchStatus {
  RECEIVED
  PROCESSING
  COMPLETED
  PARTIAL_ERROR
}

enum ApprovalStatus {
  PENDING
  APPROVED
  REJECTED
  EXECUTED
}

enum NotificationType {
  RECHARGE_SUCCESS
  RECHARGE_FAILED
  LOW_BALANCE
  CARD_LINKED
  ADJUSTMENT_APPLIED
  SYNC_COMPLETE
}

enum NotificationChannel {
  SMS
  EMAIL
  PUSH
}

enum NotificationStatus {
  QUEUED
  SENT
  DELIVERED
  FAILED
  BOUNCED
}

enum NotificationLanguage {
  EN
  BN
}

// ============================================
// MODELS
// ============================================

model User {
  id                    String           @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  phone                 String           @unique(map: "users_phone_key") @db.VarChar(15)
  email                 String?          @unique(map: "users_email_key") @db.VarChar(255)
  passwordHash          String           @map("password_hash") @db.VarChar(255)
  fullNameBn            String?          @map("full_name_bn") @db.VarChar(100)
  fullNameEn            String?          @map("full_name_en") @db.VarChar(100)
  nidNumber             String?          @unique(map: "users_nid_number_key") @db.VarChar(20)
  status                UserStatus       @default(ACTIVE)
  lastLoginAt           DateTime?        @map("last_login_at") @db.Timestamptz(6)
  failedLoginAttempts   Int              @default(0) @map("failed_login_attempts")
  lockedUntil           DateTime?        @map("locked_until") @db.Timestamptz(6)
  deletedAt             DateTime?        @map("deleted_at") @db.Timestamptz(6)
  createdAt             DateTime         @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt             DateTime         @updatedAt @map("updated_at") @db.Timestamptz(6)

  roles                 UserRoleAssignment[]
  cards                 Card[]
  transactions          Transaction[]
  paymentSessions       PaymentSession[]
  balanceAdjustmentsRequested BalanceAdjustment[] @relation("AdjustmentRequester")
  balanceAdjustmentsApproved1 BalanceAdjustment[] @relation("AdjustmentApprover1")
  balanceAdjustmentsApproved2 BalanceAdjustment[] @relation("AdjustmentApprover2")
  auditLogs             AuditLog[]
  notifications         Notification[]
  sessions              Session[]
  configUpdates         Config[]

  @@index([phone], map: "idx_users_phone_active")
  @@index([status, deletedAt], map: "idx_users_status_deleted")
  @@map("users")
}

model UserRoleAssignment {
  id          String    @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId      String    @map("user_id") @db.Uuid
  role        UserRole
  grantedBy   String?   @map("granted_by") @db.Uuid
  grantedAt   DateTime  @default(now()) @map("granted_at") @db.Timestamptz(6)
  revokedAt   DateTime? @map("revoked_at") @db.Timestamptz(6)
  createdAt   DateTime  @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt   DateTime  @updatedAt @map("updated_at") @db.Timestamptz(6)

  user        User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  granter     User?     @relation("RoleGranter", fields: [grantedBy], references: [id])

  @@unique([userId, role], name: "user_roles_user_role_unique", map: "user_roles_user_role_active")
  @@index([userId], map: "idx_user_roles_user_id")
  @@index([userId, role, revokedAt], map: "idx_user_roles_user_active")
  @@map("user_roles")
}

model Card {
  id            String        @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId        String        @map("user_id") @db.Uuid
  cardNumber    String        @unique(map: "cards_card_number_key") @db.Char(16)
  cardStatus    CardStatus    @default(ACTIVE) @map("card_status")
  balance       Decimal       @default(0.00) @db.Decimal(12, 2)
  lastSyncSeq   BigInt        @default(0) @map("last_sync_seq")
  lastSyncedAt  DateTime?     @map("last_synced_at") @db.Timestamptz(6)
  issuedAt      DateTime?     @map("issued_at") @db.Timestamptz(6)
  expiresAt     DateTime?     @map("expires_at") @db.Timestamptz(6)
  deletedAt     DateTime?     @map("deleted_at") @db.Timestamptz(6)
  createdAt     DateTime      @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt     DateTime      @updatedAt @map("updated_at") @db.Timestamptz(6)

  user          User          @relation(fields: [userId], references: [id], onDelete: SetNull)
  transactions  Transaction[]
  paymentSessions PaymentSession[]
  syncEvents    SyncEvent[]
  balanceAdjustments BalanceAdjustment[]
  notifications Notification[]

  @@index([userId, deletedAt], map: "idx_cards_user_active")
  @@index([cardNumber, cardStatus, deletedAt], map: "idx_cards_active_lookup")
  @@index([cardNumber, balance, lastSyncSeq], map: "idx_cards_sync_lookup")
  @@map("cards")
}

model Transaction {
  id              String            @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  cardId          String?           @map("card_id") @db.Uuid
  userId          String?           @map("user_id") @db.Uuid
  type            TransactionType
  amount          Decimal           @db.Decimal(12, 2)
  balanceBefore   Decimal           @map("balance_before") @db.Decimal(12, 2)
  balanceAfter    Decimal           @map("balance_after") @db.Decimal(12, 2)
  status          TransactionStatus @default(PENDING)
  reference       String?           @db.VarChar(100)
  description     String?           @db.VarChar(500)
  idempotencyKey  String?           @map("idempotency_key") @db.VarChar(128)
  metadata        Json              @default("{}")
  createdAt       DateTime          @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt       DateTime          @updatedAt @map("updated_at") @db.Timestamptz(6)

  card            Card?             @relation(fields: [cardId], references: [id], onDelete: SetNull)
  user            User?             @relation(fields: [userId], references: [id], onDelete: SetNull)
  balanceAdjustment BalanceAdjustment?

  @@index([cardId, createdAt(sort: Desc)], map: "idx_transactions_card_date")
  @@index([userId, createdAt(sort: Desc)], map: "idx_transactions_user_date")
  @@index([type, status, createdAt(sort: Desc)], map: "idx_transactions_type_status")
  @@index([cardId, createdAt(sort: Desc), amount, balanceAfter, type, status], map: "idx_transactions_card_balance")
  @@index([idempotencyKey], map: "idx_transactions_idempotency")
  @@map("transactions")

  // NOTE: This table is partitioned by RANGE (created_at) monthly.
  // Prisma does not natively support partitioned tables.
  // Partition management is handled outside Prisma via SQL migrations.
  // All queries MUST include a createdAt range filter for partition pruning.
}

model PaymentSession {
  id                  String                @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  cardId              String                @map("card_id") @db.Uuid
  userId              String                @map("user_id") @db.Uuid
  bkashPaymentId      String?               @unique(map: "payment_sessions_bkash_payment_id_key") @map("bkash_payment_id") @db.VarChar(100)
  bkashTrxId          String?               @unique(map: "payment_sessions_bkash_trx_id_key") @map("bkash_trx_id") @db.VarChar(100)
  amount              Decimal               @db.Decimal(12, 2)
  status              PaymentSessionStatus  @default(INITIATED)
  idempotencyKey      String                @unique(map: "payment_sessions_idempotency_key_key") @map("idempotency_key") @db.VarChar(128)
  bkashCallbackPayload Json?                @map("bkash_callback_payload")
  expiresAt           DateTime              @map("expires_at") @db.Timestamptz(6)
  completedAt         DateTime?             @map("completed_at") @db.Timestamptz(6)
  failureReason       String?               @map("failure_reason") @db.VarChar(500)
  createdAt           DateTime              @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt           DateTime              @updatedAt @map("updated_at") @db.Timestamptz(6)

  card                Card                  @relation(fields: [cardId], references: [id], onDelete: SetNull)
  user                User                  @relation(fields: [userId], references: [id], onDelete: SetNull)

  @@index([cardId, status, createdAt(sort: Desc)], map: "idx_payment_sessions_card_status")
  @@index([userId, status, createdAt(sort: Desc)], map: "idx_payment_sessions_user_status")
  @@index([status, expiresAt], map: "idx_payment_sessions_pending")
  @@map("payment_sessions")
}

model SyncBatch {
  id              String            @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  terminalId      String            @map("terminal_id") @db.VarChar(50)
  terminalType    TerminalType      @map("terminal_type")
  stationId       String            @map("station_id") @db.VarChar(50)
  batchStatus     BatchStatus       @default(RECEIVED) @map("batch_status")
  totalEvents     Int               @map("total_events")
  processedCount  Int               @default(0) @map("processed_count")
  errorCount      Int               @default(0) @map("error_count")
  firstSequence   BigInt            @map("first_sequence")
  lastSequence    BigInt            @map("last_sequence")
  rawBatchPayload Json?             @map("raw_batch_payload")
  createdAt       DateTime          @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt       DateTime          @updatedAt @map("updated_at") @db.Timestamptz(6)

  events          SyncEvent[]

  @@index([terminalId, batchStatus, createdAt(sort: Desc)], map: "idx_sync_batches_terminal_status")
  @@index([stationId, createdAt(sort: Desc)], map: "idx_sync_batches_station_date")
  @@index([batchStatus, terminalId], map: "idx_sync_batches_processing")
  @@map("sync_batches")
}

model SyncEvent {
  id                String                @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  batchId           String                @map("batch_id") @db.Uuid
  cardId            String?               @map("card_id") @db.Uuid
  terminalId        String                @map("terminal_id") @db.VarChar(50)
  terminalType      TerminalType          @map("terminal_type")
  eventType         SyncEventType         @map("event_type")
  sequenceNumber    BigInt                @map("sequence_number")
  balanceDelta      Decimal?              @map("balance_delta") @db.Decimal(12, 2)
  eventTimestamp    DateTime              @map("event_timestamp") @db.Timestamptz(6)
  rawPayload        Json                  @map("raw_payload")
  idempotencyKey    String                @unique(map: "idx_sync_events_idempotency") @map("idempotency_key") @db.VarChar(128)
  processingStatus  SyncProcessingStatus  @default(PENDING) @map("processing_status")
  errorMessage      String?               @map("error_message") @db.VarChar(500)
  processedAt       DateTime?             @map("processed_at") @db.Timestamptz(6)
  createdAt         DateTime              @default(now()) @map("created_at") @db.Timestamptz(6)

  batch             SyncBatch             @relation(fields: [batchId], references: [id], onDelete: Cascade)
  card              Card?                 @relation(fields: [cardId], references: [id], onDelete: SetNull)

  @@index([batchId, sequenceNumber], map: "idx_sync_events_batch_seq")
  @@index([cardId, sequenceNumber(sort: Desc)], map: "idx_sync_events_card_seq")
  @@index([terminalId, sequenceNumber], map: "idx_sync_events_terminal_pending")
  @@map("sync_events")
}

model AuditLog {
  id          String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  actorId     String?  @map("actor_id") @db.Uuid
  action      String   @db.VarChar(50)
  entityType  String   @map("entity_type") @db.VarChar(50)
  entityId    String   @map("entity_id") @db.Uuid
  oldValues   Json?    @map("old_values")
  newValues   Json?    @map("new_values")
  ipAddress   String?  @map("ip_address") @db.VarChar(45)
  userAgent   String?  @map("user_agent") @db.VarChar(500)
  createdAt   DateTime @default(now()) @map("created_at") @db.Timestamptz(6)

  actor       User?    @relation(fields: [actorId], references: [id], onDelete: SetNull)

  @@index([entityType, entityId, createdAt(sort: Desc)], map: "idx_audit_log_entity")
  @@index([actorId, createdAt(sort: Desc)], map: "idx_audit_log_actor")
  @@index([action, createdAt(sort: Desc)], map: "idx_audit_log_action_date")
  @@index([entityType, entityId, createdAt(sort: Desc), action, actorId], map: "idx_audit_log_entity_covering")
  @@map("audit_log")
}

model BalanceAdjustment {
  id              String          @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  cardId          String          @map("card_id") @db.Uuid
  userId          String?         @map("user_id") @db.Uuid
  amount          Decimal         @db.Decimal(12, 2)
  reason          String          @db.VarChar(500)
  requestedBy     String          @map("requested_by") @db.Uuid
  approvedBy1     String?         @map("approved_by_1") @db.Uuid
  approvedBy2     String?         @map("approved_by_2") @db.Uuid
  approvedAt1     DateTime?       @map("approved_at_1") @db.Timestamptz(6)
  approvedAt2     DateTime?       @map("approved_at_2") @db.Timestamptz(6)
  approvalStatus  ApprovalStatus  @default(PENDING) @map("approval_status")
  rejectionReason String?         @map("rejection_reason") @db.VarChar(500)
  executedAt      DateTime?       @map("executed_at") @db.Timestamptz(6)
  transactionId   String?         @unique(map: "balance_adj_transaction_unique") @map("transaction_id") @db.Uuid
  createdAt       DateTime        @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt       DateTime        @updatedAt @map("updated_at") @db.Timestamptz(6)

  card            Card            @relation(fields: [cardId], references: [id], onDelete: SetNull)
  user            User?           @relation(fields: [userId], references: [id], onDelete: SetNull)
  requester       User            @relation("AdjustmentRequester", fields: [requestedBy], references: [id])
  approver1       User?           @relation("AdjustmentApprover1", fields: [approvedBy1], references: [id])
  approver2       User?           @relation("AdjustmentApprover2", fields: [approvedBy2], references: [id])
  transaction     Transaction?    @relation(fields: [transactionId], references: [id])

  @@index([cardId, approvalStatus, createdAt(sort: Desc)], map: "idx_balance_adj_card_status")
  @@index([requestedBy, approvalStatus, createdAt(sort: Desc)], map: "idx_balance_adj_requested_by")
  @@index([approvalStatus, cardId, amount], map: "idx_balance_adj_pending")
  @@map("balance_adjustments")
}

model Notification {
  id            String             @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId        String?            @map("user_id") @db.Uuid
  cardId        String?            @map("card_id") @db.Uuid
  type          NotificationType
  channel       NotificationChannel
  recipient     String             @db.VarChar(255)
  template      String             @db.VarChar(100)
  templateVars  Json               @default("{}") @map("template_vars")
  language      NotificationLanguage @default(EN)
  status        NotificationStatus @default(QUEUED)
  providerRef   String?            @map("provider_ref") @db.VarChar(100)
  errorMessage  String?            @map("error_message") @db.VarChar(500)
  retryCount    Int                @default(0) @map("retry_count")
  sentAt        DateTime?          @map("sent_at") @db.Timestamptz(6)
  createdAt     DateTime           @default(now()) @map("created_at") @db.Timestamptz(6)

  user          User?              @relation(fields: [userId], references: [id], onDelete: SetNull)
  card          Card?              @relation(fields: [cardId], references: [id], onDelete: SetNull)

  @@index([userId, createdAt(sort: Desc)], map: "idx_notifications_user_date")
  @@index([status, retryCount, createdAt], map: "idx_notifications_status_retry")
  @@index([cardId], map: "idx_notifications_card_id")
  @@map("notifications")
}

model Session {
  id            String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId        String   @map("user_id") @db.Uuid
  tokenHash     String   @unique(map: "idx_sessions_token_hash") @map("token_hash") @db.VarChar(128)
  expiresAt     DateTime @map("expires_at") @db.Timestamptz(6)
  ipAddress     String?  @map("ip_address") @db.VarChar(45)
  userAgent     String?  @map("user_agent") @db.VarChar(500)
  deviceInfo    Json     @default("{}") @map("device_info")
  createdAt     DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  lastActiveAt  DateTime @map("last_active_at") @db.Timestamptz(6)

  user          User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, expiresAt], map: "idx_sessions_user_active")
  @@map("sessions")
}

model Config {
  id          String   @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  key         String   @unique(map: "config_key_key") @db.VarChar(100)
  value       Json
  description String?  @db.VarChar(500)
  updatedBy   String?  @map("updated_by") @db.Uuid
  createdAt   DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt   DateTime @updatedAt @map("updated_at") @db.Timestamptz(6)

  updatedByUser User?  @relation(fields: [updatedBy], references: [id])

  @@map("config")
}
```

### 11.1 Prisma Notes & Limitations

| Feature | Prisma Support | Workaround |
|---------|---------------|------------|
| Table partitioning | ❌ Not supported | Manage partitions via raw SQL migrations; Prisma queries work transparently |
| Partial indexes | ❌ Not supported | Create via raw SQL migration after `prisma migrate deploy` |
| CHECK constraints | ❌ Not supported | Create via raw SQL migration; application-level validation as primary enforcement |
| Triggers | ❌ Not supported | Create via raw SQL migration |
| RLS policies | ❌ Not supported | Create via raw SQL migration; set `app.current_user_id` and `app.current_role` via `SET LOCAL` |
| `TIMESTAMPTZ` | ✅ Supported | Use `@db.Timestamptz(6)` |
| `NUMERIC(12,2)` | ✅ Supported | Use `@db.Decimal(12, 2)` |
| `JSONB` | ✅ Supported | Use `Json` type (Prisma maps to JSONB for PostgreSQL) |
| `UUID` default | ✅ Supported | Use `@default(dbgenerated("gen_random_uuid()"))` |
| `INET` type | ❌ Not directly | Use `@db.VarChar(45)` for IPv4/IPv6 string storage |

### 11.2 Post-Migration SQL (Run After `prisma migrate deploy`)

```sql
-- 1. Create partial indexes
CREATE INDEX CONCURRENTLY idx_users_active ON users (id, phone)
  WHERE deleted_at IS NULL AND status = 'ACTIVE';

CREATE INDEX CONCURRENTLY idx_cards_active_lookup ON cards (card_number, balance, last_sync_seq)
  WHERE deleted_at IS NULL AND card_status = 'ACTIVE';

CREATE INDEX CONCURRENTLY idx_transactions_pending ON transactions (card_id, id)
  WHERE status = 'PENDING';

CREATE INDEX CONCURRENTLY idx_transactions_idempotency ON transactions (idempotency_key)
  WHERE idempotency_key IS NOT NULL;

CREATE INDEX CONCURRENTLY idx_payment_sessions_pending ON payment_sessions (id, card_id, amount)
  WHERE status IN ('INITIATED', 'PROCESSING');

CREATE INDEX CONCURRENTLY idx_sync_events_terminal_pending ON sync_events (terminal_id, sequence_number)
  WHERE processing_status = 'PENDING';

CREATE INDEX CONCURRENTLY idx_sync_batches_processing ON sync_batches (terminal_id, id)
  WHERE batch_status IN ('RECEIVED', 'PROCESSING');

CREATE INDEX CONCURRENTLY idx_balance_adj_pending ON balance_adjustments (id, card_id, amount)
  WHERE approval_status = 'PENDING';

CREATE INDEX CONCURRENTLY idx_notifications_status_retry ON notifications (status, retry_count, created_at)
  WHERE status IN ('QUEUED', 'FAILED');

CREATE INDEX CONCURRENTLY idx_sessions_user_active ON sessions (user_id, expires_at)
  WHERE expires_at > NOW();

-- 2. Create CHECK constraints
ALTER TABLE users ADD CONSTRAINT chk_users_status
  CHECK (status IN ('ACTIVE', 'SUSPENDED', 'PENDING_VERIFICATION'));

ALTER TABLE users ADD CONSTRAINT chk_users_failed_attempts
  CHECK (failed_login_attempts >= 0 AND failed_login_attempts <= 10);

ALTER TABLE cards ADD CONSTRAINT chk_cards_balance
  CHECK (balance >= 0.00 AND balance <= 10000.00);

ALTER TABLE cards ADD CONSTRAINT chk_cards_number_format
  CHECK (card_number ~ '^[0-9]{16}$');

ALTER TABLE transactions ADD CONSTRAINT chk_transactions_balance_after
  CHECK (balance_after >= 0 AND balance_after <= 10000.00);

ALTER TABLE transactions ADD CONSTRAINT chk_transactions_amount_positive
  CHECK (amount > 0);

ALTER TABLE payment_sessions ADD CONSTRAINT chk_payment_amount_range
  CHECK (amount >= 50.00 AND amount <= 5000.00);

ALTER TABLE sync_batches ADD CONSTRAINT chk_batch_counts
  CHECK (processed_count >= 0 AND error_count >= 0
         AND processed_count + error_count <= total_events);

ALTER TABLE balance_adjustments ADD CONSTRAINT chk_adj_amount_nonzero
  CHECK (amount != 0);

ALTER TABLE balance_adjustments ADD CONSTRAINT chk_adj_different_approvers
  CHECK (approved_by_1 IS NULL OR approved_by_2 IS NULL OR approved_by_1 != approved_by_2);

ALTER TABLE balance_adjustments ADD CONSTRAINT chk_adj_approver_not_requester
  CHECK (approved_by_1 IS NULL OR approved_by_1 != requested_by);

ALTER TABLE notifications ADD CONSTRAINT chk_notification_retry_limit
  CHECK (retry_count >= 0 AND retry_count <= 5);

-- 3. Create triggers
-- (See Section 6.4 for trigger definitions)

-- 4. Enable RLS
-- (See Section 8.1 for RLS policy definitions)

-- 5. Set up transaction partitioning
-- (See Section 5 for partition management)
```

---

## Appendix A: Capacity Planning

| Metric | Value | Calculation |
|--------|-------|-------------|
| Daily transactions | 500,000 | Given |
| Monthly transactions | 15,000,000 | 500K × 30 |
| Row size (transactions) | ~350 bytes | Estimated with indexes |
| Monthly storage (transactions) | ~5.25 GB | 15M × 350 bytes |
| 5-year storage (transactions) | ~315 GB | 5.25 GB × 60 months |
| Total DB storage (all tables) | ~500 GB | Including indexes, audit log, sync data |
| Peak write IOPS | ~6,000 | 500K writes / 24h / 3600s × peak factor 10 |
| Peak read IOPS | ~15,000 | 3× write ratio for queries |
| Recommended RDS instance | db.r6g.xlarge | 4 vCPU, 32 GB RAM, EBS-optimized |
| Recommended storage | 1 TB gp3 | 3,000 IOPS baseline, burst to 16,000 |

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **bKash** | Bangladesh's largest mobile financial service (MFS) provider |
| **BDT** | Bangladeshi Taka (currency) |
| **DMTCL** | Dhaka Mass Transit Company Limited |
| **TVM** | Ticket Vending Machine |
| **POS** | Point of Sale terminal |
| **Idempotency Key** | Unique key ensuring duplicate requests produce the same result |
| **Sequence Number** | Terminal-assigned monotonic counter for ordering sync events |
| **Partition Pruning** | PostgreSQL optimization that skips irrelevant partitions |
| **RLS** | Row-Level Security — PostgreSQL feature for row-level access control |
