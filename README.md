# AjiriNow (Backend)

Django REST backend for **AjiriNow** — a platform serving the fast-growing town of **Meru**, connecting **construction workers (fundis)** with **clients and businesses**.

**What it does**
- Fundis get a **7-day free trial**, then pay a **monthly subscription (M-Pesa)** to appear on a public directory and **browse jobs**.
- Clients can **post jobs** (paid) and optionally **post ads** (paid).
- Businesses can **run ads** to reach fundis and clients.

**Stack**: Django REST Framework · PostgreSQL · JWT Auth · M-Pesa · Docker/Compose · Render

## 🚀 Core Features

- **Fundis (Workers)**
  - Register → Login → **7-day free trial**
  - Trial active: **listed** in public directory + **can browse jobs**
  - After trial: must **subscribe monthly (M-Pesa)** to stay listed & keep access
  - Expired/unpaid: **hidden** from directory + **no job access**

- **Clients**
  - Register → Login → **Post jobs** (requires payment to go live)
  - Optionally **post ads** (paid)

- **Businesses**
  - **Create ads** (paid) visible to fundis & clients

## 🧩 Business Logic (Backend Rules)

- **Trial**
  - Starts at fundi registration: `trial_end_at = created_at + 7 days`
  - Access gates check: `is_trial_active OR is_subscription_active`

- **Subscription**
  - Monthly billing via **M-Pesa** (STK Push)
  - On **successful payment** → mark active, set `current_period_end`
  - On **expiry** → background task marks account inactive/hidden

- **Jobs**
  - Job becomes **active** after successful client payment
  - Fundis can **browse/apply** only if access gate passes

- **Ads**
  - Visible only after payment confirmation

- **Payments**
  - Unified payment records: `type ∈ {SUBSCRIPTION, JOB_POST, AD}` with gateway refs
  - Webhook/callback validates payment and updates domain state

## 🛠️ Tech Stack

- **Backend**: Django REST Framework (Python)
- **Database**: PostgreSQL
- **Auth**: JWT (access/refresh)
- **Payments**: M-Pesa (STK Push)
- **DevOps**: Docker & Docker Compose
- **Deploy**: Render (Dockerized)
- **Testing**: Manual (automated tests planned)

---

## Part 6 — Data Model (quick sketch)

```markdown
## 🗃️ Data Model (Simplified)

- **User**(id, email, password_hash, role ∈ {FUNDI, CLIENT, BUSINESS}, created_at)
- **FundiProfile**(user_id FK, skills[], location, is_listed, trial_end_at, subscription_status, current_period_end)
- **Subscription**(id, fundi_id FK, status, period_start, period_end, latest_payment_id FK)
- **Job**(id, posted_by=Client FK, title, location, budget, skills[], status ∈ {pending_payment, active, closed}, created_at)
- **Application**(id, job_id FK, fundi_id FK, status ∈ {applied, accepted, rejected}, created_at)
- **Ad**(id, business_user_id FK, title, body, status ∈ {pending_payment, active, expired}, created_at)
- **Payment**(id, type ∈ {SUBSCRIPTION, JOB_POST, AD}, amount, currency, status ∈ {pending, success, failed}, gateway="mpesa", gateway_ref, user_id FK, object_ref (job/ad/subscription), created_at)
```
----
## 🔐 Environment Variables

** Django**
SECRET_KEY=
DEBUG=1
ALLOWED_HOSTS=**

** DB**
DATABASE_URL=postgres://user:pass@localhost:5432/ajirinow
** OR individual: **
DB_NAME=ajirinow
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

**JWT**
JWT_ACCESS_TTL=15m
JWT_REFRESH_TTL=7d

**M-Pesa (STK Push)**
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_PASSKEY=
MPESA_SHORTCODE=
MPESA_CALLBACK_URL=https://your-domain.com/api/payments/mpesa/callback

**App**
TIME_ZONE=Africa/Nairobi

## ⚙️ Local Setup

```bash
# Clone the repository
git clone https://github.com/<you>/ajirinow.git
cd ajirinow

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver


**admin (optional)**
python manage.py createsuperuser

** 🐳 Docker**

**Build & run**
docker-compose up --build

**Apply migrations inside the container (if needed)**
docker-compose exec web python manage.py migrate
```
---

**💸 Payments (M-Pesa)**

- Uses **STK Push** for:
  - Fundi **subscriptions** (monthly)
  - Client **job posts**
  - Business **ads**

**Flow**
1) Backend creates `Payment(pending)` with `type` and target object (subscription/job/ad)
2) Call STK Push → prompt user on phone
3) M-Pesa hits `MPESA_CALLBACK_URL`
4) Backend verifies callback → updates `Payment(success|failed)`
5) On **success**:
   - Subscription: mark fundi active, set `current_period_end`
   - Job/Ad: mark **active/published**
---

## 🔗 API Quickstart

### Auth: Register (Fundi)
POST /api/auth/register
```json
{
  "email": "fundi@example.com",
  "password": "StrongPass!123",
  "role": "FUNDI"
}
```

### Auth: Login
POST /api/auth/login
```
json {
  "email": "fundi@example.com",
  "password": "StrongPass!123"
}
→ { "access": "...", "refresh": "..." }
```
### Fundi: My Access Status
GET /api/fundis/me/access
Authorization: Bearer <access>
→ ```json 
{ "trial_active": true, "subscription_active": false, "is_listed": true, "trial_end_at": "2025-09-08T12:00:00Z" }```

### Fundi: Start Subscription (initiate payment)
POST /api/payments/subscription
Authorization: Bearer <access>
→ ```json{ "payment_id": 101, "status": "pending", "mpesa_checkout_request_id": "..." }```

### Client: Post Job (after payment)
POST /api/jobs
Authorization: Bearer <access>
```json
{
  "title": "Need 3 plumbers for 2 days",
  "location": "Mru",
  "budget": 15000,
  "skills": ["plumbing"]
}
```
→ job is pending_payment` until M-Pesa callback marks it active
---
## ✅ Manual Test Checklist

- Auth: register/login (Fundi, Client, Business)
- Trial: fundi created → `trial_end_at = +7d` → can list & browse
- Gate: after trial expires (simulate), fundi cannot browse and is hidden
- Subscription: STK push success → fundi listed + access restored
- Jobs: client creates job → pending until payment callback → becomes active
- Ads: business creates ad → pending until payment callback → becomes active
- Payments: verify records saved with gateway refs; idempotent callbacks
---
## 🔮 Roadmap

- Automated tests (pytest/DRF) + dockerized test runner
- Background scheduler for subscription expiry sweeps
- Notifications (email/SMS) for jobs & expiries
- Ratings & reviews for fundis
- Advanced search & filters (skills, location, availability)
- Admin dashboard (payments, churn, active subscriptions)
- Observability: structured logs, basic metrics, request IDs
