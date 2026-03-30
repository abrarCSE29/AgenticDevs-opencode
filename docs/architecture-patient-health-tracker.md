# Architecture Document - Patient Health Tracker

## 1. Architecture Pattern
**Pattern**: Layered MVC with REST API
**Rationale**: Simple, well-understood pattern suitable for MVP. Separates concerns between presentation (React), business logic (Express), and data (PostgreSQL).

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              React SPA (TypeScript)                   │   │
│  │  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐  │   │
│  │  │Dashboard│ │Medication│ │ Reports │ │  Visits  │  │   │
│  │  │  Page   │ │  Pages   │ │  Page   │ │  Page    │  │   │
│  │  │         │ │ Profile  │ │         │ │          │  │   │
│  │  └─────────┘ └──────────┘ └─────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       SERVER LAYER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Node.js / Express API (TypeScript)          │   │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────────┐  │   │
│  │  │  Auth    │ │  Profile  │ │  Export Service    │  │   │
│  │  │Middleware│ │  Service  │ │  (PDF/CSV/JSON)    │  │   │
│  │  └──────────┘ └───────────┘ └────────────────────┘  │   │
│  │  ┌──────────┐ ┌───────────┐ ┌────────────────────┐  │   │
│  │  │  Business│ │ Notification│ │  Notification    │  │   │
│  │  │  Logic   │ │  Service  │ │  Service          │  │   │
│  │  └──────────┘ └───────────┘ └────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  PostgreSQL  │  │   AWS S3     │  │  Redis Cache     │  │
│  │  Database    │  │  (Images)    │  │  (Sessions)      │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   SendGrid   │  │   Firebase   │  │  CloudWatch      │  │
│  │   (Email)    │  │   (Push)     │  │  (Monitoring)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  OCR API (Phase 2 - Future Integration)              │   │
│  │  - Auto-extract data from medical documents          │   │
│  │  - Supports prescription parsing                      │   │
│  │  - Lab report digitization                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 3. Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    blood_group VARCHAR(5),
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Patient Profiles Table
```sql
CREATE TABLE patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    blood_group VARCHAR(5),
    relationship VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### User Patient Profiles Junction Table
```sql
CREATE TABLE user_patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,
    can_export BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, patient_profile_id)
);
```

### Doctors Table
```sql
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    specialty VARCHAR(255),
    clinic_name VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Medicines Master Table (Pre-installed Catalog)
```sql
CREATE TABLE medicines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    generic_name VARCHAR(255),
    category VARCHAR(100), -- e.g., 'Antidiabetic', 'Antihypertensive', 'Analgesic'
    manufacturer VARCHAR(255),
    common_dosages TEXT[], -- Array of common dosages: ['500mg', '1000mg']
    common_frequencies TEXT[], -- Array: ['Once daily', 'Twice daily', 'As needed']
    unit VARCHAR(20), -- e.g., 'mg', 'ml', 'tablet', 'capsule'
    is_custom BOOLEAN DEFAULT FALSE, -- TRUE for user-added custom medications
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
-- Pre-populate with common medications (see seed data below)
```

### Medications Table (Patient-Specific Prescriptions)
```sql
CREATE TABLE medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    medicine_id UUID REFERENCES medicines(id), -- FK to master table
    doctor_id UUID REFERENCES doctors(id),
    -- Patient-specific fields (different per patient even for same medicine)
    dosage VARCHAR(100) NOT NULL, -- e.g., '500mg' (patient-specific)
    frequency VARCHAR(50) NOT NULL, -- e.g., 'Twice daily' (patient-specific)
    duration_days INTEGER NOT NULL,
    notes TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Data Model Explanation:**

The master-detail relationship between `medicines` and `medications` solves the user's concern:

| Scenario | How It Works |
|----------|--------------|
| Two patients on Metformin | Both reference the same `medicines.id` for Metformin, but each has their own `medications` record with different dosages/schedules |
| Finding all patients on a medication | JOIN medications → medicines WHERE name = 'Metformin' |
| Pre-installed catalog | System ships with ~500 common medications pre-populated |
| Custom medications | Caregivers can add custom medicines (marked `is_custom = TRUE`) |

**Seed Data for Medicines Master Table:**
```sql
-- Antidiabetic
INSERT INTO medicines (name, generic_name, category, common_dosages, common_frequencies, unit) VALUES
('Metformin', 'Metformin Hydrochloride', 'Antidiabetic', ARRAY['500mg', '850mg', '1000mg'], ARRAY['Once daily', 'Twice daily', 'With meals'], 'tablet'),
('Glipizide', 'Glipizide', 'Antidiabetic', ARRAY['5mg', '10mg'], ARRAY['Once daily', 'Twice daily'], 'tablet'),
('Insulin', 'Insulin', 'Antidiabetic', ARRAY['10U', '20U', '30U'], ARRAY['Once daily', 'Twice daily', 'With meals'], 'unit');

-- Antihypertensive
INSERT INTO medicines (name, generic_name, category, common_dosages, common_frequencies, unit) VALUES
('Lisinopril', 'Lisinopril', 'Antihypertensive', ARRAY['5mg', '10mg', '20mg', '40mg'], ARRAY['Once daily'], 'tablet'),
('Amlodipine', 'Amlodipine Besylate', 'Antihypertensive', ARRAY['2.5mg', '5mg', '10mg'], ARRAY['Once daily'], 'tablet'),
('Losartan', 'Losartan Potassium', 'Antihypertensive', ARRAY['25mg', '50mg', '100mg'], ARRAY['Once daily', 'Twice daily'], 'tablet');

-- Analgesic
INSERT INTO medicines (name, generic_name, category, common_dosages, common_frequencies, unit) VALUES
('Paracetamol', 'Acetaminophen', 'Analgesic', ARRAY['500mg', '650mg', '1000mg'], ARRAY['As needed', 'Every 4-6 hours', 'Every 6-8 hours'], 'tablet'),
('Ibuprofen', 'Ibuprofen', 'Analgesic', ARRAY['200mg', '400mg', '600mg', '800mg'], ARRAY['As needed', 'Every 6-8 hours', 'With food'], 'tablet');

-- Cardiovascular
INSERT INTO medicines (name, generic_name, category, common_dosages, common_frequencies, unit) VALUES
('Atorvastatin', 'Atorvastatin Calcium', 'Cardiovascular', ARRAY['10mg', '20mg', '40mg', '80mg'], ARRAY['Once daily', 'At bedtime'], 'tablet'),
('Aspirin', 'Acetylsalicylic Acid', 'Cardiovascular', ARRAY['75mg', '81mg', '100mg', '325mg'], ARRAY['Once daily', 'As needed'], 'tablet');

-- Continue with other categories as needed...
```

### Medication Schedules Table
```sql
CREATE TABLE medication_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medication_id UUID REFERENCES medications(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    taken_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Test Reports Table
```sql
CREATE TABLE test_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(id),
    test_name VARCHAR(255) NOT NULL,
    test_date DATE NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Doctor Visits Table
```sql
CREATE TABLE doctor_visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    doctor_id UUID REFERENCES doctors(id),
    visit_date TIMESTAMP NOT NULL,
    reason VARCHAR(500),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Notifications Table
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    scheduled_for TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Notification Preferences Table
```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE CASCADE UNIQUE,
    medication_reminders BOOLEAN DEFAULT TRUE,
    visit_reminders BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    push_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Data Model Relationship: Medicines Master Table

**Problem Solved:**
The user's concern was: *"Two patients may have the same medication. Then how will we find out which patient has which medicine?"*

**Solution:**
We implement a **master-detail relationship** between two tables:

```
┌─────────────────────┐       ┌─────────────────────┐
│      medicines      │       │    medications      │
│   (Master Table)    │       │ (Patient-Specific)  │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │◄──────│ medicine_id (FK)    │
│ name                │       │ patient_profile_id  │
│ generic_name        │       │ doctor_id           │
│ category            │       │ dosage              │
│ common_dosages[]    │       │ frequency           │
│ common_frequencies[]│       │ duration_days       │
│ manufacturer        │       │ start_date          │
│ is_custom           │       │ end_date            │
└─────────────────────┘       │ status              │
                              └─────────────────────┘
```

**Example Scenario:**
- **Patient A**: Metformin 500mg, twice daily
- **Patient B**: Metformin 1000mg, once daily
- Both reference `medicines.id` for Metformin, but have different `dosage` and `frequency` values

**Benefits:**
1. **Data Consistency**: Same medication name across all patients
2. **Easy Queries**: Find all patients on a specific medication
3. **Autocomplete**: Search medicines when adding prescriptions
4. **Pre-populated Catalog**: System ships with common medications
5. **Custom Medications**: Users can add medications not in the catalog

## 4. API Endpoints

### Authentication
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login
- POST /api/auth/logout - Logout
- POST /api/auth/forgot-password - Request password reset
- POST /api/auth/reset-password - Reset password
- GET /api/auth/verify-email/:token - Verify email

### User Profile
- GET /api/profile - Get user profile
- PUT /api/profile - Update user profile

### Doctors
- GET /api/doctors - List all doctors
- POST /api/doctors - Add new doctor
- GET /api/doctors/:id - Get doctor details
- PUT /api/doctors/:id - Update doctor
- DELETE /api/doctors/:id - Delete doctor
- GET /api/doctors/:id/prescriptions - Get doctor's prescriptions

### Medications
- GET /api/medications - List all medications for a patient
- POST /api/medications - Add new medication (auto-generates schedule)
- GET /api/medications/:id - Get medication details with schedule
- PUT /api/medications/:id - Update medication
- DELETE /api/medications/:id - Delete medication
- PATCH /api/medications/:id/schedule/:scheduleId - Mark dose as taken

### Medicines Catalog (Master Table)
- GET /api/medicines - List all medicines (with search/filter)
- GET /api/medicines/search - Search medicines by name (autocomplete)
- GET /api/medicines/:id - Get medicine details
- POST /api/medicines - Add custom medicine (for medications not in catalog)
- GET /api/medicines/categories - Get all medicine categories

### Test Reports
- GET /api/reports - List all reports
- POST /api/reports - Upload new report (multipart/form-data)
- GET /api/reports/:id - Get report details
- PUT /api/reports/:id - Update report metadata
- DELETE /api/reports/:id - Delete report

### Doctor Visits
- GET /api/visits - List all visits
- POST /api/visits - Schedule new visit
- GET /api/visits/:id - Get visit details
- PUT /api/visits/:id - Update visit
- DELETE /api/visits/:id - Cancel visit
- PATCH /api/visits/:id/notes - Add post-visit notes

### Notifications
- GET /api/notifications - List notifications
- PATCH /api/notifications/:id/read - Mark as read
- GET /api/notifications/preferences - Get preferences
- PUT /api/notifications/preferences - Update preferences

### Dashboard
- GET /api/dashboard - Get dashboard data (today's meds, upcoming visits, recent activity)

### Patient Profiles
- GET /api/profiles - List all patient profiles for current user
- POST /api/profiles - Create new patient profile
- GET /api/profiles/:id - Get patient profile details
- PUT /api/profiles/:id - Update patient profile
- DELETE /api/profiles/:id - Delete patient profile
- PATCH /api/profiles/:id/switch - Set active profile

### Data Export
- GET /api/export/medications/pdf - Export medication chart as PDF
- GET /api/export/medications/csv - Export medication chart as CSV
- GET /api/export/all/json - Export all patient data as JSON (HIPAA compliance)

## 5. Security Architecture

### Authentication Flow
1. User registers with email/password
2. Password hashed with bcrypt (cost factor 12)
3. Verification email sent via SendGrid
4. User verifies email and logs in
5. Server issues JWT access token (24h expiry) and refresh token (7d expiry)
6. Access token sent in Authorization header for API requests
7. Refresh token used to get new access token

### Data Protection
- **At Rest**: AES-256 encryption for database and S3 storage
- **In Transit**: TLS 1.2+ for all communications
- **Password Storage**: Bcrypt with cost factor 12
- **API Security**: Rate limiting, CORS, input validation

### HIPAA Compliance
- All PHI encrypted at rest and in transit
- Audit logging for all data access
- Access controls (users can only access their own data)
- Data retention policies
- Secure session management

## 6. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    VPC                                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   Public    │  │   Private   │  │   Private   │  │   │
│  │  │   Subnet    │  │   Subnet    │  │   Subnet    │  │   │
│  │  │             │  │             │  │             │  │   │
│  │  │  ALB       │  │  ECS Fargate│  │  RDS        │  │   │
│  │  │  (HTTPS)   │  │  (Node.js)  │  │  PostgreSQL │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  S3 Bucket  │  │ ElastiCache │  │ CloudWatch  │  │   │
│  │  │  (Images)   │  │  (Redis)    │  │ (Monitoring)│  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  CloudFront CDN                       │   │
│  │                  (React SPA)                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Infrastructure Components
- **CloudFront**: CDN for React SPA static assets
- **ALB**: Application Load Balancer with SSL termination
- **ECS Fargate**: Container orchestration for Node.js API
- **RDS PostgreSQL**: Managed database with Multi-AZ
- **S3**: Object storage for test report images
- **ElastiCache Redis**: Session storage and caching
- **CloudWatch**: Logging and monitoring
