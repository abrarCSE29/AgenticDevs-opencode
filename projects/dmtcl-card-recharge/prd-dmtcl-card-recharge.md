# Product Requirements Document (PRD)

**Project Name:** DMTCL Online Card Recharge System  
**Document Version:** 1.0  
**Last Updated:** March 31, 2026  
**Prepared By:** Business Analyst  
**Status:** Draft  
**Related Documents:** [BRD - DMTCL Card Recharge](brd-dmtcl-card-recharge.md)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Target Users (Personas)](#2-target-users-personas)
3. [Feature Overview (MoSCoW Prioritization)](#3-feature-overview-moscow-prioritization)
4. [User Stories](#4-user-stories)
5. [Acceptance Criteria](#5-acceptance-criteria)
6. [User Flows](#6-user-flows)
7. [Wireframe References](#7-wireframe-references)
8. [Success Metrics](#8-success-metrics)
9. [Dependencies](#9-dependencies)
10. [Technology Assumptions](#10-technology-assumptions)
11. [Timeline Estimates](#11-timeline-estimates)
12. [Open Questions](#12-open-questions)

---

## 1. Problem Statement

Metro rail commuters in Dhaka struggle with recharging their transit cards because they must visit physical ticket counters or kiosks, which results in long queues, wasted time, limited operating hours, and a frustrating user experience that discourages public transit adoption.

Additionally, DMTCL operations staff struggle with managing high volumes of in-person recharge requests at counters, which results in understaffed stations during peak hours, increased operational costs, and inability to provide real-time transaction visibility to management.

## 2. Target Users (Personas)

### Persona: Rahim - Daily Commuter
- **Role**: Office worker who uses metro rail daily
- **Demographics**: Age 25-45, tech-comfortable, uses smartphone regularly
- **Goals**: Recharge card quickly without waiting in line, track spending, ensure sufficient balance
- **Pain Points**: Long queues at counters during rush hour, counter closes early, no way to check balance remotely
- **Usage Frequency**: Daily (2-4 recharges per month)

### Persona: Fatima - Occasional Traveler
- **Role**: Student who uses metro rail 2-3 times per week
- **Demographics**: Age 18-25, very tech-comfortable, prefers mobile-first experiences
- **Goals**: Recharge small amounts frequently, monitor balance to avoid running out mid-journey
- **Pain Points**: Forgets to recharge until card is empty, no easy way to check balance, limited cash on hand
- **Usage Frequency**: 2-3 times per week (weekly recharges)

### Persona: Mr. Hassan - Station Operations Manager
- **Role**: DMTCL station manager overseeing ticket counters
- **Demographics**: Age 35-55, moderate tech comfort, uses desktop systems
- **Goals**: Reduce counter queue length, monitor station transaction volumes, resolve user complaints
- **Pain Points**: Overwhelmed counters during peak hours, no real-time visibility into online vs offline recharges, manual reconciliation
- **Usage Frequency**: Daily (admin dashboard monitoring)

### Persona: Nusrat - DMTCL Finance Analyst
- **Role**: Finance team member responsible for revenue reconciliation
- **Demographics**: Age 28-40, high tech comfort, uses desktop extensively
- **Goals**: Accurate daily reconciliation, audit-ready transaction records, automated reporting
- **Pain Points**: Manual reconciliation between bKash settlements and card transactions, time-consuming report generation
- **Usage Frequency**: Daily (reporting and reconciliation)

## 3. Feature Overview (MoSCoW Prioritization)

| Feature | Description | Priority | Effort (T-shirt) |
|---------|-------------|----------|------------------|
| User Registration & Login | Phone/email-based registration with password and OTP login | Must | M |
| Card Linking | Link transit cards to user account with validation | Must | M |
| bKash Payment Integration | Online recharge via bKash payment gateway | Must | L |
| Real-Time Balance Update | Instant balance reflection after successful payment | Must | M |
| Transaction History | View all recharges and tap transactions with filtering | Must | M |
| Machine Sync API | Receive and process tap/punch data from station gates | Must | XL |
| Admin Dashboard | Monitor transactions, users, and system health | Must | L |
| SMS/Email Notifications | Confirmations for recharges and low balance alerts | Should | M |
| OTP-Based Login | Passwordless login via SMS OTP | Should | S |
| Balance Adjustment (Admin) | Manual balance correction with audit trail | Should | M |
| Transaction Export | Download history as PDF/CSV | Could | S |
| Bengali Language Support | Full UI localization for Bengali | Should | L |
| Reconciliation Reports | Automated daily/monthly financial reports | Should | M |
| Multi-Payment Gateway | Support for additional payment methods (Nagad, Rocket) | Won't (Phase 2) | L |
| Mobile Native App | iOS and Android native applications | Won't (Phase 2) | XL |
| Loyalty/Rewards Program | Points and rewards for frequent recharges | Won't (Phase 2) | M |

## 4. User Stories

### Epic: User Authentication & Account Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-001 | As a new user, I want to register with my phone number and email so that I can create an account | Must | 5 |
| US-002 | As a registered user, I want to log in with my credentials so that I can access my account | Must | 3 |
| US-003 | As a user who forgot my password, I want to reset it via email or SMS OTP so that I can regain access | Must | 5 |
| US-004 | As a user, I want to update my profile information so that my account details stay current | Must | 3 |
| US-005 | As a user, I want to log in using SMS OTP so that I don't need to remember a password | Should | 5 |

### Epic: Card Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-006 | As a user, I want to link my transit card to my account so that I can recharge it online | Must | 5 |
| US-007 | As a user, I want to see my linked card's current balance so that I know when to recharge | Must | 3 |
| US-008 | As a user, I want to link multiple cards (up to 5) so that I can manage cards for my family | Should | 5 |
| US-009 | As a user, I want to remove a card from my account so that I can manage my linked cards | Should | 3 |
| US-010 | As a system, I want to prevent duplicate card linking so that each card belongs to only one account | Must | 5 |

### Epic: Payment & Recharge

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-011 | As a user, I want to select a recharge amount and pay via bKash so that I can add funds to my card | Must | 8 |
| US-012 | As a user, I want to see my balance update immediately after payment so that I know the recharge worked | Must | 5 |
| US-013 | As a user, I want to receive a confirmation message after recharge so that I have proof of transaction | Should | 3 |
| US-014 | As a user, I want to be prevented from recharging below BDT 50 or above BDT 5,000 so that limits are enforced | Must | 3 |
| US-015 | As a user, I want the system to handle failed payments gracefully so that I'm not charged without receiving balance | Must | 8 |

### Epic: Transaction History & Tracking

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-016 | As a user, I want to view my complete transaction history so that I can track my spending | Must | 5 |
| US-017 | As a user, I want to distinguish between online recharges and tap transactions so that I understand my activity | Must | 3 |
| US-018 | As a user, I want to filter transactions by date range so that I can find specific transactions | Should | 5 |
| US-019 | As a user, I want to download my transaction history so that I can keep records for personal use | Could | 5 |

### Epic: Machine/Terminal Sync

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-020 | As a system, I want to receive tap transaction data from station gates so that user balances stay accurate | Must | 13 |
| US-021 | As a system, I want to handle batch sync from offline machines so that no transaction data is lost | Must | 13 |
| US-022 | As a system, I want to resolve out-of-order sync events so that balance calculations remain correct | Must | 8 |
| US-023 | As an admin, I want to monitor sync status across all machines so that I can identify connectivity issues | Should | 5 |

### Epic: Admin Dashboard

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-024 | As an admin, I want to see an overview of total transactions and revenue so that I can monitor system health | Must | 5 |
| US-025 | As an admin, I want to view and search user accounts so that I can assist with support requests | Must | 5 |
| US-026 | As an admin, I want to view all transaction records with filters so that I can investigate issues | Must | 5 |
| US-027 | As an admin, I want to manually adjust a user's balance (with approval) so that I can resolve discrepancies | Should | 8 |
| US-028 | As a finance analyst, I want automated reconciliation reports so that I can verify daily settlements | Should | 8 |

## 5. Acceptance Criteria

### US-001: User Registration

```
GIVEN I am on the registration page
WHEN I enter a valid phone number, email, and password (min 8 chars) and click "Register"
THEN my account is created and I receive a verification SMS and email

GIVEN I am on the registration page
WHEN I enter a phone number that is already registered
THEN I see an error message "This phone number is already registered"

GIVEN I am on the registration page
WHEN I enter a password shorter than 8 characters
THEN I see a validation error "Password must be at least 8 characters"

GIVEN I am on the registration page
WHEN I leave required fields empty and click "Register"
THEN I see inline validation errors for each missing field
```

### US-006: Card Linking

```
GIVEN I am logged in and on the card management page
WHEN I enter a valid 16-digit card number and click "Link Card"
THEN the card is linked to my account and I see its current balance

GIVEN I am on the card management page
WHEN I enter a card number that is already linked to another account
THEN I see an error "This card is already linked to another account"

GIVEN I am on the card management page
WHEN I enter a card number with invalid format
THEN I see a validation error "Please enter a valid card number"

GIVEN I already have 5 cards linked
WHEN I try to link another card
THEN I see an error "Maximum 5 cards allowed per account"
```

### US-011: bKash Payment Integration

```
GIVEN I am logged in and have a linked card
WHEN I select BDT 200 as recharge amount and click "Recharge with bKash"
THEN I am redirected to the bKash payment page

GIVEN I am on the bKash payment page
WHEN I complete the payment successfully
THEN I am redirected back to the platform and my balance increases by BDT 200

GIVEN I am on the bKash payment page
WHEN I cancel the payment
THEN I am redirected back with no balance change and a "Payment cancelled" message

GIVEN I attempt a recharge of BDT 30
WHEN I click "Recharge"
THEN I see an error "Minimum recharge amount is BDT 50"

GIVEN I attempt a recharge of BDT 6,000
WHEN I click "Recharge"
THEN I see an error "Maximum recharge amount is BDT 5,000"
```

### US-012: Real-Time Balance Update

```
GIVEN I have just completed a successful bKash payment
WHEN I am redirected to my dashboard
THEN my updated balance is displayed within 5 seconds

GIVEN my balance was BDT 100 before recharge
WHEN I successfully recharge BDT 200
THEN my new balance shows BDT 300
```

### US-016: Transaction History

```
GIVEN I am on the transaction history page
WHEN I view my history
THEN I see all my transactions sorted by date (newest first) with type, amount, and balance

GIVEN I have both recharge and tap transactions
WHEN I view my history
THEN recharge transactions are labeled "Online Recharge" and tap transactions are labeled "Fare Deduction"

GIVEN I select a date range filter
WHEN I apply the filter
THEN only transactions within that date range are displayed
```

### US-020: Machine Sync

```
GIVEN a user taps their linked card at a metro station gate
WHEN the gate sends transaction data to the system
THEN the user's account balance is updated to reflect the fare deduction

GIVEN a station gate was offline and reconnects
WHEN it sends batch transaction data
THEN all transactions are processed and balances are updated correctly

GIVEN two sync events arrive out of order
WHEN the system processes them
THEN the final balance is correct regardless of arrival order
```

## 6. User Flows

### Flow 1: New User Registration & First Recharge
1. User visits the DMTCL Card Recharge website
2. User clicks "Register" on the homepage
3. User fills in phone number, email, and password
4. User receives SMS and email verification codes
5. User enters verification codes to activate account
6. User logs in and is prompted to link a transit card
7. User enters their 16-digit card number
8. System validates and links the card, showing current balance
9. User clicks "Recharge Card"
10. User selects or enters recharge amount (e.g., BDT 200)
11. User clicks "Pay with bKash"
12. User is redirected to bKash payment page
13. User completes bKash payment (enter bKash number, PIN, confirm)
14. User is redirected back to the platform
15. System confirms successful recharge and shows updated balance
16. User receives SMS and email confirmation

### Flow 2: Card Tap at Station Gate (Sync)
1. User taps their linked card at a metro station entry gate
2. Gate deducts fare and records transaction locally
3. Gate sends transaction data to the central system via API
4. System matches card number to linked user account
5. System updates user's account balance and transaction history
6. User can view the fare deduction in their transaction history

### Flow 3: Admin Reconciliation
1. Admin logs into the admin dashboard
2. Admin navigates to "Reconciliation" section
3. Admin selects date range for reconciliation
4. System displays summary: total online recharges, total fare deductions, bKash settlement amount
5. Admin reviews any discrepancies flagged by the system
6. Admin exports reconciliation report as PDF

### Flow 4: Failed Payment Recovery
1. User initiates a recharge and is redirected to bKash
2. bKash payment fails (insufficient funds, timeout, etc.)
3. User is redirected back to the platform with failure status
4. System displays "Payment failed" message with reason
5. No balance change occurs
6. User can retry the recharge or choose a different amount

## 7. Wireframe References

<!-- Wireframe: Homepage / Landing Page -->
- Hero section with "Recharge Your Card Online" CTA
- Quick balance check (enter card number)
- Feature highlights (Fast, Secure, 24/7)
- Login/Register buttons

<!-- Wireframe: Registration Page -->
- Phone number input
- Email input
- Password input with strength indicator
- Terms & conditions checkbox
- Register button
- Link to login page

<!-- Wireframe: User Dashboard -->
- Current balance display (prominent)
- Linked cards list with individual balances
- Quick recharge button
- Recent transactions (last 5)
- Low balance warning banner

<!-- Wireframe: Recharge Page -->
- Select card to recharge
- Predefined amount buttons (BDT 50, 100, 200, 500, 1000)
- Custom amount input
- Min/max amount notice
- "Pay with bKash" button
- Transaction summary

<!-- Wireframe: Transaction History Page -->
- Date range filter
- Transaction type filter (All / Recharge / Fare Deduction)
- Transaction table (Date, Type, Amount, Balance After, Reference)
- Pagination
- Export button

<!-- Wireframe: Admin Dashboard -->
- KPI cards (Total Revenue Today, Active Users, Transactions Today, Sync Status)
- Transaction volume chart
- Recent transactions table
- System health indicators
- Quick links to user management and reports

<!-- Wireframe: Card Management Page -->
- List of linked cards with status and balance
- "Add New Card" button
- Card linking form (card number input, validation)
- Remove card option per card

## 8. Success Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| User Registration Rate | N/A (new system) | 5,000 registrations/month | Analytics dashboard |
| Online Recharge Adoption | 0% | 60% of all recharges within 12 months | Transaction analytics |
| Average Recharge Time | 5-10 min (counter) | < 30 seconds (online) | Session timing |
| Payment Success Rate | N/A | 98%+ | bKash integration logs |
| Sync Accuracy Rate | N/A | 99.5% | Sync monitoring system |
| Customer Satisfaction (CSAT) | N/A | 4.2/5 | In-app survey |
| System Uptime | N/A | 99.9% | Infrastructure monitoring |
| Counter Queue Reduction | Baseline TBD | 40% reduction | Station operations data |
| Daily Active Users | N/A | 50,000 DAU within 6 months | Analytics |
| Support Ticket Volume | Baseline TBD | 30% reduction in recharge-related tickets | Support system |

## 9. Dependencies

| Dependency | Type | Impact | Owner |
|-----------|------|--------|-------|
| bKash Payment Gateway API | External | Core payment processing | bKash Limited |
| bKash Merchant Account | External | Required for payment integration | DMTCL Finance |
| SMS Gateway (e.g., GreenWeb, SSLWireless) | External | OTP delivery and notifications | DMTCL IT |
| Email Service (e.g., SendGrid, AWS SES) | External | Transaction confirmations | DMTCL IT |
| DMTCL Card Reader API | Internal | Machine-to-system sync | DMTCL Hardware Team |
| DMTCL Card Management System | Internal | Card validation and balance queries | DMTCL IT |
| Bangladesh Bank MFS Guidelines | Regulatory | Compliance requirements | DMTCL Legal |
| Hosting Infrastructure | Internal | Application deployment | DMTCL IT / Cloud Provider |

## 10. Technology Assumptions

| Category | Assumption |
|----------|-----------|
| **Database** | PostgreSQL (SQL) — Selected for strong transaction integrity, ACID compliance, and financial data reliability |
| **Frontend** | React/Next.js for responsive web application with server-side rendering |
| **Backend** | Node.js/Express for RESTful API services |
| **Authentication** | JWT-based authentication with refresh token rotation |
| **Hosting** | Cloud-based deployment (AWS or equivalent) with auto-scaling |
| **Caching** | Redis for session management, API response caching, and rate limiting |
| **API Architecture** | RESTful APIs with OpenAPI/Swagger documentation |
| **Monitoring** | Application performance monitoring (APM) with alerting |
| **CI/CD** | Automated testing and deployment pipeline |
| **Language Support** | i18n framework for Bengali and English localization |

## 11. Timeline Estimates

| Phase | Features | Duration | Dependencies |
|-------|----------|----------|-------------|
| Phase 1: Foundation | User auth, account management, card linking | 4 weeks | None |
| Phase 2: Payment Integration | bKash integration, balance updates, notifications | 5 weeks | Phase 1, bKash API access |
| Phase 3: Machine Sync | Sync API, conflict resolution, batch processing | 6 weeks | Phase 2, DMTCL card reader API |
| Phase 4: Admin & Reporting | Admin dashboard, reconciliation reports, audit trail | 4 weeks | Phase 3 |
| Phase 5: Testing & Launch | Load testing, security audit, UAT, production deployment | 3 weeks | All phases complete |
| **Total** | | **22 weeks (~5.5 months)** | |

## 12. Open Questions

1. What is the exact card number format and validation rules used by DMTCL's current card system?
2. Does DMTCL have an existing API for card reader/gate integration, or does it need to be developed?
3. What is the expected peak transaction volume during rush hours (for capacity planning)?
4. Should the system support partial recharges when a user's balance plus recharge would exceed the BDT 10,000 cap?
5. What is the bKash merchant onboarding timeline and are there any special requirements for transit operators?
6. Should low-balance alerts be configurable by the user (threshold selection)?
7. What is the disaster recovery RTO/RPO requirement for this system?
8. Should the admin dashboard support role-based views (e.g., finance-only view vs. operations-only view)?
