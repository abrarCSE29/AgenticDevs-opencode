# Business Requirements Document (BRD)

**Project Name:** DMTCL Online Card Recharge System  
**Document Version:** 1.0  
**Last Updated:** March 31, 2026  
**Prepared By:** Business Analyst  
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives](#2-business-objectives)
3. [Stakeholders](#3-stakeholders)
4. [Project Scope](#4-project-scope)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Business Rules](#7-business-rules)
8. [Constraints](#8-constraints)
9. [Assumptions](#9-assumptions)
10. [Risks](#10-risks)
11. [Acceptance Criteria](#11-acceptance-criteria)

---

## 1. Executive Summary

Dhaka Mass Transit Company Limited (DMTCL) operates the Dhaka Metro Rail service, which uses smart cards for fare collection. Currently, users must visit physical ticket counters or kiosks to recharge their transit cards, leading to long queues, inconvenience, and limited operating hours. This creates a significant barrier to seamless transit usage and reduces customer satisfaction.

The DMTCL Online Card Recharge System is a web-based platform that enables users to recharge their transit/smart cards remotely using online payment methods, with initial integration focused on bKash — Bangladesh's leading mobile financial service. Users can register an account, link their transit card, and add funds instantly. When users tap their card at metro station gates or POS terminals, the transaction data syncs back to their account, providing real-time balance updates and a complete transaction history.

This solution will reduce dependency on physical recharge points, improve customer convenience, increase card recharge frequency, and provide DMTCL with valuable transaction data for operational analytics. The platform is expected to serve hundreds of thousands of daily metro rail users.

## 2. Business Objectives

| ID | Objective | Metric | Target | Timeframe |
|----|-----------|--------|--------|-----------|
| BO-001 | Reduce physical counter recharge volume | Percentage of recharges done online | 60% of all recharges | Within 12 months of launch |
| BO-002 | Improve customer satisfaction for card recharging | Customer satisfaction score (CSAT) | 4.2/5 or higher | Within 6 months of launch |
| BO-003 | Increase average card balance (revenue float) | Average balance per active card | 20% increase | Within 9 months of launch |
| BO-004 | Reduce average recharge time | Time from initiation to balance update | Under 30 seconds for online recharge | At launch |
| BO-005 | Achieve reliable card-to-account sync | Successful sync rate for tap transactions | 99.5% sync accuracy | Within 3 months of launch |

## 3. Stakeholders

| Role | Name/Group | Interest | Influence |
|------|-----------|----------|-----------|
| Project Sponsor | DMTCL Managing Director | Strategic alignment, ROI | High |
| End Users | Metro Rail Card Holders | Convenience, reliability, speed | High |
| Payment Partner | bKash Limited | Transaction volume, integration stability | High |
| Operations Team | DMTCL Station Staff | Reduced counter load, sync reliability | Medium |
| Development Team | Engineering & IT | Technical feasibility, maintainability | Medium |
| Finance Department | DMTCL Finance | Revenue reconciliation, audit trails | Medium |
| Regulatory Body | Bangladesh Bank | Payment compliance, data protection | High |
| Infrastructure Team | DMTCL IT Operations | System uptime, machine integration | Medium |

## 4. Project Scope

**In Scope:**
- User registration and account management (email/phone-based)
- Transit card linking to user accounts
- bKash payment gateway integration for online recharges
- Real-time balance updates after successful payment
- Card-to-account data synchronization (tap/punch at machines)
- Transaction history and balance tracking dashboard
- Admin dashboard for monitoring transactions and user accounts
- Machine/terminal API integration for offline-online sync
- Email and SMS notifications for recharge confirmations
- Role-based access control (Admin, Operator, User)

**Out of Scope:**
- Mobile native application (Phase 2 consideration)
- Integration with other payment gateways beyond bKash (Phase 2)
- Physical card issuance or replacement
- Legacy system data migration (handled as separate project)
- Multi-city transit system integration
- Loyalty or rewards program (Phase 2)

## 5. Functional Requirements

### Module: User Authentication & Account Management

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-001 | System shall allow users to register using phone number and email | Must | Auth |
| FR-002 | System shall support login via phone number/email and password | Must | Auth |
| FR-003 | System shall support OTP-based login via SMS | Should | Auth |
| FR-004 | System shall allow users to reset password via email or SMS OTP | Must | Auth |
| FR-005 | System shall allow users to update profile information (name, phone, email) | Must | Account |
| FR-006 | System shall allow users to view their account dashboard with current balance | Must | Account |

### Module: Card Management

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-007 | System shall allow users to link one or more transit cards to their account | Must | Card |
| FR-008 | System shall validate card number format before linking | Must | Card |
| FR-009 | System shall display linked card details (card number, status, balance) | Must | Card |
| FR-010 | System shall allow users to unlink/remove a card from their account | Should | Card |
| FR-011 | System shall prevent linking a card already linked to another active account | Must | Card |

### Module: Payment & Recharge

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-012 | System shall integrate with bKash payment gateway for online recharges | Must | Payment |
| FR-013 | System shall allow users to select recharge amount from predefined options or enter custom amount | Must | Payment |
| FR-014 | System shall enforce minimum and maximum recharge amount limits | Must | Payment |
| FR-015 | System shall update account balance in real-time after successful bKash payment | Must | Payment |
| FR-016 | System shall generate a unique transaction reference for each recharge | Must | Payment |
| FR-017 | System shall handle failed payment scenarios and rollback balance updates | Must | Payment |
| FR-018 | System shall send SMS and email confirmation after successful recharge | Should | Payment |

### Module: Transaction History & Reporting

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-019 | System shall display complete transaction history for each linked card | Must | History |
| FR-020 | System shall differentiate between online recharges and tap/punch transactions | Must | History |
| FR-021 | System shall allow filtering transaction history by date range and transaction type | Should | History |
| FR-022 | System shall display current balance for each linked card | Must | History |
| FR-023 | System shall allow users to download transaction history as PDF/CSV | Could | History |

### Module: Machine/Terminal Sync

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-024 | System shall receive transaction data from metro station gates and POS terminals | Must | Sync |
| FR-025 | System shall update account balance when a linked card is tapped at a machine | Must | Sync |
| FR-026 | System shall handle offline scenarios where machines sync data in batches | Must | Sync |
| FR-027 | System shall resolve conflicts when sync data arrives out of order | Must | Sync |
| FR-028 | System shall log all sync events for audit purposes | Must | Sync |

### Module: Admin Dashboard

| ID | Requirement | Priority | Module |
|----|-------------|----------|--------|
| FR-029 | System shall provide admin dashboard with overview of total transactions, revenue, and active users | Must | Admin |
| FR-030 | System shall allow admins to view and manage user accounts | Must | Admin |
| FR-031 | System shall allow admins to view all transaction records with filtering | Must | Admin |
| FR-032 | System shall allow admins to manually adjust balances (with audit trail) | Should | Admin |
| FR-033 | System shall generate daily/monthly reconciliation reports | Should | Admin |

## 6. Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-001 | Performance | Page load time for dashboard | < 2 seconds |
| NFR-002 | Performance | Balance update latency after payment | < 5 seconds |
| NFR-003 | Performance | API response time for sync endpoints | < 500ms |
| NFR-004 | Availability | System uptime | 99.9% (8.76 hours downtime/year max) |
| NFR-005 | Scalability | Concurrent users supported | 10,000 concurrent users |
| NFR-006 | Scalability | Daily transaction volume | 500,000 transactions/day |
| NFR-007 | Security | Data encryption at rest | AES-256 |
| NFR-008 | Security | Data encryption in transit | TLS 1.3 |
| NFR-009 | Security | Password storage | bcrypt with salt (cost factor 12+) |
| NFR-010 | Security | Payment data handling | PCI-DSS compliant (no card data stored) |
| NFR-011 | Compliance | Bangladesh Bank MFS regulations | Full compliance |
| NFR-012 | Compliance | Data retention policy | Transaction records retained for 5 years |
| NFR-013 | Accessibility | WCAG compliance | WCAG 2.1 Level AA |
| NFR-014 | Reliability | Data sync accuracy | 99.5% successful sync rate |
| NFR-015 | Auditability | All financial operations logged | Immutable audit trail |

## 7. Business Rules

| ID | Rule | Description |
|----|------|-------------|
| BR-001 | Minimum recharge amount | Users cannot recharge less than BDT 50 |
| BR-002 | Maximum recharge amount | Users cannot recharge more than BDT 5,000 per transaction |
| BR-003 | Maximum card balance | A card cannot hold more than BDT 10,000 total balance |
| BR-004 | Card linking limit | A user account can link up to 5 transit cards |
| BR-005 | Exclusive card linking | A transit card can only be linked to one active user account at a time |
| BR-006 | Transaction immutability | Once a transaction is recorded, it cannot be deleted (only reversed with admin approval) |
| BR-007 | Balance cannot go negative | Card balance cannot drop below BDT 0 |
| BR-008 | Sync priority | Online recharge balance updates take priority over tap/punch sync updates |
| BR-009 | Admin balance adjustment | Any manual balance adjustment requires dual admin approval and is fully audited |
| BR-010 | Session timeout | User sessions expire after 30 minutes of inactivity |

## 8. Constraints

| ID | Constraint | Description |
|----|-----------|-------------|
| C-001 | Payment gateway | Initial launch limited to bKash integration only |
| C-002 | Regulatory | Must comply with Bangladesh Bank regulations for mobile financial services |
| C-003 | Infrastructure | Must integrate with existing DMTCL card reader hardware and protocols |
| C-004 | Timeline | Phase 1 launch targeted within 6 months |
| C-005 | Budget | Development and infrastructure costs within approved DMTCL IT budget |
| C-006 | Technology | Database must use SQL-based RDBMS for transaction integrity |
| C-007 | Language | UI must support both Bengali and English |

## 9. Assumptions

| ID | Assumption | Description |
|----|-----------|-------------|
| A-001 | bKash API availability | bKash payment API maintains 99.9% uptime and provides adequate documentation |
| A-002 | Machine connectivity | Metro station gates and POS terminals have network connectivity for sync |
| A-003 | Card format | Transit cards use a consistent, standardized card number format |
| A-004 | User devices | Users have access to smartphones or computers with modern browsers |
| A-005 | SMS delivery | SMS gateway for OTP and notifications maintains reliable delivery |
| A-006 | Existing infrastructure | DMTCL provides necessary APIs/endpoints for machine data integration |
| A-007 | Team expertise | Development team has experience with payment gateway integrations |

## 10. Risks

| ID | Risk | Impact | Probability | Mitigation |
|----|------|--------|-------------|------------|
| R-001 | bKash API changes or downtime | High | Medium | Abstract payment layer, implement retry logic, maintain fallback recharge methods |
| R-002 | Machine sync failures causing balance discrepancies | High | Medium | Implement robust conflict resolution, daily reconciliation jobs, user dispute process |
| R-003 | High traffic during peak hours causing system slowdown | High | Medium | Auto-scaling infrastructure, CDN caching, rate limiting, load testing |
| R-004 | Fraudulent recharge attempts or payment disputes | High | Low | Transaction monitoring, fraud detection rules, bKash dispute resolution process |
| R-005 | Data breach of user financial information | Critical | Low | Encryption at rest and in transit, regular security audits, PCI-DSS compliance |
| R-006 | Regulatory changes affecting MFS operations | Medium | Medium | Maintain legal counsel relationship, design flexible compliance layer |
| R-007 | Scope creep adding features beyond Phase 1 | Medium | High | Strict change control, clear Phase 1/Phase 2 boundaries |
| R-008 | Legacy machine incompatibility with new sync protocol | High | Medium | Early integration testing with DMTCL hardware team, protocol abstraction layer |

## 11. Acceptance Criteria

The project will be considered complete when:

1. All Must-have functional requirements (FR-001 through FR-033 marked as Must) are implemented, tested, and verified
2. bKash payment integration successfully processes test and live transactions with 99.9% success rate
3. Real-time balance updates occur within 5 seconds of successful payment
4. Card-to-account sync achieves 99.5% accuracy rate in integration testing
5. System handles 10,000 concurrent users without performance degradation
6. Security audit passes with no critical or high-severity findings
7. User acceptance testing completed with sign-off from DMTCL Product Owner
8. Admin dashboard provides complete transaction visibility and reporting capabilities
9. All business rules (BR-001 through BR-010) are enforced and tested
10. System achieves 99.9% uptime during 30-day stability testing period
11. Bengali and English language support verified across all user-facing screens
12. Audit trail captures all financial operations with immutable logging
