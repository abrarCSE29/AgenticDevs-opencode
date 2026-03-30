---
name: nosql-data-modeling
description: Document modeling, sharding strategies, consistency patterns, and denormalization for NoSQL databases
license: MIT
compatibility: opencode
---

# NoSQL Data Modeling Skill

Patterns and best practices for designing scalable NoSQL database architectures.

## When to Use

Load this skill when designing a NoSQL database schema, choosing a NoSQL pattern, or planning NoSQL scaling strategy.

## NoSQL Pattern Selection

### Decision Matrix

| Data Shape | Access Pattern | Best Fit | Default Product |
|-----------|---------------|----------|-----------------|
| Hierarchical/nested | CRUD, flexible queries | Document | MongoDB |
| Simple key→value | High throughput, low latency | Key-Value | Redis |
| Time-ordered | Range queries by time | Time-Series | InfluxDB / TimescaleDB |
| Wide rows, write-heavy | Partition-tolerant writes | Column-Family | Cassandra |
| Highly connected | Traversal, shortest path | Graph | Neo4j |

### MongoDB (Document Store — Default)

Best for: General web applications, flexible schemas, nested data.

### Redis (Key-Value)

Best for: Caching, sessions, rate limiting, real-time leaderboards.

### Cassandra (Column-Family)

Best for: Write-heavy workloads, time-series at massive scale, geo-distributed.

## Document Modeling (MongoDB)

### Embedding vs Referencing

| Pattern | When to Use | Example |
|---------|------------|---------|
| Embed | 1:1, 1:few, data accessed together | `{ user: { address: {} } }` |
| Reference | 1:many (unbounded), many:many, large documents | `{ userId: ObjectId("...") }` |

### Embedding Rules

- Embed when child data is always read with parent
- Embed when child data is bounded (< 100-500 items)
- Embed when updates are infrequent
- Keep documents under 16MB (BSON limit)

### Reference Rules

- Reference when child data is unbounded
- Reference when child data is read independently
- Reference when child data is shared across parents
- Use application-level JOINs or `$lookup` sparingly

### Document Schema Design

```javascript
// Good: Embedded for bounded, co-accessed data
{
  _id: ObjectId(),
  name: "Project Alpha",
  status: "active",
  owner: { id: ObjectId(), name: "John" },
  settings: { visibility: "private", notifications: true },
  createdAt: ISODate()
}

// Good: Referenced for unbounded data
// projects collection
{ _id: ObjectId("proj1"), name: "Project Alpha", taskCount: 42 }
// tasks collection
{ _id: ObjectId(), projectId: ObjectId("proj1"), title: "Fix bug" }
```

### Schema Validation

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name", "createdAt"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+$" },
        name: { bsonType: "string", minLength: 1 },
        role: { enum: ["user", "admin", "moderator"] }
      }
    }
  }
})
```

## Sharding Strategy

### Shard Key Selection

| Key Property | Distribution | Query Locality | Example |
|-------------|-------------|---------------|---------|
| High cardinality | Even | Poor | `_id`, `userId` (hashed) |
| Low cardinality | Poor (hot shards) | Good | `region`, `status` |
| Compound | Balanced | Balanced | `{ region: 1, _id: 1 }` |

### Shard Key Rules

- **High cardinality**: Many possible values
- **Even distribution**: Avoid hot shards
- **Query locality**: Queries should target few shards when possible
- **Non-monotonically changing**: Avoid auto-increment or timestamp-only keys

### Recommended Shard Keys

| Workload | Shard Key | Rationale |
|----------|-----------|-----------|
| User-centric | `userId` (hashed) | Even distribution, user queries hit one shard |
| Time-series | `{ timestamp: 1, _id: 1 }` | Range queries work, compound avoids hot shard |
| Multi-tenant | `tenantId` (hashed) | Tenant isolation, even distribution |

## Consistency Models

| Model | Guarantee | Use Case | Trade-off |
|-------|-----------|----------|-----------|
| Strong | All reads see latest write | Payments, inventory | Higher latency |
| Eventual | Reads may be stale briefly | Social feeds, analytics | Lower latency |
| Causal | Preserves cause-effect ordering | Chat, collaborative editing | Medium complexity |

### MongoDB Read/Write Concerns

```javascript
// Strong consistency
db.collection.findOne({}, { readConcern: { level: "majority" } })
db.collection.insertOne(doc, { writeConcern: { w: "majority", j: true } })

// Eventual consistency (performance)
db.collection.findOne({}, { readConcern: { level: "local" } })
db.collection.insertOne(doc, { writeConcern: { w: 1 } })
```

## Denormalization Patterns

| Pattern | Description | Trade-off |
|---------|-------------|-----------|
| Duplication | Copy data across documents | Storage vs read speed |
| Materialized views | Pre-computed aggregations | Staleness vs query speed |
| Bucketing | Group time-series into buckets | Update complexity vs query speed |
| Approximation | HyperLogLog for counts | Accuracy vs memory |

## Indexing (MongoDB)

### Index Types

| Type | Use Case | Example |
|------|----------|---------|
| Single field | Equality queries | `{ email: 1 }` |
| Compound | Multi-field queries | `{ status: 1, createdAt: -1 }` |
| Multikey | Array fields | `{ tags: 1 }` |
| Text | Full-text search | `{ title: "text", body: "text" }` |
| TTL | Auto-expire documents | `{ createdAt: 1 }, { expireAfterSeconds: 3600 }` |
| Partial | Subset of documents | `{ status: 1 }, { partialFilterExpression: { status: "active" } }` |

### Index Rules

- Cover queries with indexes (all WHERE/JOIN/SORT fields in index)
- ESR rule: Equality → Sort → Range in compound index order
- Avoid multikey compound indexes (only one array field per index)
- Monitor with `db.collection.explain()` — check for COLLSCAN

## Loose Coupling Patterns

| Pattern | Description |
|---------|-------------|
| Bounded contexts | Each service owns its collections |
| Change streams | Real-time event notifications on data changes |
| Event sourcing | Store events, derive state |
| Outbox pattern | Write event + data in same transaction |
| Idempotent writes | Use `_id` or unique keys for safe retries |
| CDC (Change Data Capture) | Debezium/Atlas Sync for cross-service data flow |

## Connection Pooling (MongoDB)

| Setting | Recommendation |
|---------|---------------|
| Max pool size | 100 (default) |
| Min pool size | Match steady-state connections |
| Max idle time | 10 seconds |
| Wait queue timeout | 5 seconds |

The MongoDB driver handles pooling internally — configure via connection string.

## Caching Strategy

| Layer | Technology | TTL | Use Case |
|-------|-----------|-----|----------|
| Application | Redis / node-cache | 5-60s | Hot queries, sessions |
| Database | MongoDB in-memory | N/A | Working set in RAM |
| CDN | Cloudflare / Vercel | 1h-24h | Public content |
| Query result | Application | 30-300s | Expensive aggregations |
