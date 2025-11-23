# SmoothSchedule Backend

Django REST API for the SmoothSchedule multi-tenant SaaS scheduling platform.

## Overview

This repository contains the **Django backend** for SmoothSchedule. The React frontend is maintained separately in the [`SmoothScheduleReact`](https://github.com/PoDuck/SmoothScheduleReact) repository.

### Key Features
- 🏢 **Multi-tenant architecture** with subdomain-based tenant resolution
- 🔐 **JWT authentication** with role-based permissions
- 📅 **Appointment scheduling** with resource management
- 💳 **Payment processing** integration
- 👥 **Customer management** with booking history
- 🎨 **White-labeling** support for tenant customization
- 📊 **Analytics and reporting**

---

## Technology Stack

- **Framework:** Django 5.x
- **API:** Django REST Framework (DRF)
- **Database:** PostgreSQL (production), SQLite (development)
- **Authentication:** djangorestframework-simplejwt
- **Language:** Python 3.11+

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- PostgreSQL (for production) or SQLite (for development)
- pip and virtualenv

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PoDuck/smoothschedule.git
   cd smoothschedule
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

5. **Run migrations:**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load sample data (optional):**
   ```bash
   python manage.py loaddata sample_data
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/api/v1/`

---

## Project Structure

```
smoothschedule/
├── backend/
│   ├── config/              # Django settings and configuration
│   ├── apps/
│   │   ├── core/           # Multi-tenancy, authentication, base models
│   │   ├── bookings/       # Appointments, availability, blockers
│   │   ├── resources/      # Resources (staff, rooms, equipment)
│   │   ├── customers/      # Customer management
│   │   ├── payments/       # Payment processing
│   │   └── website/        # Website builder for tenants
│   ├── manage.py
│   └── requirements.txt
├── api-schema.ts            # API contract (synced from frontend)
├── IMPLEMENTATION.md        # API implementation guide
├── HANDOFF.md              # Cross-repo sync protocol
├── CLAUDE.md               # AI assistant guide
└── README.md               # This file
```

---

## API Contract

The API follows a **contract-first approach** using `api-schema.ts` as the source of truth.

### Key Principles:
1. **Frontend defines the contract** - TypeScript interfaces in `SmoothScheduleReact/api-schema.ts`
2. **Backend implements the contract** - Django models and DRF serializers match exactly
3. **Changes are synchronized** - See `HANDOFF.md` for the sync protocol

### Example Contract → Implementation:

**TypeScript Contract:**
```typescript
export interface Appointment {
  id: string;
  resourceId: string | null;
  customerId: string;
  startTime: Date;
  durationMinutes: number;
  status: AppointmentStatus;
}
```

**Django Model:**
```python
class Appointment(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    resource = models.ForeignKey('Resource', null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
```

**DRF Serializer:**
```python
class AppointmentSerializer(serializers.ModelSerializer):
    resource_id = serializers.UUIDField(source='resource.id', allow_null=True)
    customer_id = serializers.UUIDField(source='customer.id')

    class Meta:
        model = Appointment
        fields = ['id', 'resource_id', 'customer_id', 'start_time',
                  'duration_minutes', 'status']
```

---

## Development Workflow

### Two-Repository Setup

- **Frontend Development:** Use Google AI Studio with `SmoothScheduleReact` repo
- **Backend Development:** Use Claude Code with this repo
- **Synchronization:** Follow the protocol in `HANDOFF.md`

### Making API Changes

1. **Read `HANDOFF.md`** to understand the sync process
2. **Check `api-schema.ts`** for the current contract
3. **Update models/serializers** to match the contract
4. **Generate migrations** if models changed
5. **Test endpoints** to verify correct data shape
6. **Update `api-schema.ts` copy** if backend-driven change

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.bookings

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

---

## Multi-Tenancy

### How It Works

SmoothSchedule uses **subdomain-based multi-tenancy**:

- `platform.smoothschedule.com` → Platform admin console
- `acme.smoothschedule.com` → Acme Corp's tenant portal
- `salon.smoothschedule.com` → Salon XYZ's tenant portal

### Tenant Isolation

All queries are automatically filtered by tenant:

```python
# Middleware resolves tenant from subdomain
# All queries automatically scoped to request.tenant

appointments = Appointment.objects.all()  # Only returns current tenant's data
```

### Important Rules:
- ✅ **Always use tenant-aware models** (inherit from `TenantModel`)
- ✅ **Validate tenant isolation** in tests
- ❌ **Never bypass tenant filtering** for cross-tenant queries
- ❌ **Never expose tenant IDs** to other tenants

---

## Authentication & Permissions

### JWT Authentication

```bash
# Login
POST /api/v1/auth/login/
{
  "email": "user@example.com",
  "password": "password123",
  "subdomain": "acme"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}

# Use token in requests
GET /api/v1/appointments/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### User Roles

- **superuser** - Full platform access
- **platform_manager** - Platform administration
- **platform_support** - Customer support
- **owner** - Tenant owner (full tenant access)
- **manager** - Tenant manager
- **staff** - Tenant staff member
- **resource** - Bookable resource (can view their schedule)
- **customer** - End customer (booking appointments)

---

## Key API Endpoints

See `IMPLEMENTATION.md` for complete endpoint documentation.

### Booking
- `GET /api/v1/booking/availability/` - Get available time slots
- `POST /api/v1/booking/appointments/` - Create appointment

### Scheduler
- `GET /api/v1/appointments/` - List appointments
- `PATCH /api/v1/appointments/{id}/` - Update appointment (drag & drop)

### Resources
- `GET /api/v1/resources/` - List resources
- `POST /api/v1/resources/` - Create resource

### Customers
- `GET /api/v1/customers/` - List customers
- `GET /api/v1/customers/{id}/` - Customer detail

### Platform Admin
- `GET /api/v1/platform/businesses/` - List all tenants
- `POST /api/v1/platform/masquerade/` - Masquerade as user

---

## Contributing

1. Read `CLAUDE.md` for development guidelines
2. Create a feature branch from `main`
3. Make your changes following the coding conventions
4. Write tests for new features
5. Run tests and linting
6. Commit with conventional commit messages
7. Push and create a pull request

---

## Documentation

- **CLAUDE.md** - Comprehensive AI assistant guide
- **HANDOFF.md** - Cross-repository synchronization protocol
- **IMPLEMENTATION.md** - API endpoint specifications
- **api-schema.ts** - TypeScript API contract

---

## License

TBD

---

## Support

For questions or issues:
- Check the documentation files
- Review `HANDOFF.md` for sync issues
- Open an issue on GitHub

---

**Related Repositories:**
- [SmoothScheduleReact](https://github.com/PoDuck/SmoothScheduleReact) - React frontend (Google AI Studio)
