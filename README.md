## TalentHire – FastAPI Job Board & Hiring API

TalentHire is a backend API for a lightweight hiring platform where employers post jobs and candidates apply. It includes JWT-based auth, role-based access (employer vs candidate), advanced job search and filters, application tracking, and database indexes tuned for performance (with optional Redis caching).

## Features
- Authentication & roles: JWT login, OAuth2 password flow, employer vs candidate
- Employers: create/update/delete jobs, view applicants, update application status
- Candidates: register/update profile, apply to jobs, view their applications with job details
- Jobs: search by title/description, filter by location/salary/experience/status, popular (most applications), trendy (most viewed), view count tracking
- Database & performance: PostgreSQL + SQLAlchemy 2.0, Alembic migrations, GIN/B-Tree indexes for search/filters, indexed job applications
- Testing: pytest suite for employers, candidates, jobs, and login
- Optional caching: Redis (Docker)

## Tech Stack
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- JWT via python-jose, OAuth2PasswordBearer
- pytest
- Optional Redis for caching

## Project Structure
```
app/
  main.py          # FastAPI app entrypoint & router registration
  config.py        # Pydantic settings (env-based configuration)
  database.py      # SQLAlchemy engine, SessionLocal, Base, get_db()
  models.py        # SQLAlchemy models: Employer, Candidate, Job, CandidateJobApplication
  schema.py        # Pydantic schemas for requests/responses
  oauth2.py        # JWT creation, password hashing, current_user dependency
  routers/
    auth.py        # /login
    employers.py   # /employers
    candidates.py  # /candidates/me
    jobs.py        # /jobs and job-related endpoints
alembic/           # Alembic migrations & env
tests/             # pytest-based API tests
```

## Getting Started (Local Development)
### 1) Clone the repo
```bash
git clone <your-fork-url> talenthire
cd talenthire
```

### 2) Create & activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
# On Windows: .venv\Scripts\activate
```

### 3) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Infrastructure: Postgres & Redis via Docker
### PostgreSQL (required)
```bash
docker run -d \
  --name talenthire-postgres \
  -e POSTGRES_USER=talenthire \
  -e POSTGRES_PASSWORD=talenthire \
  -e POSTGRES_DB=talenthire \
  -p 5432:5432 \
  postgres:16-alpine
```
Adjust user/password/db as needed, but keep .env in sync.

### Redis (optional, for caching)
```bash
docker run -d \
  --name redis-talenthire \
  -p 6379:6379 \
  redis:7-alpine
```

## Configuration (.env)
Create a `.env` in the project root (same folder as `app/` and `alembic.ini`):
```
# Database
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=talenthire
DATABASE_PASSWORD=talenthire
DATABASE_NAME=talenthire

# JWT / Auth
SECRET_KEY=super-secret-key-change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional Redis (if you add caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```
These map to `app.config.Settings`.

## Database Migrations
Alembic migrations include indexes for:
- Trigram text search on job title/description (GIN)
- Filters on job location, salary range, experience range (B-Tree)
- View count ordering
- Job applications by job_id and candidate_id

Run migrations:
```bash
alembic upgrade head
```
Create a new migration later:
```bash
alembic revision -m "describe change"
# edit migration file
alembic upgrade head
```

## Run the API
From the project root:
```bash
uvicorn app.main:app --reload
```
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## High-Level API Overview
### Authentication
- POST `/login` – returns access_token (bearer)

### Employers
- POST `/employers` – register employer
- GET `/employers/{id}` – get employer
- GET `/employers` – list employers
- DELETE `/employers/{id}` – delete (employer-only auth)

### Candidates (prefix `/candidates/me`)
- POST `` – register candidate
- GET `` – current candidate profile
- PUT `` – update profile
- DELETE `` – delete profile
- GET `/my-applications` – candidate’s applications with job details

### Jobs (prefix `/jobs`)
- POST `` – create job (employer-only)
- GET `` – list jobs with filters:
  - `search` (title/description), `location`
  - `salary_min`, `salary_max`
  - `experience_min`, `experience_max`
  - `order_by` (default `created_at`), `order` (`asc`/`desc`)
  - `job_status`, `limit`, `skip`
- GET `/{id}` – get job by id (increments view count)
- DELETE `/{id}` – delete (owner employer only)
- PUT `/{id}` – update (owner employer only)
- POST `/{id}/apply` – candidate applies
- GET `/{id}/applicants` – employer views applicants
- PATCH `/{id}/candidate/{candidate_id}` – employer updates application status
- GET `/{id}/views` – get view count
- PATCH `/{id}/status` – update status (`active`/`expired`)
- GET `/job/popular` – job with most applications
- GET `/job/trendy` – job with highest view count

## Tests
Run all tests:
```bash
pytest
```
Tests cover employers, candidates, jobs (CRUD + filters + popular/trendy), views, applications, and login.

## Optional: Redis Caching (not wired by default)
If you add caching:
- Add Redis settings to `app.config.Settings`
- Create a Redis client helper
- Cache `GET /jobs` (2–5 min TTL) and `GET /jobs/job/popular` (5–10 min TTL)
- Invalidate caches on job create/update/delete

## Development Tips
- Use `/docs` to explore endpoints quickly.
- Keep `database-migration.md` updated with EXPLAIN ANALYZE results when adding indexes.
- New machine checklist:
  1) Docker up Postgres (and Redis if needed)
  2) Create `.env`
  3) `pip install -r requirements.txt`
  4) `alembic upgrade head`
  5) `uvicorn app.main:app --reload`
