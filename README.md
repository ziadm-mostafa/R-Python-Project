# LibreFlow - Library Management System

A full-stack Library Management System built as a university assignment, demonstrating **FastAPI** (backend) and **Angular** (frontend) with JWT authentication, role-based access control, Redis caching, SQL Server, Docker deployment, and comprehensive testing.

| Layer | Technology | Location |
|-------|-----------|----------|
| **Backend** | FastAPI (Python 3.12) | `library-management-system/` |
| **Frontend** | Angular 19 (Standalone) | `library-system/` |
| **Database** | SQL Server Express 2022 | Local instance |
| **Cache** | Redis 7 | Docker |

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Team Members & Role Assignments](#team-members--role-assignments)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Business Rules](#business-rules)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Docker Reference](#docker-reference)
- [Key Technical Decisions](#key-technical-decisions)
- [Tools & Technologies](#tools--technologies)

---

## Features

### JWT Authentication & Role-Based Access (3 marks)
- JWT token generation/validation via `python-jose` + `bcrypt`
- Role-based authorization: **Admin** (librarian) and **Member** (patron)
- Route protection on backend (FastAPI dependencies) and frontend (Angular guards)
- Login/register pages with inline validation and toast feedback

### Database Integration (2 marks)
- SQL Server via SQLAlchemy ORM with `get_db` dependency injection
- Three models: `User`, `Book`, `BorrowRecord` with proper relationships
- Unicode (NVARCHAR) support for all user-facing text fields

### Input Validation (3 marks)
- Pydantic schemas with `Field` constraints (ge=0, min_length, regex for ISBN)
- Separate `Create`, `Update`, and `Response` schemas per entity
- HTTP 422 with descriptive error details on validation failure

### Clean Code (2 marks)
- Modular architecture: `routers/`, `schemas/`, `models/`, `core/`, `cache/`, `monitoring/`
- Separation of concerns (routes, business logic, data access)
- Type hints throughout, consistent naming conventions

### Logging & Monitoring (3 marks)
- Structured logging with 5 severity levels (DEBUG through CRITICAL)
- Request/response middleware (method, path, status, duration)
- `GET /health` - database connectivity health check
- `GET /stats` - aggregate request metrics (total, failed, error rate, uptime)
- `GET /stats/recent-errors` - last 10 error log lines
- Angular `/admin/dashboard` - visual monitoring dashboard (admin-only)

### Redis Caching (2 marks)
- Cache-aside pattern on `GET /books` and `GET /books/{id}`
- Automatic cache invalidation on create, update, delete, borrow, and return
- Configurable TTL (60s default), graceful fallback when Redis is unavailable

### API Testing (1 mark)
- 11 pytest tests across 3 test files covering:
  - **Auth**: Registration, successful login, invalid login
  - **Books**: Admin CRUD, member forbidden, ISBN validation
  - **Borrow**: Borrow success, borrow limit enforcement, return
- Isolated `library_db_test` database with per-session setup/teardown

### Git & GitHub (1 mark)
- Feature branch workflow: `main` to `develop` to `feature/*`
- Meaningful commits per team member

### Frontend Bonus (2 marks)
- Angular 19 standalone components with Signals and zoneless change detection
- Tailwind CSS dark mode with responsive design
- Reactive forms with inline validation
- JWT auth interceptor with 401 redirect and toast error notifications
- Book cover upload (device or URL) with live image preview
- Optimistic UI updates with revert on error

### Docker Bonus (2 marks)
- `Dockerfile` with Python 3.12-slim, ODBC Driver 18, non-root user
- `docker-compose.yml` with Redis + backend, health checks, volume mounts

---

## Architecture

```
                        HTTP/JSON                   SQL
    Angular --------------------------- FastAPI -------------- SQL Server
    localhost:4200                     localhost:8001          localhost:53516
                                            |
                                           Redis
                                           Cache
```

### Auth Flow
1. User submits credentials to `POST /auth/login`
2. Backend verifies password hash, returns JWT `access_token`
3. Frontend stores token in `localStorage`, decodes user info
4. `AuthInterceptor` attaches `Authorization: Bearer <token>` to every request
5. Backend `get_current_user` / `get_current_admin` dependencies validate on each call
6. Frontend guards (`authGuard`, `adminGuard`) protect routes based on decoded role

---

## Team Members & Role Assignments

| Member | Role | Key Deliverables | Scoring Marks |
|--------|------|------------------|---------------|
| **Abdelrahman Ezat** | DevOps & Frontend Lead | Angular UI, Docker, Git/GitHub, pytest tests, README | Testing 1 + Git 1 + Frontend 2 + Docker 2 = **6** |
| **Ziad Mustafa** | Auth & Security Lead | JWT auth, registration/login, password hashing, role deps | JWT 3 = **3** |
| **Omar Khaled** | Business Logic Lead | Book CRUD, borrow/return system, availability logic, cache invalidation | -- (shared) |
| **Joseph Wafik** | Data Layer Lead | SQLAlchemy models, Pydantic schemas, validation, DB session | Database 2 + Validation 3 = **5** |
| **Shehab Hossam** | Performance Lead | Redis client, cache-aside pattern, TTL management, cache invalidation | Caching 2 = **2** |
| **Saeed Nadim** | Observability Lead | Logging setup, request middleware, /health & /stats endpoints, monitoring | Logging & Monitoring 3 = **3** |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- SQL Server Express 2022 with ODBC Driver 18
- Docker Desktop (for Redis)

### 1. Database
```sql
CREATE DATABASE library_db;
CREATE DATABASE library_db_test;  -- for pytest
```

### 2. Backend
```bash
cd library-management-system
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env    # edit DATABASE_URL + SECRET_KEY
uvicorn app.main:app --reload    # -> http://localhost:8000
```

### 3. Redis (Docker)
```bash
docker run -d -p 6379:6379 redis:7
```

### 4. Frontend
```bash
cd library-system
npm install
ng serve    # -> http://localhost:4200
```

### 5. Docker (All-in-One)
```bash
cd library-management-system
docker compose up --build -d
# Backend: http://localhost:8001 (Docker maps 8001:8000)
# Redis is included in compose; SQL Server runs locally
```

### Verify
| Check | URL | Expected |
|-------|-----|----------|
| Health | `GET /health` | `{"status": "healthy"}` |
| Swagger | `/docs` | Interactive API explorer |
| Frontend | `http://localhost:4200` | LibreFlow home page |
| Tests | `pytest -x -q` | 11 passed |

---

## API Reference

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | -- | Register new user (role: member) |
| POST | `/auth/login` | -- | Login, returns JWT token |

### Books
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/books` | -- | List all books (cached) |
| GET | `/books/{id}` | -- | Get book by ID (cached) |
| POST | `/books` | Admin | Create book |
| PUT | `/books/{id}` | Admin | Update book |
| DELETE | `/books/{id}` | Admin | Delete book (if no active borrows) |
| POST | `/books/upload-cover` | Admin | Upload cover image |

### Borrow
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/borrow/{book_id}` | Member | Borrow a book |
| POST | `/borrow/return/{book_id}` | Member | Return a book |
| GET | `/borrow/my-history` | Member | Personal borrow history |
| GET | `/borrow/all` | Admin | All borrow records |

### Monitoring
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | -- | DB connectivity check |
| GET | `/stats` | -- | Request metrics & error rate |
| GET | `/stats/recent-errors` | -- | Last 10 error log entries |
| GET | `/admin/dashboard` | Admin | Visual monitoring (frontend) |

---

## Business Rules
- Books cannot be borrowed if `available_copies <= 0`
- A user cannot borrow the same book twice without returning it first
- Maximum **3 active borrows** per user
- Returning a book restores `available_copies`
- Books with active borrows cannot be deleted
- `total_copies` cannot be reduced below the number of currently borrowed copies

---

## Project Structure

```
R&Python/
├── library-management-system/       # FastAPI Backend
│   ├── app/
│   │   ├── cache/                   # Redis client & health
│   │   ├── core/                    # Security, deps, logger, middleware
│   │   ├── database/                # SQLAlchemy engine & session
│   │   ├── models/                  # ORM models (Book, User, BorrowRecord)
│   │   ├── monitoring/              # Request metrics & counters
│   │   ├── routers/                 # API endpoints (auth, books, borrow)
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   └── main.py                  # FastAPI app entry point
│   ├── tests/                       # pytest test suite
│   ├── static/uploads/              # Uploaded cover images (gitignored)
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── requirements.txt
│
├── library-system/                  # Angular Frontend
│   └── src/app/
│       ├── core/                    # Services, guards, interceptors, models
│       ├── features/                # Page components
│       │   ├── admin/               # Book management + Dashboard
│       │   ├── auth/                # Login & Register
│       │   ├── books/               # Book list & cards
│       │   └── borrow/              # Borrow history
│       └── layout/                  # Navbar, auth/main layouts
│
├── .gitignore
├── init-db.sql
└── README.md
```

---

## Testing

```bash
cd library-management-system
pytest -v                    # Full suite
pytest -x -q                 # Fast mode (stop on first failure)
pytest --cov=app --cov-report=term-missing   # With coverage
```

**Test isolation**: Uses `library_db_test` database with per-session create/drop.

### Test Coverage
| File | Tests | What it covers |
|------|-------|----------------|
| `test_auth.py` | 3 | Register, login success, invalid login |
| `test_books.py` | 5 | CRUD, role enforcement, ISBN validation |
| `test_borrow.py` | 3 | Borrow, limit enforcement, return |

---

## Docker Reference

```bash
# Build & start
docker compose up --build -d

# View logs
docker compose logs -f backend

# Run tests inside container
docker compose exec backend pytest -v

# Stop
docker compose down
```

**Important**: SQL Server runs locally (not in Docker). The backend connects via `host.docker.internal:53516`. Ensure your local SQL Server has TCP/IP enabled on port 53516 and both SQL Server + Windows Authentication enabled.

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| SQL Server over SQLite | Required by assignment spec; models real-world enterprise setup |
| Cache-aside over write-through | Simpler to implement; works well for read-heavy library workloads |
| NVARCHAR over VARCHAR | Supports Arabic/Chinese/Unicode book titles and user names |
| `with_for_update()` | Prevents race conditions on concurrent borrow/return requests |
| Standalone Angular components | Modern Angular best practice; avoids NgModule boilerplate |
| Signals over RxJS | Simpler state management; zoneless performance benefits |
| Optimistic UI with revert | Better UX (instant feedback) with fallback on error |

---

## Tools & Technologies

| Tool | Purpose |
|------|---------|
| FastAPI | REST API framework with automatic OpenAPI docs |
| SQLAlchemy | ORM with MS SQL dialect |
| Pydantic | Request/response validation |
| Redis | In-memory caching |
| Angular 19 | SPA frontend with Signals |
| Tailwind CSS | Utility-first styling |
| Docker | Containerization & deployment |
| pytest | API-level integration testing |
| ODBC Driver 18 | SQL Server connectivity from Linux containers |
