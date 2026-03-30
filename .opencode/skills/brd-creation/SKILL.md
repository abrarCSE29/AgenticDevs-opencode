---
name: brd-creation
description: Guidelines and templates for creating Business Requirements Documents (BRD) for web application projects
license: MIT
compatibility: opencode
---

# BRD Creation Skill

Structured methodology for producing Business Requirements Documents.

## When to Use

Load this skill when the user describes a project idea and needs to formalize business requirements before development begins.

## BRD Section Guide

### 1. Executive Summary
Write 2-3 paragraphs covering:
- The business problem or opportunity
- Proposed solution at a high level
- Expected business impact

### 2. Business Objectives
List 3-5 SMART objectives:
- **Specific**: Clear outcome statement
- **Measurable**: Include a metric or KPI
- **Achievable**: Realistic given constraints
- **Relevant**: Aligned with business strategy
- **Time-bound**: Include target timeframe

Example:
- Reduce customer onboarding time from 5 days to 1 day by Q3 2026
- Achieve 95% customer satisfaction score within 6 months of launch

### 3. Stakeholders
| Role | Name/Group | Interest | Influence |
|------|-----------|----------|-----------|
| Sponsor | VP of Product | Strategic alignment | High |
| End Users | Customers | Usability, features | High |
| Development Team | Engineering | Technical feasibility | Medium |
| Operations | DevOps | Deployment, stability | Medium |

### 4. Project Scope
**In Scope:**
- Feature A, Feature B, Integration X

**Out of Scope:**
- Mobile app (Phase 2), Legacy system migration (separate project)

### 5. Functional Requirements
Organize by module or feature area. Use ID format: `FR-XXX`

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-001 | System shall support user registration via email | Must | Auth |
| FR-002 | System shall allow password reset via email link | Must | Auth |

### 6. Non-Functional Requirements
Categories: Performance, Security, Scalability, Availability, Accessibility, Compliance

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-001 | Performance | Page load time | < 2 seconds |
| NFR-002 | Security | Data encryption | AES-256 at rest |
| NFR-003 | Availability | Uptime | 99.9% |

### 7. Business Rules
Rules the system must enforce:
- BR-001: Users cannot access premium features without an active subscription
- BR-002: All financial transactions require audit logging

### 8. Constraints
- Budget limitations
- Timeline requirements
- Technology mandates
- Regulatory requirements

### 9. Assumptions
List assumptions explicitly:
- Users have modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
- Third-party API maintains 99.9% uptime
- Team has React/Node.js expertise

### 10. Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Third-party API changes | High | Medium | Abstract API layer, monitor changelog |
| Scope creep | High | High | Strict change control process |

### 11. Acceptance Criteria
Define what "done" looks like:
- All Must-have requirements implemented and tested
- Performance targets met under load testing
- Security audit passed
- User acceptance testing completed with sign-off from Product Owner

## Elicitation Questions

Ask these when the user's description is vague:
1. Who are the primary users and what problem do they face today?
2. What does success look like 6 months after launch?
3. What existing systems need to integrate with this?
4. Are there regulatory or compliance requirements?
5. What is the budget and timeline range?
