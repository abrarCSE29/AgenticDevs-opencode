# Database Architecture Document

**Project Name**: [Project Name]
**Database Type**: [SQL / NoSQL]
**Database Engine**: [PostgreSQL / MongoDB / etc.]
**Version**: 1.0
**Last Updated**: [Date]
**Author**: [DB SQL Admin / DB NoSQL Admin] Agent
**Related BRD**: [docs/brd-<project-name>.md]
**Related PRD**: [docs/prd-<project-name>.md]
**Related Architecture**: [docs/architecture-<project-name>.md]
**Status**: [Draft | Review | Approved]

---

## Table of Contents

1. [Data Model Overview](#data-model-overview)
2. [Schema Design](#schema-design)
3. [Entity Relationships](#entity-relationships)
4. [Indexing Strategy](#indexing-strategy)
5. [Scaling Strategy](#scaling-strategy)
6. [Consistency & Concurrency](#consistency--concurrency)
7. [Loose Coupling Design](#loose-coupling-design)
8. [Migration Strategy](#migration-strategy)
9. [Performance Considerations](#performance-considerations)

---

## Data Model Overview

[2-3 paragraphs: what data the system manages, key entities, how they relate, why this database engine was chosen.]

### Key Entities

| Entity | Description | Estimated Volume | Growth Rate |
|--------|-------------|-----------------|-------------|
| | | | |

### Access Pattern Summary

| Operation | Frequency | Latency Target |
|-----------|-----------|----------------|
| Reads | | |
| Writes | | |

## Schema Design

### [Entity/Table Name 1]

**SQL Example:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);
```

**NoSQL Example:**
```javascript
{
  _id: ObjectId(),
  email: "user@example.com",      // unique, indexed
  name: "John Doe",
  role: "user",                    // enum: user, admin, moderator
  createdAt: ISODate(),
  updatedAt: ISODate(),
  deletedAt: null                  // soft delete
}
```

### [Entity/Table Name 2]

[Same pattern — SQL DDL or NoSQL document structure]

### [Entity/Table Name N]

[Continue for all core entities]

## Entity Relationships

### Relationship Map

```
[Entity1] ──1:N──▶ [Entity2]
[Entity1] ──M:N──▶ [Entity3] (via [junction_table/collection])
[Entity2] ──1:1──▶ [Entity4]
```

### Relationship Details

| Parent | Child | Type | FK / Reference | Cascade Rule |
|--------|-------|------|----------------|-------------|
| | | 1:N | | Soft delete |
| | | M:N | | |

## Indexing Strategy

### Index Inventory

| Table/Collection | Index Name | Columns/Fields | Type | Purpose |
|-----------------|-----------|----------------|------|---------|
| | | | B-tree / Compound / etc. | |

### Query Coverage

| Query Pattern | Index Used | Expected Scan Type |
|--------------|-----------|-------------------|
| | | Index Scan / IXSCAN |

### Indexes to Avoid

[List columns that should NOT be indexed and why]

## Scaling Strategy

### Vertical Scaling

| Setting | Value | Rationale |
|---------|-------|-----------|
| Connection pool size | | |
| Max connections | | |
| Pool timeout | | |

### Horizontal Scaling

| Strategy | Configuration | When to Trigger |
|----------|--------------|-----------------|
| Read replicas | [number] replicas | Read latency > [X]ms |
| Partitioning/Sharding | [strategy] key | Data volume > [X]GB |
| Caching | [Redis / in-memory] TTL [X]s | |

### Capacity Planning

| Metric | Current Estimate | 1 Year | 3 Year |
|--------|-----------------|--------|--------|
| Data size | | | |
| Read QPS | | | |
| Write QPS | | | |
| Connections | | | |

## Consistency & Concurrency

### Consistency Model

| Operation Type | Level | Configuration |
|---------------|-------|--------------|
| User-facing reads | | |
| Writes | | |
| Analytics/Reports | | |

### Concurrency Control

[Optimistic locking (version column), pessimistic locking, or MVCC approach]

## Loose Coupling Design

### Service Boundaries

| Service | Owns (Tables/Collections) | Accesses Externally Via |
|---------|--------------------------|----------------------|
| | | API / Event / CDC |

### Decoupling Patterns Used

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| [Materialized views / Change streams / Event tables / etc.] | | |

### Data Isolation Rules

- Rule 1: [e.g., No cross-service direct database access]
- Rule 2: [e.g., All inter-service data sync via events]
- Rule 3: [e.g., Each service has its own connection pool]

## Migration Strategy

### Migration Order

| Step | Migration | Dependencies |
|------|-----------|-------------|
| 1 | Create [table] | None |
| 2 | Create [table] | Step 1 |
| 3 | Create [indexes] | Step 1, 2 |

### Zero-Downtime Migration Rules

- Add columns as nullable first, backfill, then add NOT NULL
- Create indexes CONCURRENTLY (SQL) / in background (NoSQL)
- Never rename or drop columns in the same deployment as code changes
- Use expand-contract pattern for breaking schema changes

### Rollback Plan

[How to revert each migration step safely]

## Performance Considerations

### Expected Hot Paths

| Path | Expected Load | Optimization |
|------|--------------|-------------|
| | | |

### Query Optimization Notes

[List any known expensive queries and their optimization strategies]

### Monitoring Queries

```sql
-- Example: Check slow queries
-- Example: Check index usage
-- Example: Check connection pool status
```
