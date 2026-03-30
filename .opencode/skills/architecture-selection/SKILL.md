---
name: architecture-selection
description: Framework for selecting web application architecture patterns and documenting technical decisions
license: MIT
compatibility: opencode
---

# Architecture Selection Skill

Decision framework for choosing and documenting web application architecture.

## When to Use

Load this skill when you need to select an architecture pattern, choose a technology stack, or create architecture documentation for a web application.

## Architecture Patterns for Web Applications

### Monolith (Recommended for most web apps)

**Use when:**
- Team size: 1-5 developers
- Project is new or has moderate complexity
- Fast time-to-market is important
- Team is co-located or small

**Stack example:**
- Frontend: Next.js (React) with App Router
- Backend: Next.js API Routes or Express.js
- Database: PostgreSQL with Prisma ORM
- Deployment: Vercel or AWS ECS

**Pros:** Simple deployment, easy debugging, fast development
**Cons:** Scaling is vertical only, single point of failure

### Microservices

**Use when:**
- Team size: 5+ developers across multiple teams
- Different parts of the system have vastly different scaling needs
- Teams need independent deployment cycles
- Clear domain boundaries exist

**Stack example:**
- Frontend: Next.js BFF (Backend for Frontend)
- Services: Node.js/Go services per domain
- Communication: REST + Message Queue (RabbitMQ/Kafka)
- Database: Service-per-database pattern
- Orchestration: Kubernetes
- API Gateway: Kong or AWS API Gateway

**Pros:** Independent scaling, technology flexibility, team autonomy
**Cons:** Distributed system complexity, network latency, operational overhead

### Serverless

**Use when:**
- Traffic is unpredictable or spiky
- Cost optimization for low-traffic apps
- Event-driven workloads
- Small team or solo developer

**Stack example:**
- Frontend: Next.js on Vercel
- API: AWS Lambda + API Gateway
- Database: DynamoDB or PlanetScale
- Storage: S3
- Auth: Auth0 or Clerk

**Pros:** Pay per use, auto-scaling, no server management
**Cons:** Cold starts, vendor lock-in, debugging complexity

### Jamstack (Static + API)

**Use when:**
- Content-heavy sites (blogs, docs, marketing)
- SEO is critical
- Performance is priority
- Simple data requirements

**Stack example:**
- Frontend: Next.js/Remix with SSG
- CMS: Contentful/Sanity/Strapi
- CDN: Cloudflare/Vercel Edge
- Forms: Formspree/Netlify Forms

**Pros:** Excellent performance, high security, low cost
**Cons:** Limited dynamic functionality, build times for large sites

## Decision Matrix

| Criterion | Weight | Monolith | Microservices | Serverless | Jamstack |
|-----------|--------|----------|---------------|------------|----------|
| Time to market | 25% | 5 | 2 | 4 | 5 |
| Scalability | 20% | 3 | 5 | 5 | 4 |
| Team velocity | 20% | 5 | 3 | 4 | 4 |
| Operational cost | 15% | 4 | 2 | 4 | 5 |
| Complexity | 10% | 5 | 2 | 3 | 5 |
| Flexibility | 10% | 3 | 5 | 3 | 2 |
| **Weighted Score** | | **4.2** | **3.0** | **4.0** | **4.3** |

Score 1-5 for each. Multiply by weight. Higher is better.

## Technology Stack Evaluation

### Frontend
| Framework | Best For | SSR | SSG | Learning Curve |
|-----------|----------|-----|-----|---------------|
| Next.js | Full-stack web apps | Yes | Yes | Medium |
| Remix | Progressive enhancement | Yes | No | Medium |
| Astro | Content sites | No | Yes | Low |
| Vite + React | SPAs | No | No | Low |

### Backend
| Framework | Best For | Performance | Ecosystem |
|-----------|----------|-------------|-----------|
| Express.js | General purpose | Good | Excellent |
| Fastify | High performance | Excellent | Good |
| NestJS | Enterprise | Good | Excellent |
| Hono | Edge/lightweight | Excellent | Growing |

### Database
| Database | Best For | Type | Scaling |
|----------|----------|------|---------|
| PostgreSQL | Relational data, complex queries | Relational | Vertical + Read replicas |
| MongoDB | Document storage, rapid prototyping | Document | Horizontal sharding |
| Redis | Caching, sessions, real-time | Key-value | Clustering |
| PlanetScale | MySQL-compatible, serverless | Relational | Horizontal |

## Architecture Decision Record (ADR) Format

Use this template for each significant decision:

```markdown
## ADR-XXX: [Decision Title]

**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Date**: YYYY-MM-DD
**Deciders**: [List of people involved]

### Context
What is the issue that we're seeing that is motivating this decision?

### Decision Drivers
- Driver 1
- Driver 2

### Considered Options
1. Option A — description
2. Option B — description
3. Option C — description

### Decision Outcome
**Chosen option**: "[Option X]", because [justification].

### Consequences
**Positive:**
- Benefit 1
- Benefit 2

**Negative:**
- Trade-off 1
- Trade-off 2

### Related Decisions
- Links to related ADRs
```

## Default Recommendation

For new web application projects with typical requirements:
- **Architecture**: Monolith (Next.js full-stack)
- **Database**: PostgreSQL + Prisma ORM
- **Auth**: NextAuth.js or Clerk
- **Deployment**: Vercel or Docker on AWS
- **CI/CD**: GitHub Actions

This can evolve into microservices later if scaling demands it. Start simple.
