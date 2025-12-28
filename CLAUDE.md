# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gezamko Shop is a Django-based e-commerce backend for selling shoes. It uses Django REST Framework for APIs, Keycloak for authentication (production), PostgreSQL for the database, and integrates with Paymob for payments and Posta for shipping.

## Common Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
pre-commit install

# Run server (port 8090)
python manage.py runserver 8090

# Database
python manage.py migrate
python manage.py seed_database  # Seed with sample data
python manage.py seed_database --no-images  # Skip image downloads
python manage.py seed_database --clear  # Clear existing data first

# Testing
pytest  # Run all tests
pytest tests/test_products.py  # Run specific test file
pytest -k "test_name"  # Run tests matching name
pytest --cov=. --cov-report=html  # Run with coverage

# Code formatting (auto-runs on commit via pre-commit)
pre-commit run --all-files
black .
isort .

# Security scanning
bandit -r . -x ./venv,./tests,./.git
```

## Architecture

### Django Apps
- **gezamko/** - Main project config (settings, urls, celery)
- **users/** - Custom User model with roles (admin/staff/customer), Keycloak authentication
- **products/** - Product catalog with images
- **orders/** - Order management with items
- **payments/** - Paymob integration for card/wallet/cash payments
- **shipments/** - Posta shipping integration with tracking
- **complaints/** - Customer complaint system with responses

### Authentication
- **Development**: Session/Basic auth (Django default)
- **Production**: Keycloak Bearer tokens via `users/authentication.py:KeycloakAuthentication`
- Auth mode switches automatically based on `DEBUG` setting in `gezamko/settings.py:179-182`

### Permissions System
Custom permission classes in `users/permissions.py`:
- `IsAdminUser`, `IsStaffUser`, `IsCustomer` - Role-based permissions
- `IsOwnerOrStaff`, `IsOwnerOrAdmin` - Object-level ownership checks
- `ProductPermission` - Public read, staff write
- `OrderPermission`, `ComplaintPermission` - Owner or staff access

### User Roles
The `User` model (`users/models.py`) has three roles:
- `admin` - Full access, auto-sets `is_staff` and `is_superuser`
- `staff` - Product management, order processing, auto-sets `is_staff`
- `customer` - Default role, can create orders and complaints

### API Structure
Base URL: `/api/v1/`
- `/api/v1/users/` - User profile management
- `/api/v1/products/` - Product CRUD (public read)
- `/api/v1/orders/` - Order management
- `/api/v1/payments/` - Payment initiation and webhooks
- `/api/v1/shipments/` - Shipment tracking
- `/api/v1/complaints/` - Complaint handling
- `/api/docs/` - Swagger UI
- `/api/redoc/` - ReDoc

### External Services
- **Paymob**: Payment processing via `payments/services.py`
- **Posta**: Shipping via `shipments/services.py`
- **Keycloak**: OAuth2/OIDC authentication (production)
- **Celery/Redis**: Background tasks

### Test Structure
Tests in `tests/` directory use pytest with fixtures from `tests/conftest.py`:
- `api_client` - Unauthenticated client
- `user`, `admin_user` - Test users
- `authenticated_client`, `admin_client` - Pre-authenticated clients

### Database
- Development: SQLite (`USE_SQLITE=True` in env)
- Production: PostgreSQL
- Configured in `gezamko/settings.py:88-107`

## CI/CD Pipeline

GitHub Actions (`.github/workflows/ci.yml`) runs:
1. Tests with coverage (pytest)
2. Bandit security scan
3. SonarQube analysis
4. Linting (flake8, black, isort)
5. Docker build (main branch only)

## Docker

```bash
docker-compose up  # Starts: db, redis, keycloak, web, celery, celery-beat
```

Services run on:
- Web: 8090
- Keycloak: 8080
- PostgreSQL: 5432
- Redis: 6379

## Frontend

The Next.js frontend is located at `../gezamko-shop-frontend/`.

```bash
cd ../gezamko-shop-frontend
npm install
npm run dev  # Runs on port 3005
```

Frontend connects to backend at `http://localhost:8090/api/v1`
