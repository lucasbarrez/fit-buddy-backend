# ⚡ Backend API Template - FastAPI

> **A FastAPI template designed for modern web applications.**
> Featuring BetterAuth session verification, asynchronous PostgreSQL (SQLAlchemy + AsyncPG), and a clean, layered architecture.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📖 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Authentication Strategy](#-authentication-strategy)
- [Development Workflow](#-development-workflow)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)

---

## ✨ Features

- **High Performance**: Built on **FastAPI** and **Uvicorn**, utilizing Python's `asyncio` for non-blocking I/O.
- **Secure Authentication**: Integrated with **BetterAuth** (Next.js) via strict **HMAC session verification** and verified database lookups.
- **Robust Database**: Fully asynchronous **PostgreSQL** access using **SQLAlchemy 2.0** and **AsyncPG** + Supabase.
- **Clean Architecture**: Separation of concerns with **Endpoints**, **Services**, and **Repositories** layers.
- **Type Safety**: strict typing with **Pydantic V2** and **Mypy**.
- **Container Ready**: Optimized **Docker** configurations for both development (hot-reload) and production.
- **🛠️ Developer Experience**:
  - **UV** for lightning-fast package management.
  - **Makefile** for common tasks.
  - **Pre-commit hooks** (Ruff, Black, Mypy) for code quality.
  - **SlowAPI** for rate limiting.

---

## 🏗 Architecture

This project follows a **Layered Architecture** to ensure maintainability and testability.

```mermaid
graph TD
    Client[Client - Next.js] -->|HTTP Request| API[API Endpoint - FastAPI]
    API -->|Validation| Schema[Pydantic Schema]
    API -->|Auth Check| Auth[Security Layer]
    Auth -->|HMAC + DB| DB[(PostgreSQL)]
    API -->|Business Logic| Service[Service Layer]
    Service -->|Data Access| Repo[Repository Layer]
    Repo -->|SQL Query| DB
```

1.  **Endpoints (`app/api`):** Handle HTTP requests, parsing, and response formatting.
2.  **Services (`app/services`):** Contain business logic. They verify rules and orchestrate data operations.
3.  **Repositories (`app/repositories`):** Abstract the database interaction. Services ask repositories for data, not the database directly.
4.  **Security (`app/core/security.py`):** Handles session verification logic (HMAC signing & DB checks).

---

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Language:** Python 3.11+
- **Database:** PostgreSQL (primary), Supabase (optional services)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Driver:** `asyncpg`
- **Dependency Management:** [uv](https://github.com/astral-sh/uv)
- **Linting/Formatting:** Ruff, Black, Mypy, Pre-commit
- **Testing:** Pytest

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **UV** (Recommended) or user standard `pip`
- **PostgreSQL** database (e.g. Docker, Supabase, Neon)

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd oh-my-match-backend

# Run the setup script (installs uv, venv, dependencies)
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment

Copy the example configuration:

```bash
cp .env.example .env
```

**Crucial Variables to Update:**

```ini
# .env

# Your Database Connection (Note: Use postgresql+asyncpg:// scheme)
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/dbname"

# BetterAuth Configuration (Must match your Next.js frontend)
BETTER_AUTH_SECRET="your_shared_secret_key"
BETTER_AUTH_URL="http://localhost:3000"
```

### 3. Run Development Server

```bash
# Using Makefile
make dev

# OR directly with uvicorn
source .venv/bin/activate
uvicorn app.main:app --reload
```

API will be available at: [http://localhost:8000](http://localhost:8000)

---

## 🔐 Authentication Strategy

This API is designed to work as a backend for a **BetterAuth** (Next.js) frontend. It does **not** issue cookies/tokens itself but **verifies** the session tokens sent by the client.

### How Verification Works

1.  **Client Request:** The frontend sends a request with `Authorization: Bearer <session_token>`.
2.  **HMAC Check:** The backend crypto-graphically verifies the token signature using `HMAC-SHA256` and the `BETTER_AUTH_SECRET`.
3.  **Database Lookup:**
    - The backend extracts the session ID from the token.
    - It queries the `session` table in PostgreSQL.
    - It verifies the session exists and has not expired (`expiresAt > NOW()`).
4.  **User Context:** If valid, the backend fetches the `user` details and injects them into `request.state.user`.

**Security Note:** This approach is stateful but highly secure, allowing instant session revocation.

---

## 💻 Development Workflow

The project uses a `Makefile` to simplify common commands:

| Command          | Description                                 |
| :--------------- | :------------------------------------------ |
| `make install`   | Install dependencies and pre-commit hooks   |
| `make dev`       | Start development server with hot-reload    |
| `make test`      | Run tests with Pytest                       |
| `make lint`      | Run Ruff and Mypy checks                    |
| `make format`    | Auto-format code with Black and Ruff        |
| `make docker-up` | Start Postgres (and app) via Docker Compose |

### Pre-commit Hooks

We use pre-commit to ensure code quality before every commit. It runs:

- **Ruff**: Linter & Import sorter
- **Black**: Code formatter
- **Mypy**: Static type checker

To run manually:

```bash
pre-commit run --all-files
```

---

## 📦 Deployment

The application is containerized using Docker, ready for deployment on any cloud provider (AWS, GCP, DigitalOcean, Railway).

### Production Docker Build

```bash
# Build and run in production mode
docker-compose -f docker-compose.prod.yml up -d --build
```

**Key Production Settings:**

- Ensure `DEBUG=False` in `.env`.
- Set `ENVIRONMENT=production`.
- Use a managed PostgreSQL instance for data persistence.

---

## 📄 API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📁 Project Structure

```bash
app/
├── api/             # API Routers & Endpoints
│   ├── dependencies.py  # Auth dependencies (get_current_user)
│   └── v1/
├── core/            # Core config & utilities
│   ├── config.py       # Pydantic Settings
│   ├── db.py           # Database connection (SQLAlchemy)
│   ├── security.py     # Auth verification logic
│   └── logging.py      # Loguru setup
├── middleware/      # Custom middlewares (Rate Limit, CORS)
├── repositories/    # Database interactions
├── schemas/         # Pydantic models (Input/Output)
├── services/        # Business logic
└── main.py          # App entrypoint
```
