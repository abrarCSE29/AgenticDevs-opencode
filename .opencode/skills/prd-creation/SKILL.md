---
name: prd-creation
description: Guidelines and templates for creating Product Requirements Documents (PRD) with user stories and acceptance criteria for web applications
license: MIT
compatibility: opencode
---

# PRD Creation Skill

Structured methodology for producing Product Requirements Documents with user-centric specifications.

## When to Use

Load this skill after a BRD exists (or the user has clear business goals) and you need to define the product specification that developers will implement.

## PRD Section Guide

### 1. Problem Statement
Frame the user problem in this format:

> [User type] struggles with [problem] because [reason], which results in [negative impact].

Example:
> Small business owners struggle with invoice management because existing tools are too complex, which results in delayed payments and cash flow issues.

### 2. Target Users (Personas)

Create 2-4 personas:

**Persona: [Name]**
- **Role**: Their job or context
- **Demographics**: Age range, tech comfort level
- **Goals**: What they want to achieve
- **Pain Points**: Current frustrations
- **Usage Frequency**: Daily / Weekly / Monthly

### 3. Feature Overview (MoSCoW Prioritization)

| Feature | Description | Priority | Effort (T-shirt) |
|---------|-------------|----------|------------------|
| User Authentication | Email/password + OAuth | Must | M |
| Dashboard | Overview of key metrics | Must | L |
| Export to PDF | Download reports as PDF | Should | S |
| Real-time Notifications | Push notifications for updates | Could | L |
| AI Recommendations | ML-based suggestions | Won't (Phase 2) | XL |

### 4. User Stories

Use INVEST criteria: Independent, Negotiable, Valuable, Estimable, Small, Testable.

**Format**: As a [user type], I want [action/feature] so that [benefit].

**Epic: [Epic Name]**

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-001 | As a new user, I want to register with my email so that I can create an account | Must | 3 |
| US-002 | As a returning user, I want to log in with Google so that I don't need another password | Must | 5 |
| US-003 | As a user, I want to reset my password via email so that I can regain access | Must | 3 |

### 5. Acceptance Criteria

Use Given/When/Then format for each user story:

**US-001: User Registration**

```
GIVEN I am on the registration page
WHEN I enter a valid email and strong password and click "Register"
THEN my account is created and I receive a confirmation email

GIVEN I am on the registration page
WHEN I enter an email that already exists
THEN I see an error message "An account with this email already exists"

GIVEN I am on the registration page
WHEN I enter a password shorter than 8 characters
THEN I see a validation error indicating minimum password length
```

### 6. User Flows
Describe step-by-step for each major flow:

**Flow: New User Onboarding**
1. User lands on homepage
2. User clicks "Get Started"
3. User fills registration form
4. User receives verification email
5. User clicks verification link
6. User completes profile setup
7. User lands on dashboard

### 7. Wireframe References
Placeholder sections for each key screen:
- `<!-- Wireframe: Login Page -->`
- `<!-- Wireframe: Dashboard -->`
- `<!-- Wireframe: Settings -->`

### 8. Success Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| User Registration Rate | N/A | 1000 users/month | Analytics |
| Task Completion Rate | N/A | 90% | User analytics |
| Time to First Value | N/A | < 5 minutes | Session tracking |
| User Satisfaction | N/A | 4.5/5 | In-app survey |

### 9. Dependencies

| Dependency | Type | Impact | Owner |
|-----------|------|--------|-------|
| Stripe API | External | Payment processing | Stripe |
| SendGrid | External | Email delivery | SendGrid |
| Auth Service | Internal | SSO integration | Backend team |

### 10. Timeline Estimates

| Phase | Features | Duration | Dependencies |
|-------|----------|----------|-------------|
| Phase 1: Foundation | Auth, Dashboard | 4 weeks | None |
| Phase 2: Core | CRUD operations, API | 6 weeks | Phase 1 |
| Phase 3: Polish | Export, Notifications | 3 weeks | Phase 2 |

### 11. Open Questions
- Should we support multi-tenancy from day one?
- What is the SLA for third-party integrations?
- Do we need GDPR compliance for initial launch?
