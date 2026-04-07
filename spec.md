# spec.md — AI-Powered EMR System

> **Single source of truth.** Every prompt to AI, every task, every PR must reference this file.
> Version: 1.0 | Language: English | Network: Multi-clinic

---

## 0 — How to use this spec

When prompting Antigravity (or any AI) during development, always start with:

```
Read @spec.md first.
Task: [what you want to build]
Rules: match the spec exactly. Flag any ambiguity before coding.
```

---

## 1 — Project overview

**Product:** AI-Powered EMR (Electronic Medical Records) System
**Type:** Full-stack multi-tenant web application
**Purpose:** A modern, AI-assisted Electronic Medical Records platform for a network of multiple clinics and hospitals. Doctors, patients, and admins each have their own portal. AI agents assist doctors with diagnosis, prescriptions, lab analysis, and record summarization automatically.

### What makes this EMR special
- 5 AI agents work in the background to assist doctors
- Multi-clinic network — one platform, many clinics
- Patients can view their own records and book appointments
- AI reads lab reports and flags abnormal results instantly
- AI checks drug interactions before prescriptions are saved

### The 3 portals

| Portal | Users | Purpose |
|---|---|---|
| Doctor portal | Doctors, Nurses | Patient care, records, prescriptions, AI assistance |
| Patient portal | Patients | View records, book appointments, see prescriptions |
| Admin panel | Super admin, Clinic admin | Manage clinics, users, billing, settings |

---

## 2 — Tech stack

### Frontend
| Concern | Choice |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript (strict mode) |
| Styling | Tailwind CSS |
| UI components | shadcn/ui |
| State management | Zustand + TanStack Query |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| Tables | TanStack Table |
| Auth | NextAuth.js (JWT) |
| Deployment | Vercel |

### Backend
| Concern | Choice |
|---|---|
| Framework | FastAPI (Python 3.12+) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 + Alembic |
| Auth | JWT (python-jose) + bcrypt |
| AI agents | OpenAI GPT-4o via openai SDK |
| Agent orchestration | Custom orchestrator (FastAPI background tasks) |
| Background jobs | Celery + Redis |
| File storage | Local filesystem (upgrade later) |
| Deployment | Railway |

### Infrastructure
| Concern | Choice |
|---|---|
| Frontend | Vercel |
| Backend | Railway |
| Database | Railway PostgreSQL |
| Cache / Queue | Railway Redis |
| AI | OpenAI API |
| Environment | .env.local (Next.js) + Railway env vars |

---

## 3 — Multi-clinic architecture

This is a **multi-tenant** system. Each clinic is a separate tenant.

```
[Super Admin]
      │
      ├── Clinic A (e.g. City Hospital)
      │     ├── Clinic Admin
      │     ├── Doctors
      │     ├── Nurses
      │     └── Patients
      │
      ├── Clinic B (e.g. Health Center)
      │     ├── Clinic Admin
      │     ├── Doctors
      │     └── Patients
      │
      └── Clinic C ...
```

### Tenancy rules
- Every database record has a `clinic_id`
- Doctors only see patients from their clinic
- Clinic admins only manage their own clinic
- Super admin sees everything across all clinics
- Patients belong to one clinic (can transfer)
- API routes enforce clinic isolation at query level

---

## 4 — User roles

| Role | Description |
|---|---|
| `super_admin` | Full access across all clinics |
| `clinic_admin` | Full access within their clinic only |
| `doctor` | Manage patients, records, prescriptions in their clinic |
| `nurse` | View patients, update vitals, assist doctor |
| `patient` | View own records, book appointments, see prescriptions |
| `receptionist` | Manage appointments, check-in patients, billing |

---

## 5 — The 5 AI agents

This is the core of the system. Each agent is a specialized GPT-4o powered service.

### Agent 1 — Diagnosis agent
**Trigger:** Doctor enters patient symptoms and clicks "Get AI Suggestions"
**What it does:**
- Reads patient history, current symptoms, vitals, age, gender
- Suggests top 3 possible diagnoses with confidence %
- Lists recommended tests for each diagnosis
- Flags any red flag symptoms that need urgent attention
- Doctor reviews and accepts, modifies, or rejects suggestions

**Input to GPT-4o:**
```
Patient age, gender, symptoms, vitals, medical history,
current medications, allergies, recent lab results
```

**Output:**
```json
{
  "diagnoses": [
    {
      "name": "Type 2 Diabetes",
      "confidence": 78,
      "reasoning": "...",
      "recommended_tests": ["HbA1c", "Fasting glucose"],
      "red_flags": []
    }
  ]
}
```

---

### Agent 2 — Records summary agent
**Trigger:** Doctor opens a patient profile
**What it does:**
- Reads all past visits, records, lab results, prescriptions
- Generates a clean 1-page summary of the patient's health history
- Highlights: chronic conditions, allergies, current medications, recent abnormal results
- Updates summary automatically when new records are added

**Output:** Plain text summary shown at top of patient profile

---

### Agent 3 — Prescription agent
**Trigger:** Doctor writes a new prescription
**What it does:**
- Checks for drug-drug interactions with current medications
- Checks for drug-allergy conflicts
- Suggests appropriate dosage based on patient weight, age, kidney/liver status
- Warns if prescribed dose is outside safe range
- Suggests generic alternatives if available

**Output:**
```json
{
  "interactions": [],
  "allergy_conflicts": [],
  "dosage_suggestion": "500mg twice daily",
  "warnings": [],
  "generic_alternatives": ["Paracetamol 500mg"]
}
```

---

### Agent 4 — Lab results agent
**Trigger:** Lab result is uploaded (PDF or image)
**What it does:**
- Reads and extracts values from the lab report
- Flags abnormal values with severity: mild / moderate / critical
- Explains each abnormal value in plain language
- Suggests follow-up actions
- Links findings to patient's current diagnosis

**Output:**
```json
{
  "extracted_values": [
    {
      "test": "HbA1c",
      "value": "9.2%",
      "normal_range": "< 5.7%",
      "status": "critical"
    }
  ],
  "summary": "HbA1c is critically elevated indicating poor diabetes control.",
  "recommended_actions": ["Adjust insulin dosage", "Book follow-up in 2 weeks"]
}
```

---

### Agent 5 — Billing agent
**Trigger:** Doctor marks visit as complete
**What it does:**
- Reads all services provided during the visit
- Looks up clinic fee schedule
- Auto-generates itemized invoice
- Calculates any applicable discounts
- Marks which items may be covered by insurance

**Output:** Draft invoice ready for receptionist to review and send

---

### AI orchestrator
The orchestrator decides which agent to call and when:

```
Doctor opens patient     → Records summary agent runs automatically
Doctor enters symptoms   → Diagnosis agent runs on demand
Doctor writes rx         → Prescription agent runs automatically
Lab result uploaded      → Lab results agent runs automatically
Visit marked complete    → Billing agent runs automatically
```

All agent calls are:
- Asynchronous (never block the UI)
- Logged in `ai_jobs` table with status and result
- Retried automatically on failure (max 3 retries)
- Cost tracked per call in `ai_cost_usage` table

---

## 6 — Module list

### Doctor portal modules
1. Dashboard — today's appointments, AI alerts, pending tasks
2. Patient list — search, filter, view all patients
3. Patient profile — full history + AI summary at top
4. New visit / SOAP note — structured visit documentation
5. Appointments — schedule, view, manage
6. Medical records — upload, view, manage
7. Prescriptions — write, view, AI interaction check
8. Lab results — view, upload, AI analysis
9. Vitals tracking — record and chart vitals
10. AI assistant — diagnosis help, ask AI anything about patient

### Patient portal modules
1. Dashboard — upcoming appointments, recent activity
2. My records — all medical records
3. My prescriptions — active and past prescriptions
4. My lab results — results with plain language AI explanation
5. Book appointment — select doctor, date, time
6. My vitals — vitals history chart
7. Messages — message my doctor

### Admin panel modules
1. Dashboard — all clinics overview, key metrics
2. Clinic management — add, edit, configure clinics
3. User management — manage all users per clinic
4. Patient management — all patients across network
5. Appointments overview — platform-wide appointments
6. Billing & invoices — all invoices and payments
7. AI monitoring — agent jobs, costs, errors
8. Reports & analytics — usage, health trends, revenue
9. System settings — feature flags, configuration

---

## 7 — Database schema

> All tables include: `id` (uuid PK), `clinic_id` (uuid FK), `created_at`, `updated_at`, `deleted_at` (soft delete)

### Core tables

```
clinics                 — clinic and hospital profiles
users                   — all users (all roles)
user_roles              — role per user per clinic
patients                — patient demographic profiles
doctors                 — doctor profiles and specialties
appointments            — visit scheduling
visits                  — completed visit records (SOAP notes)
medical_records         — uploaded documents
vitals                  — patient vitals per visit
diagnoses               — diagnoses linked to visits
prescriptions           — prescription records
prescription_items      — individual drugs per prescription
lab_results             — lab result uploads
lab_result_values       — extracted individual test values
invoices                — billing invoices
invoice_items           — line items per invoice
fee_schedules           — clinic pricing per service
ai_jobs                 — AI agent job queue and results
ai_cost_usage           — token and cost tracking per call
audit_logs              — immutable action log
notifications           — in-app notifications per user
messages                — doctor-patient messages
```

---

## 8 — API structure

```
/api/v1/auth/            — login, logout, refresh, me
/api/v1/clinics/         — clinic management (admin only)
/api/v1/users/           — user management
/api/v1/patients/        — patient records
/api/v1/doctors/         — doctor profiles
/api/v1/appointments/    — scheduling
/api/v1/visits/          — visit/SOAP notes
/api/v1/records/         — medical record uploads
/api/v1/vitals/          — vitals
/api/v1/diagnoses/       — diagnoses
/api/v1/prescriptions/   — prescriptions
/api/v1/lab-results/     — lab results
/api/v1/invoices/        — billing
/api/v1/ai/diagnose      — diagnosis agent
/api/v1/ai/summarize     — records summary agent
/api/v1/ai/check-rx      — prescription agent
/api/v1/ai/analyze-lab   — lab results agent
/api/v1/ai/billing       — billing agent
/api/v1/ai/jobs          — AI job status and history
/api/v1/reports/         — analytics
/api/v1/settings/        — system config
```

### Response envelope
```json
{
  "data": {},
  "error": null,
  "meta": { "page": 1, "per_page": 50, "total": 100 }
}
```

---

## 9 — Auth & security

- JWT access token: 15 min expiry
- Refresh token: 7 days in httpOnly cookie
- Every route has role guard
- Every query filters by `clinic_id` — data never crosses clinics
- 2FA mandatory for `super_admin`
- Brute force: lock after 5 failed attempts for 15 min
- Audit log on every create, update, delete action
- Patients only see their own data

---

## 10 — Non-functional requirements

| Requirement | Target |
|---|---|
| Page load | < 2 seconds |
| AI agent response | < 10 seconds |
| API response (p95) | < 500ms |
| Uptime | 99.9% |
| Language | English only |
| Device support | Desktop + tablet (responsive) |
| Accessibility | WCAG 2.1 AA |

---

## 11 — Out of scope (v1)

- Telemedicine / video calls
- Insurance claims processing
- Native mobile app
- DICOM imaging viewer
- Pharmacy system integration
- Wearable device data
- SMS / WhatsApp notifications

---

## 12 — Success criteria

- [ ] All 3 portals working with correct role-based access
- [ ] Multi-clinic isolation — doctor in clinic A cannot see clinic B
- [ ] All 5 AI agents triggered and returning results
- [ ] Diagnosis agent suggests top 3 diagnoses from symptoms
- [ ] Prescription agent catches drug-drug interactions
- [ ] Lab results agent flags abnormal values with severity
- [ ] Billing agent auto-generates invoice on visit completion
- [ ] Records summary auto-generates when doctor opens patient
- [ ] Appointments can be booked, modified, cancelled
- [ ] All actions written to audit_logs
- [ ] AI job costs tracked per call

---


---

*End of spec.md — v1.0*