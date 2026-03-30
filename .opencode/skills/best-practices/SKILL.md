---
name: best-practices
description: Web application best practices covering code quality, security, performance, testing, and DevOps
license: MIT
compatibility: opencode
---

# Web Application Best Practices Skill

Comprehensive development standards for modern web applications.

## When to Use

Load this skill when defining coding standards, reviewing implementations, or creating a best practices guide for a web application project.

## Code Organization

### Project Structure (Next.js)

```
src/
├── app/                    # App Router pages and layouts
│   ├── (auth)/            # Auth route group
│   ├── (dashboard)/       # Dashboard route group
│   ├── api/               # API routes
│   └── layout.tsx
├── components/
│   ├── ui/                # Primitive UI components (Button, Input, Card)
│   ├── forms/             # Form components
│   └── features/          # Feature-specific components
├── lib/
│   ├── db.ts              # Database client
│   ├── auth.ts            # Auth configuration
│   └── utils.ts           # Shared utilities
├── hooks/                 # Custom React hooks
├── types/                 # TypeScript type definitions
├── services/              # Business logic and API calls
└── constants/             # App-wide constants
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Hooks | camelCase with `use` prefix | `useAuth.ts` |
| Utilities | camelCase | `formatDate.ts` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL` |
| Types/Interfaces | PascalCase | `interface UserProfile` |
| Files (non-component) | kebab-case | `api-client.ts` |
| CSS Modules | PascalCase matching component | `UserProfile.module.css` |

## Coding Standards

### TypeScript
- Enable `strict: true` in tsconfig.json
- Avoid `any` — use `unknown` and narrow with type guards
- Use `interface` for object shapes, `type` for unions/intersections
- Prefer `readonly` for immutable properties
- Use discriminated unions for state management

### React/Next.js
- Server Components by default, `"use client"` only when needed
- Keep components small (< 150 lines)
- Extract business logic to custom hooks
- Use React Server Components for data fetching
- Co-locate related files (component + test + styles)

## Security Guidelines

### OWASP Top 10 Coverage

1. **Injection**: Use parameterized queries (Prisma, prepared statements)
2. **Broken Authentication**: Use established auth libraries (NextAuth, Clerk)
3. **Sensitive Data Exposure**: Encrypt at rest and in transit (HTTPS everywhere)
4. **XML External Entities**: N/A for JSON-based APIs
5. **Broken Access Control**: Implement RBAC at API and UI level
6. **Security Misconfiguration**: Remove default credentials, disable debug in production
7. **XSS**: Sanitize user input, use React's built-in escaping, CSP headers
8. **Insecure Deserialization**: Validate input schemas (Zod, Yup)
9. **Using Components with Known Vulnerabilities**: `npm audit`, Dependabot
10. **Insufficient Logging**: Log auth events, admin actions, errors

### Input Validation
- Validate on both client and server
- Use schema validation (Zod) for API inputs
- Sanitize HTML content (DOMPurify)
- Rate limit API endpoints

### Secrets Management
- Never commit secrets to version control
- Use environment variables with `.env.local`
- Use secret management services (AWS Secrets Manager, Vercel Environment Variables)
- Rotate secrets regularly

## Performance Optimization

### Frontend
- Use Next.js Image component for automatic optimization
- Implement lazy loading for below-the-fold content
- Use React.lazy() and Suspense for code splitting
- Minimize bundle size: analyze with `@next/bundle-analyzer`
- Use SWR or React Query for client-side caching
- Implement virtual scrolling for long lists

### Backend
- Use database connection pooling (Prisma connection limit)
- Implement Redis caching for frequently accessed data
- Use pagination for list endpoints (cursor-based preferred)
- Optimize database queries: use indexes, avoid N+1 queries
- Implement request deduplication

### Database
- Add indexes for frequently queried columns
- Use database-level constraints (not just app-level)
- Implement soft deletes for audit trails
- Use transactions for multi-step operations
- Monitor slow queries

## Testing Strategy

### Test Pyramid
```
       /  E2E  \         ~10% (Critical user flows)
      /----------\
     / Integration \     ~30% (API, component integration)
    /--------------\
   /    Unit Tests   \   ~60% (Functions, hooks, utils)
  /__________________\
```

### Coverage Targets
- Unit tests: 80%+ coverage
- Integration tests: All API endpoints
- E2E tests: Critical user journeys (auth, checkout, core CRUD)

### Testing Tools
| Layer | Tool | Purpose |
|-------|------|---------|
| Unit | Vitest | Fast unit tests |
| Component | Testing Library | React component tests |
| Integration | Vitest + Supertest | API testing |
| E2E | Playwright | Browser automation |
| Visual | Chromatic | Visual regression |

## DevOps & CI/CD

### Branch Strategy
- `main` — production-ready code
- `develop` — integration branch (optional for small teams)
- `feature/*` — feature branches
- `fix/*` — bug fix branches
- Hotfixes branch from `main`

### CI Pipeline (GitHub Actions)
```yaml
# Recommended stages:
1. Lint & Type Check
2. Unit Tests
3. Build
4. Integration Tests
5. E2E Tests (on PR to main)
6. Deploy Preview (Vercel preview)
7. Deploy Production (merge to main)
```

### Deployment
- Use preview deployments for PRs
- Blue/green or canary deployments for production
- Feature flags for gradual rollouts
- Automated rollback on health check failure

## Code Review Checklist

- [ ] Code follows naming conventions and project structure
- [ ] TypeScript strict mode compliance (no `any`)
- [ ] Input validation on all API endpoints
- [ ] Error handling with appropriate user feedback
- [ ] Unit tests added for new logic
- [ ] No hardcoded values (use constants/env vars)
- [ ] Performance considered (unnecessary re-renders, N+1 queries)
- [ ] Security implications reviewed
- [ ] Documentation updated if API changes
- [ ] Accessibility basics (alt text, keyboard navigation, ARIA labels)
