# Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup pre-commit hooks
pre-commit install

# Run migrations
python manage.py migrate

# Run server
python manage.py runserver
```

# Committing

Pre-commit hooks auto-format code before each commit:

```bash
git add .
git commit -m "your message"
```

To format all files manually:

```bash
pre-commit run --all-files
```

---

this project as an ecommerce backend for selling products online.
these products are shoes. and can be something else in the future.

the project is build using latest django framework.

the project uses

- django rest framework for building apis
- keycloak for authentication and authorization
- postgresql as database
- docker for containerization
- docker-compose for orchestration
- pytest for testing
- paymob for payment gateway integration
- posta for shipping integration
- logging

the app will use github actions for ci/cd, currently it won't be deployed but the continuos integration will run the tests on every push to the repositories main branch.

the ci flow will run

- tests
- sonarqube scan
- bandit scan.

# ERD

- products

  - id
  - name
  - description
  - price
  - stock
  - created_at
  - updated_at

  * images
    - id
    - product_id
    - image_url
    - created_at
    - updated_at

- orders
  - id
  - user_id
  - total_amount
  - status
  - created_at
  - updated_at
  * order_items
    - id
    - order_id
    - product_id
    - quantity
    - price
    - created_at
    - updated_at
- users
  - id
  - username
  - email
  - password
  - first_name
  - last_name
  - other keycloak integration fields
  - created_at
  - updated_at
- payments

  - id
  - order_id
  - payment_method
  - amount
  - status
  - created_at
  - updated_at

- shipments

  - id
  - order_id
  - shipping_address
  - shipping_method
  - tracking_number
  - status
  - created_at
  - updated_at

- complaints
  - id
  - order_id
  - user_id
  - subject
  - description
  - status
  - created_at
  - updated_at

# Users

we have 3 types of users for the app the admin of the company, the
staff, and the customer each can login to the app but each has different
permissions

# Database Seeding

Populate the database with sample users, products (with real images), and orders:

```bash
# Full seed
python manage.py seed_database

# Without downloading images (faster)
python manage.py seed_database --no-images

# Clear existing data first
python manage.py seed_database --clear

# Seed only products or users
python manage.py seed_database --products-only
python manage.py seed_database --users-only
```

**Default credentials:**

- Admin: `admin@gezamko.com` / `admin123!@#`
- Staff: `staff1@gezamko.com` / `staff123!@#`
- Customer: `ahmed@example.com` / `customer123!@#`
