# SmoothSchedule Backend

Django REST API for the SmoothSchedule multi-tenant scheduling platform.

## Quick Start (Local Development)

### Prerequisites
- Docker and Docker Compose
- Git

### 1. Start Services

```bash
# From project root
docker-compose up --build
```

### 2. Create Database and Run Migrations

```bash
# In another terminal
docker-compose exec django python manage.py migrate
```

### 3. Create Superuser

```bash
docker-compose exec django python manage.py createsuperuser
```

### 4. Access the API

- **API Base:** http://localhost:8000/api/v1/
- **API Documentation:** http://localhost:8000/api/docs/
- **Admin:** http://localhost:8000/admin/
- **API Schema:** http://localhost:8000/api/schema/

---

## Project Structure

```
backend/
├── apps/                      # Django applications
│   ├── core/                 # Multi-tenancy, User, Business models
│   ├── bookings/             # Appointments, Blockers
│   ├── resources/            # Resources, Services
│   ├── customers/            # Customers, PaymentMethods
│   └── payments/             # Stripe integration (Phase 2)
├── config/                    # Django settings
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── local.py         # Development
│   │   └── production.py    # Production
│   ├── urls.py              # URL routing
│   └── celery_app.py        # Celery configuration
├── compose/                   # Docker configuration
├── requirements/              # Python dependencies
└── manage.py
```

---

## API Endpoints

### Authentication
```
POST /api/v1/auth/token/          # Obtain JWT token
POST /api/v1/auth/token/refresh/  # Refresh JWT token
POST /api/v1/auth/token/verify/   # Verify JWT token
```

### Core
```
GET    /api/v1/businesses/        # List businesses
GET    /api/v1/businesses/{id}/   # Business detail
PATCH  /api/v1/businesses/{id}/   # Update business

GET    /api/v1/users/             # List users
POST   /api/v1/users/             # Create user
PATCH  /api/v1/users/{id}/        # Update user
```

### Resources
```
GET    /api/v1/resources/         # List resources
POST   /api/v1/resources/         # Create resource
PATCH  /api/v1/resources/{id}/    # Update resource
DELETE /api/v1/resources/{id}/    # Delete resource

GET    /api/v1/services/          # List services
POST   /api/v1/services/          # Create service
PATCH  /api/v1/services/{id}/     # Update service
```

### Bookings
```
GET    /api/v1/appointments/                # List appointments
  ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD  # Filter by date range
  &resource_ids=uuid1,uuid2                   # Filter by resources

POST   /api/v1/appointments/                # Create appointment
PATCH  /api/v1/appointments/{id}/           # Update appointment
GET    /api/v1/appointments/availability/   # Get available time slots
  ?service_id=uuid&date=YYYY-MM-DD&timezone=America/New_York

GET    /api/v1/blockers/          # List blockers
POST   /api/v1/blockers/          # Create blocker
```

### Customers
```
GET    /api/v1/customers/         # List customers
GET    /api/v1/customers/{id}/    # Customer detail
POST   /api/v1/customers/         # Create customer
PATCH  /api/v1/customers/{id}/    # Update customer

GET    /api/v1/payment-methods/   # List payment methods
POST   /api/v1/payment-methods/   # Create payment method
```

---

## Critical TODO Items

### Phase 1 - MVP (High Priority)

#### 1. Multi-Tenancy Implementation
**Files:** `apps/core/middleware.py`, `apps/core/models.py`

- [ ] Implement thread-local storage for current business
- [ ] Create `TenantManager` to auto-filter queries by business
- [ ] Test cross-tenant isolation (security critical!)
- [ ] Add custom domain support (Phase 2)

**Code Location:**
```python
# apps/core/middleware.py - Line 60
# TODO: Implement thread-local storage

# apps/core/models.py - Line 140
# TODO: Implement TenantManager
```

#### 2. Authentication Backend
**File:** `apps/core/auth.py` (needs to be created)

- [ ] Create `BusinessScopedAuthBackend`
- [ ] Scope login to current business (email unique per business)
- [ ] Test that users cannot login to wrong business

**Implementation needed:**
```python
# Create: apps/core/auth.py
class BusinessScopedAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Get business from request.business (set by middleware)
        # Lookup user by email + business
        # Verify password
        pass
```

#### 3. Permission System
**Files:** All `views.py` files

- [ ] Implement `get_queryset()` filtering by `request.business`
- [ ] Implement `perform_create()` to auto-assign business
- [ ] Add role-based permissions (owner, manager, staff, customer)
- [ ] Test permission boundaries

**Code Locations:**
```python
# apps/core/views.py - Line 28
# apps/resources/views.py - Line 38, 66
# apps/bookings/views.py - Line 38, 101
# apps/customers/views.py - Line 36, 63
# All TODO comments marked with "Override get_queryset()"
```

#### 4. Availability Calculation
**File:** `apps/bookings/views.py`

- [ ] Implement availability calculation logic
- [ ] Consider: business hours, existing appointments, blockers, buffer times
- [ ] Return available time slots as array of strings

**Code Location:**
```python
# apps/bookings/views.py - Line 78
# TODO: Implement availability calculation logic
```

#### 5. Serializer Field Name Transformation
**All serializer files**

- [ ] Install `djangorestframework-camel-case`
- [ ] Configure in `config/settings/base.py`
- [ ] Test that API returns camelCase (matches frontend TypeScript interfaces)

**Code Locations:**
```python
# Add to requirements/base.txt:
# djangorestframework-camel-case==1.4.2

# config/settings/base.py - REST_FRAMEWORK settings
# Add CamelCaseJSONRenderer and CamelCaseJSONParser
```

### Phase 2 - Core Features (Medium Priority)

#### 6. Custom Domain Support
**File:** `apps/core/middleware.py`

- [ ] Uncomment custom domain lookup in `get_business_from_request()`
- [ ] Add `custom_domain` and `custom_domain_verified` fields to Business model
- [ ] Implement DNS verification (Celery task)
- [ ] SSL certificate automation (Let's Encrypt)

**Code Location:**
```python
# apps/core/middleware.py - Line 23
# TODO: Check custom domain first (Phase 2 feature)
```

#### 7. Stripe Connect Integration
**App:** `apps/payments/`

- [ ] Create models: `PaymentSettings`, `Transaction`
- [ ] Implement Stripe Connect OAuth flow
- [ ] Implement webhook handlers
- [ ] Payment Intent creation
- [ ] Refund handling

**Reference:** See `IMPLEMENTATION.md` for Stripe requirements

#### 8. Website Builder
**App:** Create `apps/website/` (if needed)

- [ ] Template management
- [ ] Page editor
- [ ] Content storage (JSONField)

**Reference:** See `api-schema.ts` for `WebsitePage` and `WebsiteTemplate` interfaces

---

## Testing

### Run Tests

```bash
# All tests
docker-compose exec django pytest

# Specific app
docker-compose exec django pytest apps/core/tests/

# With coverage
docker-compose exec django pytest --cov=apps --cov-report=html
```

### Test Coverage Goals

- **Overall:** 80%+
- **Security-critical:** 100%
  - TenantMiddleware
  - Authentication
  - Permission checks
  - Cross-tenant isolation

---

## Database Migrations

### Create Migrations

```bash
docker-compose exec django python manage.py makemigrations
```

### Apply Migrations

```bash
docker-compose exec django python manage.py migrate
```

### Reset Database (Development Only!)

```bash
docker-compose down -v
docker-compose up -d postgres
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser
```

---

## Code Quality

### Format Code

```bash
docker-compose exec django black .
docker-compose exec django isort .
```

### Lint

```bash
docker-compose exec django flake8
```

---

## Environment Variables

See `.env.example` for all available environment variables.

### Critical Settings

- `DJANGO_SECRET_KEY` - Change in production!
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `TENANT_DOMAIN_SUFFIX` - Multi-tenancy (e.g., `.smoothschedule.com`)
- `PLATFORM_SUBDOMAIN` - Platform admin console (e.g., `platform`)

---

## Deployment

### Production Checklist

- [ ] Set `DJANGO_SECRET_KEY` to secure random string
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use managed PostgreSQL and Redis
- [ ] Set up SSL certificates
- [ ] Configure email backend (Mailgun/SendGrid)
- [ ] Set up error tracking (Sentry)
- [ ] Run `collectstatic`
- [ ] Run migrations
- [ ] Create superuser

### Production Deployment

```bash
# Build production image
docker-compose -f docker-compose.production.yml build

# Run services
docker-compose -f docker-compose.production.yml up -d
```

---

## Troubleshooting

### Database connection errors

Check PostgreSQL is running:
```bash
docker-compose ps postgres
```

### Import errors

Rebuild containers:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Permission denied errors

Check file permissions:
```bash
chmod +x backend/compose/local/django/entrypoint
chmod +x backend/compose/local/django/start
```

---

## Related Documentation

- **CLAUDE.md** - AI assistant guide with architecture decisions
- **HANDOFF.md** - Frontend/backend sync protocol
- **IMPLEMENTATION.md** - API requirements from frontend
- **api-schema.ts** - TypeScript interfaces (contract)

---

## Support

For questions about implementation:
1. Check TODO comments in code
2. Review `IMPLEMENTATION.md` for API requirements
3. Check `api-schema.ts` for data structures
4. Review `HANDOFF.md` for sync workflow

---

**Backend Status:** ✅ Structure Complete, 🔨 Implementation In Progress

**Next Priority:** Implement multi-tenancy filtering and permissions (Phase 1 critical)
