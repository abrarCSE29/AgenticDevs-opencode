# Agent Swarm — Development Task Agents

This project configures specialized OpenCode subagents for executing web application development tasks. Agents produce standardized documentation and maintain project knowledge.

## Project Context

- **Domain**: Web applications (React/Next.js frontends, Node.js/Express backends, API-first architecture)
- **Documentation Output**: `docs/` directory in the project root
- **Agent Interaction Model**: Autonomous pipeline with bidirectional feedback between agents

## Project Folder Structure

- **Base Path**: Relative to where OpenCode server starts
- **Project Folder**: `projects/<project-name>/`
- **Docs Location**: `projects/<project-name>/docs/`
- **Templates**: Reference `docs/templates/` (read-only, shared across all projects)
- **Root docs/**: Remains for shared templates only

## Agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `project-orchestrator` | Primary | Receives project idea, manages pipeline, routes clarifications |
| `business-analyst` | Subagent | Creates BRD and PRD documents |
| `solution-architect` | Subagent | Reviews requirements, designs caching/RBAC/scalability, creates architecture, delegates to DB agents |
| `db-sql-admin` | Subagent | Designs SQL database architecture and data models |
| `db-nosql-admin` | Subagent | Designs NoSQL database architecture and data models |

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

The system works as a self-managing pipeline:

```
User describes project idea
        │
        ▼
┌──────────────────┐
│  Orchestrator     │  ← asks: "SQL or NoSQL?"
└────────┬─────────┘
         │ Task tool
         ▼
┌──────────────────┐
│  Business Analyst │  BRD + PRD (DB preference noted)
└────────┬─────────┘
         │ Task tool
         ▼
┌──────────────────┐     Task tool     ┌──────────────────┐
│ Solution Architect│ ────────────────▶│ db-sql-admin OR  │
│                   │  delegates       │ db-nosql-admin   │
│                   │ ◀──────────────── │                  │
└──────────────────┘   DB design back   └──────────────────┘
         │
         ▼
  docs/brd-*.md
  docs/prd-*.md
  docs/architecture-*.md
  docs/best-practices-*.md
  docs/database-*.md
```

### Pipeline Steps

1. **Orchestrator** receives project idea and asks user: "SQL or NoSQL?"
2. **Orchestrator** extracts project name from user input (converts to kebab-case)
3. **Orchestrator** creates folder: `projects/<project-name>/docs/`
4. **Orchestrator** initializes `AGENTS.md` in the project folder
5. **Orchestrator** invokes `@business-analyst` with project description, DB preference, and project context
6. **Business Analyst** checks clarity:
   - If vague → returns `CLARIFICATION_NEEDED` to orchestrator → orchestrator asks user → re-invokes BA
   - If clear → proceeds
7. **Business Analyst** creates BRD and PRD in `projects/<project-name>/docs/` (DB preference noted in PRD)
8. **Business Analyst** invokes `@solution-architect` with BRD/PRD content and DB preference (mandatory)
9. **Solution Architect** reviews requirements:
   - If gaps → returns `CLARIFICATION_NEEDED` to orchestrator → orchestrator asks user → re-invokes SA
   - If solid → proceeds
10. **Solution Architect** collaborates with BA for requirement gaps (max 1 round)
11. **Solution Architect** designs:
    - **Caching Strategy**: CDN/Edge, Application (Redis), HTTP caching
    - **RBAC Model**: API-level permissions + UI-level component visibility
    - **Scalability Strategy**: Per-component capacity, triggers, scaling actions
12. **Solution Architect** creates `architecture-*.md` in `projects/<project-name>/docs/`
13. **Solution Architect** invokes the appropriate DB agent based on DB preference:
      - SQL → `@db-sql-admin`
      - NoSQL → `@db-nosql-admin`
14. **DB Agent** reads BRD/PRD/architecture, designs database schema and data model
15. **DB Agent** creates `database-*.md` in `projects/<project-name>/docs/`
16. **Solution Architect** creates `best-practices-*.md` in `projects/<project-name>/docs/`
17. **Solution Architect** returns summary to orchestrator
18. **Orchestrator** presents results to user

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

Max 1 clarification round per agent. After that, agents make reasonable assumptions.

### Bidirectional Communication

- **BA → SA**: After creating BRD/PRD, BA automatically invokes SA via Task tool
- **SA → BA**: If SA finds requirement gaps (missing acceptance criteria, undefined NFRs), sends structured feedback back to BA
- **BA → SA**: After fixing gaps, BA re-invokes SA with updated documents
- **SA → DB Agent**: SA delegates database design to the appropriate DB agent
- **DB Agent → SA**: DB agent returns database design to SA
- **SA → Orchestrator**: Final summary after all docs created
- **Max feedback rounds**: 1 (prevents infinite loops; remaining issues become assumptions)

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
| Orchestrator | 30 | BA, SA, db-sql-admin, db-nosql-admin |
| Business Analyst | 12 | SA |
| Solution Architect | 18 | BA, db-sql-admin, db-nosql-admin |
| DB SQL Admin | 15 | None |
| DB NoSQL Admin | 15 | None |

## Documentation Standards

### File Naming
- BRD: `projects/<project-name>/docs/brd-<project-name>.md` (e.g., `projects/ecommerce-platform/docs/brd-ecommerce-platform.md`)
- PRD: `projects/<project-name>/docs/prd-<project-name>.md` (e.g., `projects/ecommerce-platform/docs/prd-ecommerce-platform.md`)
- Architecture: `projects/<project-name>/docs/architecture-<project-name>.md`
- Best Practices: `projects/<project-name>/docs/best-practices-<project-name>.md`
- Database: `projects/<project-name>/docs/database-<project-name>.md`

### Templates
Use templates in `docs/templates/` as starting points. Follow the section structure defined in each template.

### Versioning
- Add a `Last Updated` date in document headers
- Reference the related BRD/PRD in architecture docs
- Cross-link documents where relevant

## Code Standards

- TypeScript with strict mode for all web application code
- Follow the architecture decisions documented by the Solution Architect
- Adhere to best practices documented in `docs/best-practices-*.md`
- Follow database design documented in `docs/database-*.md`

## General Rules

- Always generate docs in the `docs/` folder
- Use markdown formatting consistently across all generated documents
- Keep documents professional and suitable for stakeholder review
- Include a table of contents for documents exceeding 100 lines
- Do NOT write documentation yourself — always delegate to the appropriate agent
