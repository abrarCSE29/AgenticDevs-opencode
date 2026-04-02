# Agent Swarm — Development Task Agents

This project configures specialized OpenCode subagents for executing web application development tasks. Agents produce standardized documentation and maintain project knowledge.

## Project Context

- **Domain**: Web applications (React/Next.js frontends, Node.js/Express backends, API-first architecture)
- **Documentation Output**: `projects/<project-name>/` directory (no separate docs/ subfolder)
- **Agent Interaction Model**: Orchestrator-centric pipeline where PO is the ONLY orchestrator

## Project Folder Structure

- **Base Path**: Relative to where OpenCode server starts
- **Project Folder**: `projects/<project-name>/`
- **Docs Location**: `projects/<project-name>/` (root of project folder)
- **Templates**: Reference `docs/templates/` (read-only, shared across all projects)
- **Root docs/**: Remains for shared templates only

## Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `project-orchestrator` | Primary | ONLY orchestrator. Receives project idea, delegates to agents one at a time, routes clarifications |
| `business-analyst` | Subagent | Creates BRD and PRD documents, returns to PO |
| `solution-architect` | Subagent | Reviews requirements, designs caching/RBAC/scalability, creates architecture + best practices |
| `db-sql-admin` | Subagent | Designs SQL database architecture and data models |
| `db-nosql-admin` | Subagent | Designs NoSQL database architecture and data models |
| `s3-docs-uploader` | Subagent | Uploads project docs to AWS S3 and returns public URLs |

### Switching to Orchestrator

Press **Tab** to cycle to `project-orchestrator`. Then describe your project idea and the pipeline runs automatically.

### Direct Invocation

You can also invoke agents directly:

```
@business-analyst Create a BRD for an e-commerce platform
@solution-architect Design the architecture for this project
@db-sql-admin Design the database schema for this project
@db-nosql-admin Design the NoSQL data model for this project
```

## Autonomous Workflow

The Project Orchestrator is the ONLY orchestrator. Every agent returns results to the PO, and the PO decides what to invoke next.

```
User describes project idea
        │
        ▼
┌──────────────────┐
│  Orchestrator     │  Central hub — invokes agents one at a time
└────────┬─────────┘
         │ Task tool
         ▼
┌──────────────────┐
│  Business Analyst │  Creates BRD + PRD
└────────┬─────────┘
         │ Returns to PO
         ▼
┌──────────────────┐
│  Orchestrator     │  Invokes SA next
└────────┬─────────┘
         │ Task tool
         ▼
┌──────────────────┐     Task tool     ┌──────────────────┐
│ Solution Architect│ ────────────────▶│ Business Analyst │
│  arch + best-prac │  clarification   │  (fixes gaps)    │
│                   │ ◀──────────────── │                  │
└────────┬─────────┘                   └──────────────────┘
         │ Returns to PO
         ▼
┌──────────────────┐
│  Orchestrator     │  ← asks: "SQL or NoSQL?" (optional)
└────────┬─────────┘
         │ Task tool (if user wants DB doc)
         ▼
┌──────────────────┐
│  DB Agent         │  db-sql-admin OR db-nosql-admin (optional)
└────────┬─────────┘
         │ Returns to PO
         ▼
┌──────────────────┐
│  Orchestrator     │  Invokes S3 upload
└────────┬─────────┘
         │ Task tool
         ▼
┌──────────────────┐
│  S3 Docs Uploader │  Uploads docs to S3
└────────┬─────────┘
         │ Returns URLs to PO
         ▼
┌──────────────────┐
│  Orchestrator     │  Presents final results to user
└──────────────────┘
```

### Pipeline Steps

1. **Orchestrator** receives project idea and extracts project name (converts to kebab-case)
2. **Orchestrator** creates folder: `projects/<project-name>/`
3. **Orchestrator** invokes `@business-analyst` with project description and project folder path
4. **Business Analyst** checks clarity:
   - If vague → returns `CLARIFICATION_NEEDED` to orchestrator → orchestrator asks user → re-invokes BA
   - If clear → proceeds
5. **Business Analyst** creates BRD and PRD in `projects/<project-name>/`
6. **Business Analyst** returns summary to Orchestrator
7. **Orchestrator** invokes `@solution-architect` with BRD/PRD file paths
8. **Solution Architect** reviews requirements:
   - If gaps → invokes `@business-analyst` directly for clarification → BA fixes → SA continues
   - If solid → proceeds
9. **Solution Architect** designs:
   - **Caching Strategy**: CDN/Edge, Application (Redis), HTTP caching
   - **RBAC Model**: API-level permissions + UI-level component visibility
   - **Scalability Strategy**: Per-component capacity, triggers, scaling actions
10. **Solution Architect** creates `architecture-*.md` in `projects/<project-name>/`
11. **Solution Architect** creates `best-practices-*.md` in `projects/<project-name>/`
12. **Solution Architect** returns summary to Orchestrator
13. **Orchestrator** asks user: "Would you like a database design document? SQL or NoSQL?" (optional)
14. **Orchestrator** invokes `@db-sql-admin` or `@db-nosql-admin` if user wants it
15. **DB Agent** reads BRD/PRD/architecture, designs database schema and data model
16. **DB Agent** creates `database-*.md` in `projects/<project-name>/` and returns summary to Orchestrator
17. **Orchestrator** invokes `@s3-docs-uploader` with project name and project directory path
18. **S3 Docs Uploader** uploads all docs to S3 and returns public URLs
19. **Orchestrator** presents results and S3 URLs to user

### Clarification Routing

All user-facing questions go through the orchestrator. Subagents never ask the user directly.

```
Subagent: "CLARIFICATION_NEEDED: 1. What auth method? 2. Expected users?"
    │
    ▼
Orchestrator: "The [agent] needs clarification:
               1. What authentication method do you want? (email/password, OAuth, SSO)
               2. How many users do you expect?"
    │
    ▼
User provides answers
    │
    ▼
Orchestrator re-invokes agent with clarifications appended
```

**Exception**: SA can invoke BA directly for requirement gap clarification (SA↔BA loop). This bypasses the orchestrator since it's a technical collaboration between the two agents.

Max 1 clarification round per agent. After that, agents make reasonable assumptions.

### Bidirectional Communication

- **PO → BA**: Orchestrator invokes BA to create BRD/PRD
- **BA → PO**: BA returns summary after creating BRD/PRD
- **PO → SA**: Orchestrator invokes SA to create architecture docs
- **SA → BA**: If SA finds requirement gaps, SA invokes BA directly for clarification
- **BA → SA**: BA fixes gaps and returns to SA (max 1 round)
- **SA → PO**: SA returns summary after all architecture docs created
- **PO → DB Agent**: Orchestrator invokes DB agent if user wants database design
- **DB Agent → PO**: Returns database design summary
- **PO → S3 Docs Uploader**: Orchestrator invokes S3 uploader
- **S3 Docs Uploader → PO**: Returns S3 public URLs
- **Max feedback rounds**: 1 between SA and BA (prevents infinite loops; remaining issues become assumptions)

### Solution Architect Responsibilities

The SA must address these for EVERY project:

1. **Caching Strategy**:
   - CDN/Edge caching for static assets and public pages
   - Application caching (Redis) for sessions, API responses, hot data
   - HTTP caching headers (Cache-Control, ETag)

2. **RBAC Model** (Role-Based Access Control):
   - API-level: Role → Permission → Endpoint access
   - UI-level: Role → Which components/routes are visible
   - Role hierarchy: Admin > Manager > User > Guest

3. **Scalability Strategy**:
   - Per-component capacity planning
   - Scaling triggers and actions (horizontal/vertical)
   - Rate limiting thresholds

### Safety Controls

| Agent | Max Steps | Can Invoke |
|-------|-----------|-----------|
| Orchestrator | 30 | BA, SA, db-sql-admin, db-nosql-admin, s3-docs-uploader |
| Business Analyst | 12 | None |
| Solution Architect | 18 | BA |
| DB SQL Admin | 15 | None |
| DB NoSQL Admin | 15 | None |
| S3 Docs Uploader | 8 | None |

## Documentation Standards

### File Naming
- BRD: `projects/<project-name>/brd-<project-name>.md` (e.g., `projects/ecommerce-platform/brd-ecommerce-platform.md`)
- PRD: `projects/<project-name>/prd-<project-name>.md` (e.g., `projects/ecommerce-platform/prd-ecommerce-platform.md`)
- Architecture: `projects/<project-name>/architecture-<project-name>.md`
- Best Practices: `projects/<project-name>/best-practices-<project-name>.md`
- Database: `projects/<project-name>/database-<project-name>.md`

### Templates
Use templates in `docs/templates/` as starting points. Follow the section structure defined in each template.

### Versioning
- Add a `Last Updated` date in document headers
- Reference the related BRD/PRD in architecture docs
- Cross-link documents where relevant

## Code Standards

- TypeScript with strict mode for all web application code
- Follow the architecture decisions documented by the Solution Architect
- Adhere to best practices documented in `projects/<project-name>/best-practices-*.md`
- Follow database design documented in `projects/<project-name>/database-*.md`

## General Rules

- Always generate docs in the `projects/<project-name>/` folder
- Use markdown formatting consistently across all generated documents
- Keep documents professional and suitable for stakeholder review
- Include a table of contents for documents exceeding 100 lines
- Do NOT write documentation yourself — always delegate to the appropriate agent
- The Project Orchestrator is the ONLY orchestrator — all agents return to PO
