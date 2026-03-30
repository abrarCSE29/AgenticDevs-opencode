# Product Requirements Document (PRD)
## Patient Health Tracker

**Document Version:** 1.3  
**Last Updated:** March 29, 2026  
**Status:** Draft (Updated with caregiver access, data export, and OCR clarification)  
**Related BRD:** [brd-patient-health-tracker.md](./brd-patient-health-tracker.md)

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Target Users](#2-target-users)
3. [Feature Overview](#3-feature-overview)
4. [User Stories](#4-user-stories)
5. [Acceptance Criteria](#5-acceptance-criteria)
6. [User Flows](#6-user-flows)
7. [Wireframe References](#7-wireframe-references)
8. [Success Metrics](#8-success-metrics)
9. [Dependencies](#9-dependencies)
10. [Timeline Estimates](#10-timeline-estimates)
11. [Open Questions](#11-open-questions)

---

## 1. Problem Statement

Patients managing ongoing healthcare—especially those with chronic conditions or multiple specialists—struggle to keep track of their medications, doctor appointments, and medical test results because information is scattered across paper prescriptions, phone notes, and various clinic portals. This fragmentation results in missed medication doses, forgotten follow-up appointments, incomplete medical histories, and increased anxiety about managing their own health. The problem is compounded for caregivers who manage healthcare for dependents (e.g., elderly parents or children) and must juggle multiple patients' records. The lack of a centralized, patient-owned health tracking tool leads to poor medication adherence, preventable health complications, and inefficient communication with healthcare providers.

---

## 2. Target Users

### Persona 1: Sarah — Chronic Condition Patient

- **Role**: Patient managing Type 2 Diabetes and hypertension
- **Demographics**: 52 years old, moderate tech comfort (uses smartphone daily, comfortable with apps)
- **Goals**: Track medications from 3 different doctors, remember when to take each medication, keep lab results organized
- **Pain Points**: Forgets which doctor prescribed what; loses paper prescriptions; misses follow-up appointments
- **Usage Frequency**: Daily (medication tracking), weekly (checking upcoming visits)

### Persona 2: James — Post-Surgery Recovery Patient

- **Role**: Patient recovering from knee replacement surgery
- **Demographics**: 38 years old, high tech comfort (early adopter of health apps)
- **Goals**: Track post-surgery medications with specific schedules, upload physical therapy progress reports, remember surgeon follow-up dates
- **Pain Points**: Complex medication schedule with tapering doses; hard to track progress over time
- **Usage Frequency**: Multiple times daily (medication reminders), weekly (report uploads)

### Persona 3: Maria — Caregiver for Elderly Parent

- **Role**: Daughter managing her 78-year-old mother's healthcare
- **Demographics**: 45 years old, moderate tech comfort
- **Goals**: Manage mother's medications from multiple specialists, coordinate doctor visits, keep all test reports in one place
- **Pain Points**: Mother sees 4 different doctors; medications sometimes overlap; hard to share complete history with new doctors
- **Usage Frequency**: Daily (checking medications), monthly (scheduling appointments)

### Persona 4: Dr. Patel — Healthcare Provider (Indirect User)

- **Role**: General practitioner who benefits from patients having organized records
- **Demographics**: N/A (not a direct app user)
- **Goals**: Patients arrive with complete medication lists and recent test results
- **Pain Points**: Patients often forget what medications they take or bring incomplete records
- **Usage Frequency**: N/A (benefits indirectly during patient visits)

---

## 3. Feature Overview (MoSCoW Prioritization)

| Feature | Description | Priority | Effort (T-shirt) |
|---------|-------------|----------|------------------|
| User Authentication | Email/password registration, login, password reset | Must | M |
| User Profile | Basic health profile with personal and emergency info | Must | S |
| Medication Management | Add, edit, delete medications with dosage and schedule | Must | L |
| Auto Medication Chart | System-generated schedule based on dosage/frequency/duration | Must | L |
| Medication Adherence Tracking | Mark doses as taken; view adherence history | Should | M |
| Doctor Management | Add, edit, remove doctors with contact details | Must | M |
| Prescription Linking | Link each medication to its prescribing doctor | Must | M |
| Test Report Upload | Upload reports via camera/photo with metadata | Must | L |
| Test Report Gallery | View, filter, and manage uploaded reports | Should | M |
| Doctor Visit Scheduling | Schedule, edit, cancel appointments with doctors | Must | M |
| Visit Calendar View | Visual calendar of upcoming and past visits | Should | M |
| Medication Reminders | Notifications for scheduled medication doses | Must | L |
| Visit Reminders | Notifications before doctor appointments (24h, 1h) | Must | M |
| Notification Preferences | Enable/disable notification types, quiet hours, channel selection | Must | S |
| In-App Notifications | Notification center within the application | Must | M |
| Email Notifications | Email alerts for reminders | Must | M |
| Push Notifications | Browser push notifications | Could | M |
| Dashboard | Central view of today's meds, upcoming visits, recent activity | Must | L |
| Activity Log | History of all actions (meds taken, reports uploaded, etc.) | Could | S |
| Image Processing | Automatic thumbnail generation, compression, format validation | Must | M |
| Patient Data Export | Export all PHI in JSON/CSV format (HIPAA Right of Access) | Must | M |
| Medication Chart Export (PDF) | Export medication charts as PDF for sharing with doctors | Should | M |
| Medication Chart Export (CSV) | Export medication charts as CSV for personal records or analysis | Should | S |
| Caregiver Access | Manage health data on behalf of linked patient profiles | Must | L |
| Multi-Profile Management | Switch between patient profiles; create profiles for dependents | Must | M |
| Report OCR (Phase 2) | Text extraction from uploaded reports via external OCR API | Could | L |
| Medication Interaction Warnings | Flag potential drug interactions (Phase 2 - Future) | Won't (MVP) | XL |
| Medication Master Catalog | Pre-installed database of common medications with search and autocomplete | Must | M |
| Custom Medication Entry | Allow users to add medications not in the master catalog | Should | S |

---

## 4. User Stories

### Epic 1: User Onboarding & Authentication

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-001 | As a new user, I want to register with my email and password so that I can create a secure account | Must | 3 |
| US-002 | As a returning user, I want to log in with my email and password so that I can access my health data | Must | 3 |
| US-003 | As a user, I want to reset my password via email so that I can regain access if I forget it | Must | 3 |
| US-004 | As a new user, I want to verify my email address so that my account is confirmed and secure | Must | 2 |
| US-005 | As a user, I want to set up my profile with name, date of birth, blood group, and emergency contact so that my basic health info is recorded | Must | 3 |

### Epic 2: Medication Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-006 | As a patient, I want to add a new medication with its name, dosage, frequency, and duration so that I can track what I need to take | Must | 5 |
| US-007 | As a patient, I want the system to automatically generate a medication schedule/chart based on the dosage and timing I enter so that I know exactly when to take each dose | Must | 8 |
| US-008 | As a patient, I want to edit or delete a medication so that I can keep my medication list accurate | Must | 3 |
| US-009 | As a patient, I want to mark a medication dose as taken so that I can track my adherence | Should | 3 |
| US-010 | As a patient, I want to view my active medications and completed/expired medications separately so that I can focus on current treatments | Must | 3 |
| US-011 | As a patient, I want to add custom notes to a medication (e.g., "take with food") so that I remember special instructions | Should | 2 |
| US-047 | As a patient, I want to search and select medications from a pre-installed catalog so that I can quickly find my medications without typing the full name | Must | 5 |
| US-048 | As a patient, I want to see autocomplete suggestions as I type a medication name so that I can select the correct medication easily | Must | 3 |
| US-049 | As a patient, I want to add a custom medication that is not in the catalog so that I can track all my medications | Should | 3 |

### Epic 3: Doctor & Prescription Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-012 | As a patient, I want to add a doctor with their name, specialty, clinic, phone, and email so that I can track my healthcare providers | Must | 3 |
| US-013 | As a patient, I want to edit or remove a doctor from my list so that my doctor information stays current | Must | 2 |
| US-014 | As a patient, I want to link each medication to the doctor who prescribed it so that I know which doctor is responsible for each treatment | Must | 5 |
| US-015 | As a patient, I want to see which doctor prescribed which medication so that I can ask the right doctor about specific medications | Must | 3 |
| US-016 | As a patient, I want to view a doctor's complete prescription history so that I can see all medications prescribed by that doctor | Should | 3 |

### Epic 4: Test Report Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-017 | As a patient, I want to upload a test report by taking a photo or selecting from my gallery so that I can digitize my paper reports | Must | 5 |
| US-018 | As a patient, I want to add metadata (test name, date, doctor, notes) to an uploaded report so that I can organize and find it later | Must | 3 |
| US-019 | As a patient, I want to view, edit, and delete my uploaded reports so that I can manage my report collection | Must | 3 |
| US-020 | As a patient, I want to filter my reports by doctor or test type so that I can quickly find specific reports | Should | 3 |

### Epic 5: Doctor Visit Scheduling

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-021 | As a patient, I want to schedule a doctor visit with date, time, doctor, and reason so that I can plan my appointments | Must | 5 |
| US-022 | As a patient, I want to view my upcoming and past visits in a list or calendar so that I can see my appointment history | Must | 5 |
| US-023 | As a patient, I want to edit or cancel a scheduled visit so that I can adjust my plans | Must | 3 |
| US-024 | As a patient, I want to add notes after a doctor visit so that I can record what was discussed | Should | 3 |

### Epic 6: Notifications & Reminders

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-025 | As a patient, I want to receive reminders for my upcoming doctor visits (24 hours and 1 hour before) so that I don't miss appointments | Must | 5 |
| US-026 | As a patient, I want to receive reminders for my scheduled medication doses so that I take them on time | Must | 8 |
| US-027 | As a patient, I want to enable or disable specific notification types so that I control what alerts I receive | Must | 3 |
| US-028 | As a patient, I want to receive notifications in-app and via email so that I don't miss important reminders | Must | 5 |
| US-029 | As a patient, I want to receive browser push notifications so that I get alerts even when the app is not open | Could | 5 |
| US-032 | As a patient, I want to set quiet hours (e.g., 10 PM - 7 AM) so that I'm not disturbed during sleep by non-critical notifications | Must | 3 |
| US-033 | As a patient, I want to choose my preferred notification channel (in-app, email, or push) for each notification type so that I receive alerts the way I prefer | Must | 3 |
| US-034 | As a patient, I want critical medication reminders to bypass quiet hours (configurable) so that I never miss important doses | Should | 2 |
| US-035 | As a patient, I want notifications queued when I'm offline to be delivered when I reconnect so that I don't miss any reminders | Should | 3 |

### Epic 7: Dashboard

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-030 | As a patient, I want to see a dashboard with today's medications, upcoming visits, and recent activity so that I have a quick health overview | Must | 8 |
| US-031 | As a patient, I want to see a summary count of my active medications, doctors, and reports on the dashboard so that I understand my health data at a glance | Should | 3 |

### Epic 8: Caregiver Access & Multi-Profile Management

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-036 | As a caregiver, I want to create a patient profile for my dependent (e.g., elderly mother) so that I can manage their health data separately from my own | Must | 5 |
| US-037 | As a caregiver, I want to link my account to multiple patient profiles so that I can manage healthcare for more than one dependent | Must | 5 |
| US-038 | As a caregiver, I want to switch between patient profiles so that I can view and manage each patient's health data independently | Must | 5 |
| US-039 | As a caregiver, I want to add medications, schedule visits, and upload reports on behalf of my linked patients so that I can manage their complete healthcare | Must | 8 |
| US-040 | As a caregiver, I want to see a separate dashboard for each linked patient so that I have a quick overview of each patient's health status | Must | 5 |
| US-041 | As a user, I want to see a clear indicator of which patient profile I am currently managing so that I don't accidentally enter data for the wrong person | Must | 3 |

### Epic 9: Data Export

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-042 | As a patient, I want to export my medication chart as a PDF so that I can share it with my doctor during visits | Should | 5 |
| US-043 | As a patient, I want to export my medication chart as a CSV file so that I can analyze my medication history or keep personal records | Should | 3 |
| US-044 | As a caregiver, I want to export medication charts for my linked patients so that I can share them with healthcare providers | Should | 3 |
| US-045 | As a patient, I want to export all my health data in a machine-readable format (JSON/CSV) so that I can exercise my HIPAA Right of Access | Must | 5 |

### Epic 10: Report OCR (Phase 2 - Future)

| ID | User Story | Priority | Points |
|----|-----------|----------|--------|
| US-046 | As a patient, I want the system to extract text from my uploaded test reports via an external OCR service so that report content is searchable | Could | 8 |

---

## 5. Acceptance Criteria

### US-001: User Registration

```
GIVEN I am on the registration page
WHEN I enter a valid email address, a strong password (min 8 chars, 1 uppercase, 1 number), and click "Register"
THEN my account is created, I see a success message, and I receive a verification email

GIVEN I am on the registration page
WHEN I enter an email that already exists in the system
THEN I see an error message "An account with this email already exists"

GIVEN I am on the registration page
WHEN I enter a password that does not meet strength requirements
THEN I see a validation error indicating the password requirements

GIVEN I am on the registration page
WHEN I leave required fields empty and click "Register"
THEN I see validation errors for each empty required field
```

### US-002: User Login

```
GIVEN I am on the login page
WHEN I enter my registered email and correct password and click "Login"
THEN I am redirected to the dashboard

GIVEN I am on the login page
WHEN I enter an incorrect password
THEN I see an error message "Invalid email or password"

GIVEN I am on the login page
WHEN I enter an unregistered email
THEN I see an error message "Invalid email or password"

GIVEN I have failed login 5 times consecutively
WHEN I attempt another login
THEN my account is temporarily locked for 15 minutes and I see a message indicating this
```

### US-006: Add Medication

```
GIVEN I am on the medications page
WHEN I click "Add Medication" and fill in the medication name, dosage (e.g., "500mg"), frequency (e.g., "Twice daily"), duration (e.g., "14 days"), and select a prescribing doctor
THEN the medication is saved and I see it in my active medications list

GIVEN I am adding a medication
WHEN I leave the medication name empty
THEN I see a validation error "Medication name is required"

GIVEN I am adding a medication
WHEN I enter a duration that is in the past
THEN I see a validation error "Duration must be a future date or number of days"

GIVEN I am adding a medication
WHEN I do not select a prescribing doctor
THEN I see a validation error "Please select the prescribing doctor"
```

### US-007: Auto Medication Chart Generation

```
GIVEN I have added a medication with frequency "Twice daily" and duration "14 days"
WHEN the medication is saved
THEN the system automatically generates a schedule showing 28 doses (2 per day x 14 days) with specific times

GIVEN I have added a medication with frequency "Three times daily" for "7 days"
WHEN I view the medication chart
THEN I see 21 scheduled doses spread across 7 days at appropriate intervals (e.g., 8 AM, 2 PM, 8 PM)

GIVEN a medication chart has been generated
WHEN I view the chart
THEN I see each dose with date, time, and a status indicator (pending/taken/missed)

GIVEN a medication's duration has expired
WHWHEN I view the medication
THEN it is moved to "Completed Medications" and the chart shows all doses as finalized
```

### US-014: Link Medication to Doctor

```
GIVEN I am adding a new medication
WHEN I select a doctor from the "Prescribing Doctor" dropdown
THEN the medication is linked to that doctor and the link is visible on the medication details

GIVEN I have a medication linked to Dr. Smith
WHEN I view the medication details
THEN I see "Prescribed by: Dr. Smith" with a link to the doctor's profile

GIVEN I want to change the prescribing doctor for a medication
WHEN I edit the medication and select a different doctor
THEN the medication is updated to show the new doctor as the prescriber
```

### US-017: Upload Test Report

```
GIVEN I am on the test reports page
WHEN I click "Upload Report" and take a photo or select an image from my gallery
THEN the image is uploaded and I am prompted to add metadata

GIVEN I am uploading a test report
WHEN I select a file that is not an image (JPEG/PNG) or PDF
THEN I see an error message "Only JPEG, PNG, and PDF files are supported"

GIVEN I am uploading a test report
WHEN I select a file larger than 10MB
THEN I see an error message "File size must be less than 10MB"

GIVEN I have uploaded a report image
WHEN I fill in the test name, date, associated doctor, and optional notes and click "Save"
THEN the report is saved and appears in my reports list with the uploaded image thumbnail
```

### US-021: Schedule Doctor Visit

```
GIVEN I am on the visits page
WHEN I click "Schedule Visit" and fill in the date, time, select a doctor, enter a reason, and click "Save"
THEN the visit is saved and appears in my upcoming visits list

GIVEN I am scheduling a visit
WHEN I select a date and time that is in the past
THEN I see a validation error "Visit date must be in the future"

GIVEN I am scheduling a visit
WHEN I do not select a doctor
THEN I see a validation error "Please select a doctor"

GIVEN I have scheduled a visit
WHEN I view the upcoming visits
THEN I see the visit with date, time, doctor name, and reason
```

### US-025: Doctor Visit Reminders

```
GIVEN I have a doctor visit scheduled for tomorrow at 10:00 AM
WHEN the current time is 24 hours before the visit (today at 10:00 AM)
THEN I receive an in-app notification and email reminder: "Reminder: You have a visit with Dr. [Name] tomorrow at 10:00 AM"

GIVEN I have a doctor visit scheduled for today at 10:00 AM
WHEN the current time is 1 hour before the visit (9:00 AM)
THEN I receive an in-app notification and email reminder: "Reminder: Your visit with Dr. [Name] is in 1 hour"

GIVEN I have disabled visit reminders in my notification preferences
WHEN a visit reminder is scheduled to be sent
THEN no notification is sent
```

### US-026: Medication Reminders

```
GIVEN I have a medication scheduled for 8:00 AM daily
WHEN the current time is 8:00 AM
THEN I receive an in-app notification and email: "Time to take [Medication Name] - [Dosage]"

GIVEN I have marked a medication dose as taken
WHEN the next scheduled dose time arrives
THEN I receive a reminder for the next dose

GIVEN I have disabled medication reminders in my notification preferences
WHEN a medication reminder is scheduled to be sent
THEN no notification is sent
```

### US-030: Dashboard

```
GIVEN I am logged in and have health data
WHEN I navigate to the dashboard
THEN I see a section showing today's medications with status (taken/pending)

GIVEN I am logged in and have scheduled visits
WHEN I view the dashboard
THEN I see a section showing my next 3 upcoming doctor visits with dates and doctor names

GIVEN I am logged in and have recent activity
WHEN I view the dashboard
THEN I see a section showing my last 5 activities (e.g., "Added medication: Metformin", "Uploaded blood test report")

GIVEN I am a new user with no data
WHEN I view the dashboard
THEN I see helpful prompts to add my first medication, doctor, or schedule a visit
```

### US-036: Create Patient Profile for Dependent

```
GIVEN I am logged in and on the profile management page
WHEN I click "Add Patient Profile" and enter the dependent's name, date of birth, blood group, and emergency contact
THEN a new patient profile is created and linked to my account

GIVEN I am creating a patient profile
WHEN I leave the patient name empty
THEN I see a validation error "Patient name is required"

GIVEN I have created a patient profile
WHEN I view my profiles
THEN I see both my own profile and the new patient profile listed
```

### US-038: Switch Between Patient Profiles

```
GIVEN I am logged in and have multiple patient profiles linked
WHEN I click on the profile selector in the header
THEN I see a dropdown listing all linked patient profiles (including my own)

GIVEN I select a different patient profile from the dropdown
WHEN the profile switch completes
THEN the dashboard and all navigation reflect the selected patient's health data

GIVEN I have switched to a patient profile
WHEN I view the header
THEN I see a clear indicator showing the current patient's name (e.g., "Managing: Mom's Health")
```

### US-039: Caregiver Manages Patient Health Data

```
GIVEN I have switched to a linked patient profile
WHEN I add a medication with name, dosage, frequency, duration, and prescribing doctor
THEN the medication is saved under the patient's profile, not my personal profile

GIVEN I have switched to a linked patient profile
WHEN I schedule a doctor visit
THEN the visit is saved under the patient's profile

GIVEN I have switched to a linked patient profile
WHEN I upload a test report
THEN the report is saved under the patient's profile

GIVEN I am managing a patient's data
WHEN I view the audit log
THEN I see entries showing my user ID as the actor and the patient's profile ID as the data owner
```

### US-042: Export Medication Chart as PDF

```
GIVEN I am viewing a patient's medication chart
WHEN I click "Export as PDF"
THEN a PDF file is downloaded containing the patient's name, all active medications, dosage schedules, and prescribing doctors

GIVEN I am exporting a medication chart as PDF
WHEN the PDF is generated
THEN it includes a timestamp and a disclaimer: "This export is for informational purposes only"

GIVEN I am a caregiver viewing a linked patient's medications
WHEN I click "Export as PDF"
THEN the PDF is generated for the selected patient's data
```

### US-043: Export Medication Chart as CSV

```
GIVEN I am viewing a patient's medication chart
WHEN I click "Export as CSV"
THEN a CSV file is downloaded with columns: Medication Name, Dosage, Frequency, Duration, Prescribing Doctor, Start Date, Status

GIVEN I open the exported CSV file
WHEN I view the data
THEN all medication information is accurately represented in tabular format
```

### US-045: Export All Health Data (HIPAA Right of Access)

```
GIVEN I am on the settings or profile page
WHEN I click "Export All My Data"
THEN the system generates a downloadable archive containing all my health data in JSON or CSV format

GIVEN I request a full data export
WHEN the export is generated
THEN it includes: profile information, all medications, all doctors, all reports metadata, all visits, and notification history

GIVEN I am a caregiver
WHEN I request a data export for a linked patient
THEN the export contains that patient's complete health data, clearly separated from other profiles
```

### US-047: Search and Select Medications from Catalog

```
GIVEN I am adding a new medication
WHEN I start typing the medication name (e.g., "Met")
THEN I see a dropdown with matching medications from the catalog (e.g., "Metformin 500mg", "Metformin 1000mg")

GIVEN I select a medication from the catalog
WHEN the medication form loads
THEN I see the medication name pre-filled with common dosage options available

GIVEN I am searching for a medication
WHEN I type a name that does not exist in the catalog
THEN I see an option to "Add as custom medication"
```

### US-048: Autocomplete Suggestions for Medication Names

```
GIVEN I am typing in the medication name field
WHEN I have typed at least 2 characters
THEN I see autocomplete suggestions matching my input

GIVEN I see autocomplete suggestions
WHEN I click on a suggestion
THEN the medication name is filled and I can proceed to enter dosage details
```

---

## 6. User Flows

### Flow 1: New User Onboarding

1. User lands on the homepage
2. User clicks "Get Started" or "Register"
3. User fills in email, password, and confirms password
4. User clicks "Register"
5. System sends verification email
6. User opens email and clicks verification link
7. User is redirected to login page
8. User logs in with credentials
9. User is prompted to complete profile (name, DOB, blood group, emergency contact)
10. User completes profile and lands on the dashboard
11. Dashboard shows empty state with prompts to add first doctor, medication, or visit

### Flow 2: Adding a Medication with Auto-Generated Chart

1. User navigates to "Medications" from the sidebar
2. User clicks "Add Medication"
3. User starts typing medication name and sees autocomplete suggestions
4. User selects medication from catalog OR enters custom medication name
5. User enters dosage (e.g., "500mg")
6. User selects frequency (e.g., "Twice daily")
7. User enters duration (e.g., "30 days")
8. User selects prescribing doctor from dropdown (or adds a new doctor)
9. User adds optional notes (e.g., "Take with breakfast and dinner")
10. User clicks "Save"
11. System validates input and saves the medication
12. System auto-generates a medication chart showing 60 doses over 30 days
13. User is redirected to medication detail view showing the generated chart
14. Medication appears in the active medications list
15. Dashboard updates to show the new medication in "Today's Medications"

### Flow 3: Uploading a Test Report

1. User navigates to "Test Reports" from the sidebar
2. User clicks "Upload Report"
3. User chooses to "Take Photo" or "Select from Gallery"
4. User captures/selects the test report image
5. System validates file type and size
6. User enters test name (e.g., "Complete Blood Count")
7. User selects test date
8. User selects associated doctor (optional)
9. User adds notes (optional, e.g., "Fasting blood sugar test")
10. User clicks "Save"
11. System uploads and stores the image
12. Report appears in the reports list with thumbnail and metadata
13. Dashboard updates to show recent activity: "Uploaded report: Complete Blood Count"

### Flow 4: Scheduling a Doctor Visit and Receiving Reminders

1. User navigates to "Visits" from the sidebar
2. User clicks "Schedule Visit"
3. User selects a doctor from the dropdown
4. User selects date (future date only)
5. User selects time
6. User enters reason for visit (e.g., "Follow-up for blood pressure")
7. User clicks "Save"
8. Visit appears in the upcoming visits list
9. Dashboard updates to show the upcoming visit
10. 24 hours before the visit: User receives in-app notification and email reminder
11. 1 hour before the visit: User receives in-app notification and email reminder
12. After the visit: User can add post-visit notes

### Flow 5: Viewing Doctor's Prescription History

1. User navigates to "Doctors" from the sidebar
2. User clicks on a specific doctor (e.g., "Dr. Smith - Cardiologist")
3. User sees doctor details (name, specialty, clinic, contact)
4. User clicks "Prescription History" tab
5. System displays all medications prescribed by this doctor
6. User can click on any medication to see its details and chart

### Flow 6: Caregiver Managing Patient Profiles

1. User (caregiver) registers or logs in with their own account
2. User navigates to "My Profiles" from the sidebar or header dropdown
3. User clicks "Add Patient Profile"
4. User enters patient details: name, date of birth, blood group, relationship (e.g., "Mother", "Father", "Child")
5. User clicks "Save" - new patient profile is created and linked to caregiver account
6. User can switch between profiles using a profile selector dropdown in the header
7. When a patient profile is selected, all data shown (medications, doctors, reports, visits) belongs to that patient
8. Caregiver can add medications, schedule visits, upload reports for the selected patient
9. Caregiver can add another patient profile (e.g., managing both parents)
10. Each patient's data is completely separate - no cross-contamination

---

## 7. Wireframe References

<!-- Wireframe: Login Page -->
- Email input field
- Password input field
- "Login" button
- "Forgot Password?" link
- "Don't have an account? Register" link

<!-- Wireframe: Registration Page -->
- Email input field
- Password input field
- Confirm password input field
- "Register" button
- "Already have an account? Login" link

<!-- Wireframe: Dashboard -->
- Header with user name and logout
- Sidebar navigation (Dashboard, Medications, Doctors, Reports, Visits, Notifications)
- "Today's Medications" card with list of medications and taken/pending status
- "Upcoming Visits" card with next 3 appointments
- "Recent Activity" card with last 5 actions
- Quick action buttons (Add Medication, Schedule Visit, Upload Report)

<!-- Wireframe: Medications Page -->
- "Active Medications" tab and "Completed" tab
- List of medications with name, dosage, frequency, prescribing doctor
- "Add Medication" button
- Click on medication to view detail/chart

<!-- Wireframe: Medication Autocomplete -->
- Search input with autocomplete dropdown
- List of matching medications with generic name and category
- "Add custom medication" option when no match found

<!-- Wireframe: Medication Detail / Chart -->
- Medication name, dosage, frequency, duration, prescribing doctor
- Auto-generated schedule chart (calendar or list view)
- Dose status indicators (pending/taken/missed)
- "Mark as Taken" button for current dose
- "Edit" and "Delete" buttons

<!-- Wireframe: Doctors Page -->
- List of doctors with name, specialty, clinic
- "Add Doctor" button
- Click on doctor to view details and prescription history

<!-- Wireframe: Test Reports Page -->
- Grid/list of uploaded reports with thumbnails
- Filter by doctor or test type
- "Upload Report" button
- Click on report to view full image and metadata

<!-- Wireframe: Visits Page -->
- "Upcoming Visits" and "Past Visits" tabs
- Calendar view toggle
- List of visits with date, time, doctor, reason
- "Schedule Visit" button

<!-- Wireframe: Notifications Page -->
- List of notifications (medication reminders, visit reminders)
- Mark as read/unread
- Notification preferences link

<!-- Wireframe: Notification Preferences -->
- Toggle switches for: Medication reminders, Visit reminders
- Channel selection: In-app, Email, Push (if enabled)

<!-- Wireframe: Profile Selector -->
- Dropdown in header showing current patient name
- "Switch Profile" option to change active patient
- "Add Patient Profile" button
- List of linked patient profiles with relationship labels

<!-- Wireframe: Export Options -->
- "Export" button on Medications page
- Export modal with format selection (PDF, CSV)
- Download confirmation message

---

## 8. Success Metrics

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| User Registration Rate | N/A | 500 registrations/month by month 6 | Analytics |
| Daily Active Users (DAU) | N/A | 30% of registered users | Analytics |
| Medication Adherence Rate | N/A | 80% of scheduled doses marked as taken | App analytics |
| Missed Appointment Rate | N/A | 50% reduction vs. baseline | User survey + app data |
| Average Medications per User | N/A | 3+ medications tracked | Database analytics |
| Average Reports per User | N/A | 2+ reports uploaded | Database analytics |
| Notification Delivery Rate | N/A | 99% successful delivery | Notification service logs |
| User Satisfaction Score | N/A | 4.2/5.0 | In-app survey (30-day post-onboarding) |
| Task Completion Rate | N/A | 85% (add med, schedule visit, upload report) | User analytics |
| Time to First Value | N/A | < 5 minutes (first medication added) | Session tracking |

---

## 9. Dependencies

| Dependency | Type | Impact | Owner | Notes |
|-----------|------|--------|-------|-------|
| SendGrid API | External | Email delivery for verification and notifications | Backend Team | Requires API key and sender verification; BAA required for PHI in emails; Transactional templates needed for: verification email, password reset, medication reminders, visit reminders |
| Firebase Cloud Messaging (FCM) | External | Browser push notifications | Frontend/Backend | Requires Firebase project setup; FCM config (server key, sender ID); Service worker for push handling; BAA required if notifications contain PHI |
| Cloud Storage (AWS S3 or equivalent) | External | Test report image storage | DevOps | Requires bucket setup with access policies; BAA required; Bucket structure: `/{user-id}/reports/{report-id}/{filename}`; Lifecycle policies for old versions; Server-side encryption (SSE-S3 or SSE-KMS) |
| PostgreSQL Database | Internal | Data persistence | Backend Team | Requires schema design and migration setup; HIPAA-compliant configuration; Encryption at rest enabled |
| Node.js/Express Backend | Internal | API layer | Backend Team | Core dependency |
| React Frontend | Internal | User interface | Frontend Team | Core dependency |
| JWT Authentication Library | Internal | Token-based auth | Backend Team | e.g., jsonwebtoken, passport-jwt |
| Image Processing Library | Internal | Client-side image compression | Frontend Team | e.g., browser-image-compression; Server-side: Sharp for thumbnail generation |
| Audit Logging Service | Internal | HIPAA-compliant audit trails | Backend Team | Append-only log storage; Separate from application database for immutability |
| Medication Master Data | Internal | Pre-populated medication catalog | Backend Team | Seed data with 500+ common medications |

**SendGrid Template Requirements:**
- Email Verification: Welcome message with verification link (24-hour expiry)
- Password Reset: Reset link (1-hour expiry)
- Medication Reminder: Medication name, dosage, scheduled time
- Visit Reminder (24h): Doctor name, appointment time, location
- Visit Reminder (1h): Doctor name, appointment time, location

**Firebase Configuration:**
- Project setup with FCM enabled
- VAPID keys for web push
- Service worker registration for background push handling
- Topic subscriptions for notification types

**S3 Bucket Structure:**
```
patient-health-tracker-uploads/
├── {user-id}/
│   ├── reports/
│   │   ├── {report-id}/
│   │   │   ├── original.{ext}
│   │   │   ├── thumbnail.{ext}
│   │   │   └── compressed.{ext}
│   │   └── ...
│   └── ...
```
- Access: Private by default; presigned URLs for temporary access
- Lifecycle: Move to Glacier after 1 year; delete after 7 years (configurable)
- Versioning: Enabled for compliance

---

## 10. Timeline Estimates

| Phase | Features | Duration | Dependencies |
|-------|----------|----------|-------------|
| **Phase 1: Foundation** | User Auth (US-001 to US-005), Profile, Caregiver Profile Management (US-036 to US-038), Dashboard Shell | 4 weeks | None |
| **Phase 2: Core Health Tracking** | Medication Management (US-006 to US-011), Doctor Management (US-012 to US-013), Prescription Linking (US-014 to US-016) | 4 weeks | Phase 1 |
| **Phase 3: Reports & Visits** | Test Report Upload (US-017 to US-020), Doctor Visit Scheduling (US-021 to US-024) | 3 weeks | Phase 1 |
| **Phase 4: Notifications** | Medication Reminders (US-026), Visit Reminders (US-025), Notification Preferences (US-027 to US-029) | 3 weeks | Phase 2, Phase 3 |
| **Phase 5: Data Export & Dashboard** | Data Export (US-042 to US-045), Dashboard Completion (US-030 to US-031), UI/UX Polish | 2 weeks | Phase 2, Phase 3 |
| **Phase 6: Testing & Launch** | UAT, Performance Testing, Security Audit, Deployment | 2 weeks | All phases |
| **Total** | | **~18 weeks (4.5 months)** | |

---

## 11. Open Questions

1. **Caregiver Access**: Should the system support a caregiver managing health data on behalf of a patient (e.g., Maria managing her mother's data)? This would require multi-user access to a single health profile. **Status: ✅ Resolved** - Yes, caregiver access is in scope for MVP. Caregivers can create and manage multiple patient profiles.

2. **Medication Interaction Alerts**: Should the system flag potential drug interactions when multiple medications are added? This would require a drug interaction database/API. **Status: Deferred to Phase 2** - Requires third-party drug interaction API (e.g., RxNav, DrugBank); significant cost and complexity; not in MVP scope.

3. **Data Export**: Should patients be able to export their health data (medications, reports, visit history) as a PDF or CSV to share with new doctors? **Status: ✅ Resolved** - Yes, medication chart export as PDF and CSV is in scope. Full PHI export for HIPAA compliance is also required.

4. **Offline Support**: Should the app support offline access for viewing medications and marking doses as taken, with sync when online?

5. **Doctor Verification**: Should there be any verification process for doctors added by patients, or is it a free-form entry?

6. **Notification Timing Customization**: Should users be able to customize the exact timing of visit reminders (e.g., 48 hours instead of 24 hours)?

7. **Report OCR**: Should the system attempt to extract text from uploaded test reports (OCR) to make them searchable? **Status: ✅ Resolved** - Deferred to Phase 2. Will be implemented via external OCR API call (not built-in).

8. **Multi-tenancy for Families**: Should a single user account be able to manage health data for multiple family members, or should each patient have their own account? **Status: ✅ Resolved** - Yes, single user account can manage health data for multiple family members via patient profiles.

9. **Image Processing Details**: What are the specific requirements for image processing? **Resolved** - Thumbnails (150x150px), compression (max 1920px width, 80% quality), supported formats (JPEG, PNG, PDF), max size (10MB original, 2MB compressed).

10. **Quiet Hours Default**: What should be the default quiet hours setting for new users? **Recommendation**: 10 PM - 7 AM based on typical sleep patterns; user-configurable.

11. **Critical Medication Definition**: How should the system determine which medications are "critical" to bypass quiet hours? **Recommendation**: User-configurable flag per medication; default to non-critical.

---

*End of Product Requirements Document*
