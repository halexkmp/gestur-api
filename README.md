# Gestur API

Gestur API is a robust backend system for managing business operations, including sales, inventory, human resources, and employee journey tracking. Built with **FastAPI** and following **Vertical Slice Architecture**, it provides a scalable and maintainable foundation for enterprise applications.

## 🚀 Technologies

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **ORM:** [Tortoise-ORM](https://tortoise.github.io/)
- **Migrations:** [Aerich](https://github.com/tortoise/aerich)
- **Database:** PostgreSQL (recommended)
- **Authentication:** JWT (JSON Web Tokens)
- **Deployment:** [Vercel](https://vercel.com/)
- **Testing:** Pytest

## 🏗 Architecture: Vertical Slice

This project follows **Vertical Slice Architecture (VSA)**. Instead of traditional horizontal layers (Controllers, Services, Repositories), features are organized by functionality. Each slice contains everything it needs to fulfill a specific use case:

```text
app/slices/<context>/<feature_name>/
├── ui/              # HTTP concerns, routes, and schemas
├── application/     # Orchestration and business rules
├── infra/           # Persistence (Repositories)
└── domain/          # Pure business logic (optional)
```

Common logic and shared models live in `app/shared/`.

## ✨ Key Features

- **Auth:** JWT-based login and session management.
- **Users:** CRUD for system users with Role-Based Access Control (RBAC).
- **Journey Registry:** Employee shift tracking with time and GPS location (lat/long).
- **Sales:** Order processing, payment methods, and receipt management.
- **Inventory:** Product management and stock change auditing.
- **Partners:** Management of external partners (Buggy men, Businesses).
- **Employees:** HR management, salary summaries, and advances.
- **Reports:** Sales filtering and partner performance analysis.

### User Roles
- `ADMIN`: Full system access.
- `MANAGER`: Operational management.
- `HUMAN_RESOURCES`: Employee and payroll management.
- `OPERATOR`: Sales and inventory operations.
- `EMPLOYEE`: Personal journey registry access.

## 🛠 Project Structure

- `api/`: Vercel serverless entrypoint.
- `app/`: Core application code.
  - `shared/`: Database models, enums, security, and utilities.
  - `slices/`: Feature-based vertical slices.
- `docs/`: Requirement documents, implementation plans, and tasks.
- `migrations/`: Aerich database migration files.
- `tests/`: Unit and integration tests.

## 🚀 Getting Started

### Local Setup

1. **Clone the repository**
2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment:**
   Create a `.env` file based on the settings in `app/config.py`:
   ```env
   DATABASE_URL=postgres://user:pass@localhost:5432/gestur
   SECRET_KEY=your-secret-key
   ENVIRONMENT=development
   ```
5. **Run Migrations:**
   ```bash
    aerich migrate #generate database migration files
   ```
   ```bash
    aerich upgrade #update database
   ```
6. **Start the server:**
   ```bash
   python app/main.py
   ```
   The API will be available at `http://localhost:8000`. Swagger docs are accessible at `/docs` (in development mode).

## ☁️ Deployment

The project is configured for deployment on **Vercel** as a Python Serverless Function.

- Entrypoint: `api/index.py`
- Configuration: `vercel.json`
- Database migrations run automatically on deployment via `migrations/run_migrations.py`.

## 📄 Guidelines

When contributing, please follow the [Vertical Slice Architecture Guide](.junie/guidelines.md) located in the `.junie` directory.
