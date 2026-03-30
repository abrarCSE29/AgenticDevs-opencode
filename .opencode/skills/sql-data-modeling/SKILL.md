---
name: sql-data-modeling
description: Schema design patterns, normalization, indexing strategies, and scaling techniques for SQL databases
license: MIT
compatibility: opencode
---

# SQL Data Modeling Skill

Patterns and best practices for designing scalable SQL database architectures.

## When to Use

Load this skill when designing a SQL database schema, creating indexing strategies, or planning database scaling.

## Schema Design Patterns

### Normalization Levels

| Level | Rule | When to Use |
|-------|------|-------------|
| 1NF | Atomic values, no repeating groups | Always |
| 2NF | No partial dependencies | Always |
| 3NF | No transitive dependencies | Default target |
| BCNF | Every determinant is a candidate key | High integrity needs |
| 4NF | No multi-valued dependencies | Rarely needed |

**Default**: Target 3NF. Denormalize intentionally with justification.

### Common Denormalization Patterns

| Pattern | Use Case | Trade-off |
|---------|----------|-----------|
| Redundant columns | Avoid expensive JOINs | Update anomalies |
| Materialized views | Complex aggregations | Staleness |
| Summary tables | Dashboard metrics | Maintenance overhead |
| JSON columns | Semi-structured data | Query complexity |

### Primary Key Strategies

| Strategy | Best For | Example |
|----------|----------|---------|
| UUID v4 | Distributed systems, microservices | `gen_random_uuid()` |
| UUID v7 | Distributed + time-ordered | Sortable by creation time |
| Auto-increment | Single instance, simple apps | `SERIAL` / `BIGSERIAL` |
| Natural key | Domain-defined unique identifier | Email, ISBN |

**Recommendation**: Use UUID v7 for web apps (distributed-safe + sortable).

## Indexing Strategies

### Index Types

| Type | Use Case | PostgreSQL Syntax |
|------|----------|-------------------|
| B-tree (default) | Equality, range,排序 | `CREATE INDEX idx ON t(col)` |
| Hash | Equality only | `CREATE INDEX idx ON t USING hash(col)` |
| GIN | Arrays, JSONB, full-text | `CREATE INDEX idx ON t USING gin(col)` |
| GiST | Geometric, range types | `CREATE INDEX idx ON t USING gist(col)` |
| Partial | Filtered subset | `CREATE INDEX idx ON t(col) WHERE status = 'active'` |
| Covering (INCLUDE) | Read-heavy, avoid table lookup | `CREATE INDEX idx ON t(col) INCLUDE (other)` |
| Composite | Multi-column queries | `CREATE INDEX idx ON t(col1, col2)` |

### Index Rules

- Index columns used in WHERE, JOIN, ORDER BY
- Composite index: order by selectivity (most selective first)
- Avoid indexing: low-cardinality columns, frequently updated columns, small tables
- Monitor with `pg_stat_user_indexes` — drop unused indexes

### Index Sizing Estimate

```
Index size ≈ (row_size + overhead) × row_count × 1.5
```

Keep total index size under available RAM for best performance.

## Partitioning Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| Range | Time-series, sequential data | `PARTITION BY RANGE (created_at)` |
| List | Known categories | `PARTITION BY LIST (region)` |
| Hash | Even distribution | `PARTITION BY HASH (user_id)` |

### Partition Rules

- Partition key should be in most WHERE clauses
- Aim for partitions of 10-50GB each
- Create partitions ahead of time (automate with pg_partman)
- Use `DEFAULT` partition as catch-all

## Connection Pooling

| Setting | Recommendation |
|---------|---------------|
| Pool size | `2 × CPU cores + effective_spindle_count` |
| Max connections | 100-200 per PostgreSQL instance |
| Pool timeout | 30 seconds |
| Idle timeout | 10 minutes |
| Tool | PgBouncer (transaction mode) |

## Replication Patterns

| Pattern | Use Case | Consistency |
|---------|----------|-------------|
| Primary-Replica | Read scaling | Eventual (replica lag) |
| Synchronous Replica | Zero data loss | Strong (write latency) |
| Multi-primary | Geo-distribution | Conflict resolution needed |

**Default**: Primary + 1-2 async replicas for read scaling.

## Loose Coupling Patterns

| Pattern | Description |
|---------|-------------|
| Service-owned schemas | Each service has its own schema, no cross-schema joins |
| Materialized views | Decouple reporting from operational tables |
| Event tables | Write domain events, other services consume via CDC |
| API abstraction | Services query via API, never direct DB access |
| Soft deletes | `deleted_at TIMESTAMP` instead of `DELETE` for audit safety |

## Migration Best Practices

- Use a migration tool (Prisma, Flyway, Alembic)
- Never modify migrations that are already deployed
- Add columns as nullable first, backfill, then add NOT NULL
- Create indexes CONCURRENTLY in production
- Test migrations against production-size data
- Always have a rollback plan
