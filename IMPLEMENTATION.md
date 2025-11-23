# Smooth Schedule - API Implementation Guide

This document outlines the API requirements to connect the Smooth Schedule React frontend with a Django (DRF) backend.

## 1. Architecture

### Multi-Tenancy
*   **Resolution:** Backend middleware must resolve the tenant from the `Host` header or `X-Tenant-Subdomain`.
*   **Isolation:** `Appointment.objects.filter(tenant=request.tenant)` must be the default behavior.

### Authentication
*   **JWT:** Use `SimpleJWT` or similar.
*   **Endpoints:**
    *   `POST /api/v1/auth/login/` (Accepts `subdomain` context)
    *   `POST /api/v1/auth/masquerade/` (Superuser/Owner only)

## 2. Data Contract
The frontend strictly adheres to the interfaces defined in `src/api-schema.ts`. The Django Serializers **must** match these shapes.

## 3. Critical Endpoints

### Booking Flow
*   `GET /api/v1/booking/availability/`
    *   **Input:** `service_id`, `date`, `timezone`
    *   **Output:** `string[]` (e.g., `["09:00", "09:30"]`)
    *   **Logic:** Calculated server-side considering Resources, Blockers, and Business Hours.

### Scheduler
*   `GET /api/v1/appointments/`
    *   **Filters:** `start_date`, `end_date`, `resource_ids`
*   `PATCH /api/v1/appointments/{id}/`
    *   Used for Drag-and-Drop resizing.

### Tenant Config
*   `GET /api/v1/tenant/config/`
    *   **Public Endpoint**. Returns branding (colors, logo) and public settings based on the subdomain.

## 4. Handoff Protocol
When implementing the backend:
1.  Read `src/api-schema.ts`.
2.  Create Django Models to match.
3.  Create DRF Serializers to match.
4.  Implement ViewSets for the endpoints above.
