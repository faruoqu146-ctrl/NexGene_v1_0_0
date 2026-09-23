
NexGene v1.0.0

«Build the biological picture before the disease becomes the story.»

NexGene is a longitudinal personal-data platform designed to progressively build a richer picture of an individual's health and biology.

v1.0.0 is the Lifestyle Layer.

It currently focuses on lifestyle observations, simple physiological signals, personal context, longitudinal patterns, and cautious weekly reports.

NexGene is not a medical device, diagnostic system, or clinical decision-support system in this release.

---

Vision

The long-term NexGene architecture is built around four progressively integrated data layers:

Phase| Domain| Status
Phase 1| Lifestyle| 🟢 v1.0.0
Phase 2| Physiology| Planned
Phase 3| Clinical| Planned
Phase 4| Genomic| Planned

The long-term objective is to combine these layers into a longitudinal biological profile that can support research and, eventually, more precise approaches to prevention and medicine.

The current release is deliberately much narrower.

Build the foundation first.

---

What v1.0.0 Does

NexGene currently supports:

- Account registration and authentication
- Secure session management
- Morning and evening check-ins
- Personal context
- Lifestyle observations
- Simple physiological signal entry
- Timeline of observations
- Pattern summaries
- Signal generation
- Early insights
- Weekly NexGene reports
- CSRF protection
- Per-user data isolation
- Rate limiting
- Request-size validation
- Password reset and email-verification flows
- Development security testing

Core user loop

Record
   ↓
Observe
   ↓
Discover
   ↓
Return
   ↓
Accumulate longitudinal data
   ↓
Weekly report
   ↓
Discover more

The goal is not to manufacture certainty from limited data.

The system uses cautious language around patterns and avoids presenting short-term observations as diagnoses or established causal relationships.

---

Current Product Surface

Today

Morning and evening check-ins, current snapshot, signals, and early observations.

Patterns

Longer-term summaries based on accumulated observations, including approximately 30-day views where sufficient data exists.

Report

A weekly narrative containing:

- Data coverage
- Observed relationships
- Positive observations
- One suggested experiment

The report is intentionally non-clinical and does not claim that one week establishes causation.

Timeline

Chronological history of recorded observations.

Context

Optional information that helps interpret observations, including:

- Age range
- Country
- Occupation
- Student status
- Field of study
- Schedule
- Timezone

Context is used as analytical context rather than as a basis for demographic stereotypes or automatic health conclusions.

---

Architecture

                 ┌─────────────────────┐
                 │     Mobile SPA      │
                 │       /static       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │       FastAPI       │
                 │      REST API       │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Auth         Data Layer     Reports
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                    SQLAlchemy 2.x
                            │
                            ▼
                         SQLite

Stack

- Backend: FastAPI
- Database: SQLite / SQLAlchemy 2.x
- Frontend: Mobile-oriented SPA
- Authentication: HttpOnly cookie sessions + CSRF protection
- Password hashing: PBKDF2-SHA256
- Deployment: Docker / Docker Compose
- Runtime: Python

---

API

Primary API groups include:

Authentication

POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/csrf
GET  /api/v1/auth/me
...

Data

POST /api/v1/checkins/morning
POST /api/v1/checkins/evening
GET  /api/v1/today
GET  /api/v1/timeline
GET  /api/v1/patterns
GET  /api/v1/signals
GET  /api/v1/insights

v1.0 additions

GET /api/v1/profile
PUT /api/v1/profile

GET /api/v1/reports/weekly

Operations

GET /api/v1/health

---

Security

Security is treated as a core part of the development architecture rather than a final deployment step.

Current controls include:

- Password policy requiring 12+ characters
- Uppercase, lowercase, number, and symbol requirements
- PBKDF2-SHA256 with 600,000 rounds
- Dummy password verification for missing accounts
- Uniform authentication errors
- HttpOnly session cookies
- CSRF token protection
- Server-side CSRF validation
- Session revocation on logout
- Session revocation following password reset
- IP/action rate limiting
- Request body limits
- Check-in payload validation
- Per-user authorization checks
- Restricted CORS configuration
- Production configuration gates
- API documentation disabled outside development mode

---

Security Verification

v1.0.0 has undergone an authorized local security and adversarial assessment.

Automated verification

14 tests passed in the previously clean unit/contract run.

Concurrent testing

24/24 concurrent user journeys succeeded.

Test journey:

Register
→ Profile
→ Check-in
→ Signals
→ Patterns
→ Report
→ Account

Adversarial testing

42/42 probes passed.

Test areas included:

- Weak passwords
- Account enumeration
- Authentication error consistency
- CSRF bypass attempts
- Session reuse after logout
- Cross-user data access
- Unauthenticated API access
- Unknown check-in types
- Oversized text
- Excessive payload keys
- Oversized request bodies
- Path probing
- Login throttling
- Concurrent check-in requests

These results apply to the local development build and should not be interpreted as a production penetration test.

---

Development Setup

Requirements

- Python 3.x
- pip
- Docker (optional)

Clone

git clone https://github.com/faruoqu146-ctrl/NexGene_v1_0_0.git
cd NexGene_v1_0_0

Install dependencies

pip install -r requirements.txt

Development environment

Set:

DEV_MODE=true

Configure the local database:

DATABASE_URL=sqlite:///./nexgene.db

Run the application using the project's configured FastAPI entry point.

The local development environment may expose interactive API documentation.

Do not expose a DEV_MODE deployment to the public internet.

---

Testing

Unit / contract suite:

DATABASE_URL=sqlite:////tmp/nexgene_test.db pytest -q

Concurrent stress testing:

python scripts/live_stress.py --users 24 --gets 80

Adversarial probes:

python scripts/adversarial_probe.py

Health check:

GET /api/v1/health

Expected development response:

{
  "status": "ok",
  "version": "1.0.0"
}

---

Production Status

NexGene v1.0.0 is not production-ready.

Before public or multi-tenant deployment:

- Set "DEV_MODE=false"
- Generate a strong random "SECRET_KEY"
- Enforce HTTPS
- Set "COOKIE_SECURE=true"
- Replace local SQLite with a managed database
- Disable "/docs"
- Disable "/redoc"
- Disable "/openapi.json"
- Remove development reset/verification tokens from external responses
- Configure real email delivery for verification and password reset
- Implement backups
- Configure monitoring
- Ensure logs do not contain passwords, tokens, or unnecessary personal data
- Re-run the complete test suite against staging
- Perform an independent security review before introducing clinical or genomic data

---

Current Limitations

v1.0.0 does not currently provide:

- Clinical data ingestion
- Genetic or genomic data ingestion
- Hospital-system integration
- Medical diagnosis
- Clinical decision support
- Validated disease prediction
- Continuous molecular monitoring
- Continuous wearable-device integration
- Medical-grade physiological monitoring

The long-term architecture may support these domains, but they are outside the scope of this release.

---

Roadmap

Phase 1 — Lifestyle

Current

Build a longitudinal record of lifestyle and contextual observations.

Phase 2 — Physiology

Future integration of richer physiological measurements and potentially external sensor/wearable data.

Phase 3 — Clinical

Future integration of structured clinical information, subject to appropriate consent, interoperability, privacy, security, and clinical governance requirements.

Phase 4 — Genomic

Future integration of genomic information and associated biological data.

The four layers are ultimately intended to become interoperable rather than isolated datasets.

             NEXGENE
                │
      ┌─────────┼─────────┐
      │         │         │
  Lifestyle  Physiology  Clinical
      │         │         │
      └─────────┼─────────┘
                │
             Genomic
                │
                ▼
     Longitudinal Biological Profile

---

Design Principle

NexGene is being built around a simple premise:

«A person's biology is not a snapshot.»

Lifestyle changes.
Physiology changes.
Clinical states change.
Molecular states change.

NexGene's long-term purpose is to build the infrastructure necessary to observe those changes longitudinally and connect the layers responsibly.

v1.0.0 is only the beginning.

---

Status

Version: "1.0.0"
Stage: Development
Current layer: Lifestyle
Security assessment: Completed for defined local-development scope
Production status: Not ready

The Raven is building. 🐦‍⬛

---

