# RentReport — Rent Credit Reporting Platform

A full-stack rent credit reporting application modeled after RentPlus (by Entrata/Rent Dynamics).

Automatically enrolls residents, reports on-time rent payments to credit bureaus, and pays property managers a $3.00/month/resident revenue share.

---

## Architecture

```
rent-credit-app/
├── backend/          # FastAPI + PostgreSQL + Celery
│   └── app/
│       ├── api/      # REST endpoints
│       ├── models/   # SQLAlchemy ORM models
│       ├── schemas/  # Pydantic schemas
│       ├── services/ # Business logic (Stripe, PMS, Metro 2, Email)
│       └── tasks/    # Celery background jobs
├── frontend/         # Next.js 14 App Router
│   └── src/app/
│       ├── (marketing)   # Landing page
│       ├── auth/         # Login & registration
│       ├── dashboard/    # Property manager portal
│       └── resident/     # Resident portal
└── docker-compose.yml
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router), Tailwind CSS, TypeScript |
| Backend | FastAPI, SQLAlchemy (async), Alembic |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis + Celery |
| Payments | Stripe Subscriptions + Stripe Connect |
| Email | Resend |
| Credit Reporting | Metro 2 format via SFTP to Experian, Equifax, TransUnion |

---

## Key Features

### For Property Managers
- **Auto-enrollment workflow**: Residents are automatically enrolled 3 days after lease start
- **PMS Integrations**: RealPage, Yardi, AppFolio, Entrata (REST API adapters)
- **Revenue share**: $3.00/month per enrolled resident via Stripe Connect
- **Dashboard**: Resident enrollment stats, annual revenue projections, quick actions
- **Property management**: Multi-property support with per-property configuration

### For Residents
- **Automatic reporting**: On-time rent payments reported monthly to all 3 bureaus
- **Positive-only policy**: Late/missed payments are NEVER reported
- **Retroactive reporting**: Up to 24 months of past on-time payments, free
- **Free trial**: First month free; $8.95/month after trial
- **Easy opt-out**: Via portal, email link, or email/phone

### Technical
- **Metro 2 format**: FCRA-compliant fixed-width file generation for bureau SFTP submission
- **Celery scheduled tasks**: Nightly PMS sync, monthly bureau submission on the 18th, PM payouts on the 20th
- **Stripe webhooks**: Subscription lifecycle management (trial ending, payment failed, cancellation)
- **JWT auth**: Separate auth flows for property managers and residents

---

## Quick Start

```bash
# 1. Copy environment config
cp .env.example .env
# Edit .env with your Stripe keys, bureau SFTP credentials, etc.

# 2. Start all services
docker-compose up -d

# 3. The API will auto-create tables on startup
# API docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

## Environment Variables

See `.env.example` for all required configuration:
- `STRIPE_SECRET_KEY` / `STRIPE_PUBLISHABLE_KEY` — Stripe keys
- `STRIPE_CONNECT_CLIENT_ID` — For property manager payout accounts
- `STRIPE_RESIDENT_PRICE_ID` — $8.95/month recurring price in Stripe
- `RESEND_API_KEY` — For transactional emails
- `EXPERIAN/EQUIFAX/TRANSUNION_FTP_*` — Bureau SFTP credentials
- `REALPAGE/YARDI/APPFOLIO/ENTRATA_*` — PMS API keys

---

## Business Model

| Fee | Amount | Direction |
|-----|--------|-----------|
| Resident monthly fee | $8.95/month | Resident → RentReport |
| PM revenue share | $3.00/month/resident | RentReport → Property Manager |
| RentReport net | $5.95/month/resident | After PM payout |

A 200-unit building at 82% enrollment rate ≈ 164 enrolled residents:
- Annual PM payout: $5,904
- Annual RentReport revenue: $11,754

---

## Credit Bureau Reporting

Reporting follows the **CDIA Metro 2 format** (industry standard for FCRA-compliant furnishers):
- Files generated on the **18th of each month**
- Transmitted via **SFTP** to bureau upload endpoints
- **Positive-only**: Only `PaymentStatus.on_time` records are included
- Account type: `4C` (Rental Agreement), Portfolio type: `I` (Installment)

---

## PMS Integration Flow

```
1. PM configures PMS API credentials in Settings
2. Nightly Celery job calls PMS adapter → fetches residents + payment ledger
3. New residents auto-enrolled (pending → trial after delay_days)
4. RentPayment records upserted from PMS ledger data
5. Monthly: pending on_time payments → Metro 2 → bureau SFTP submission
6. PM revenue share transferred via Stripe Connect on the 20th
```

---

## License

Proprietary. All rights reserved.
