# HANDOFF.md - Cross-Repository Sync Protocol

## Overview

SmoothSchedule uses a **two-repository architecture** where:
- **Frontend** (`SmoothScheduleReact`) is managed via **Google AI Studio**
- **Backend** (`smoothschedule`) is managed via **Claude Code**

The `api-schema.ts` file serves as the **API contract** between these two repositories and must be kept synchronized.

---

## The Contract: `api-schema.ts`

### Source of Truth
The `api-schema.ts` file in the **frontend repository** is the **source of truth**. The backend maintains a copy for reference.

### Location
- **Frontend (Source):** `SmoothScheduleReact/api-schema.ts`
- **Backend (Copy):** `smoothschedule/api-schema.ts`

### What It Defines
- TypeScript interfaces for all domain models (User, Business, Appointment, etc.)
- Enums and type unions (UserRole, AppointmentStatus, etc.)
- Request/response structures
- All data shapes exchanged via the API

---

## Synchronization Scenarios

### Scenario A: Frontend-Driven Change (Forward Sync)

**When:** You need a new field in the UI or modify data structures in React components

**Tools:** Google AI Studio → Claude Code

**Process:**

1. **In Google AI Studio (Frontend):**
   - Update `SmoothScheduleReact/api-schema.ts` with new/modified interfaces
   - Update `SmoothScheduleReact/mockData.ts` with test data
   - Implement the UI feature using the new data structure
   - Test the feature with mock data

2. **Handoff Prompt for Claude Code:**
   ```
   I have updated the frontend API contract in api-schema.ts. Here are the changes:

   [Paste the relevant interface/changes from api-schema.ts]

   Please:
   1. Update the backend copy of api-schema.ts
   2. Create/update the corresponding Django Models
   3. Create/update the DRF Serializers to match this contract
   4. Implement/update the ViewSet endpoints if needed
   5. Generate migrations
   ```

3. **In Claude Code (Backend):**
   - Review the changes to understand the new contract
   - Update `smoothschedule/api-schema.ts`
   - Create/modify Django models to match
   - Create/modify DRF serializers (must exactly match the TypeScript interface)
   - Update ViewSets/views as needed
   - Generate and run migrations
   - Test endpoints to verify they return data in the correct shape

4. **Verification:**
   - Backend serializer output should exactly match TypeScript interface
   - Test with real API calls from frontend (or Postman/curl)

---

### Scenario B: Backend-Driven Change (Backward Sync)

**When:** The backend needs to change the data structure (new field, renamed field, etc.)

**Tools:** Claude Code → Google AI Studio

**Process:**

1. **In Claude Code (Backend):**
   - Modify Django models as needed
   - Update DRF serializers
   - Update `smoothschedule/api-schema.ts` to reflect changes
   - Generate and run migrations
   - Test endpoints

2. **Handoff Prompt for Google AI Studio:**
   ```
   The backend API contract has changed. Here is the updated structure:

   [Paste the modified interfaces from api-schema.ts]

   OR

   [Paste the Django Serializer output example]

   Please:
   1. Update SmoothScheduleReact/api-schema.ts to match
   2. Update mockData.ts with compatible test data
   3. Refactor any React components that use the old structure
   4. Test the UI with the new data shape
   ```

3. **In Google AI Studio (Frontend):**
   - Update `api-schema.ts` to match backend changes
   - Update `mockData.ts` with new fields/structure
   - Fix TypeScript errors in components
   - Update UI components to use new fields
   - Test with mock data

4. **Verification:**
   - No TypeScript errors
   - UI displays new fields correctly
   - Mock data matches production API shape

---

## Common Handoff Examples

### Example 1: Adding a New Field

**Frontend Change:**
```typescript
// api-schema.ts - Frontend adds new field
export interface Appointment {
  id: string;
  resourceId: string | null;
  customerId: string;
  customerName: string;
  serviceId: string;
  startTime: Date;
  durationMinutes: number;
  status: AppointmentStatus;
  notes?: string;
  customerNotes?: string;  // 👈 NEW FIELD
}
```

**Handoff to Backend:**
> "I added a `customerNotes` field to the Appointment interface for customer-provided notes. Please update the backend model and serializer to include this optional text field."

**Backend Implementation:**
```python
# models.py
class Appointment(TenantModel):
    # ... existing fields ...
    notes = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)  # 👈 NEW

# serializers.py
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'resource_id', 'customer_id', 'customer_name',
                  'service_id', 'start_time', 'duration_minutes',
                  'status', 'notes', 'customer_notes']  # 👈 ADDED
```

---

### Example 2: Adding a New Enum Value

**Frontend Change:**
```typescript
// api-schema.ts
export type AppointmentStatus = 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW' | 'IN_PROGRESS';  // 👈 ADDED IN_PROGRESS
```

**Handoff to Backend:**
> "I added an 'IN_PROGRESS' status to AppointmentStatus for appointments that are currently happening. Please update the backend model choices."

**Backend Implementation:**
```python
# models.py
class Appointment(TenantModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),  # 👈 NEW
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
```

---

### Example 3: New Model/Resource

**Frontend Change:**
```typescript
// api-schema.ts
export interface ServiceCategory {
  id: string;
  name: string;
  description: string;
  colorHex: string;
  sortOrder: number;
}

export interface Service {
  id: string;
  name: string;
  durationMinutes: number;
  price: number;
  description: string;
  categoryId?: string;  // 👈 NEW RELATIONSHIP
}
```

**Handoff to Backend:**
> "I added a new ServiceCategory model and linked Services to categories via categoryId. Please create the Django models, serializers, and CRUD endpoints for ServiceCategory. Also add the foreign key relationship to Service."

---

## Best Practices

### DO ✅
- Always update `api-schema.ts` first before changing serializers/components
- Include example data when describing changes
- Test both mock data (frontend) and real API (backend) after sync
- Keep interface names consistent between TypeScript and Django models
- Use descriptive commit messages referencing the contract change
- Update mockData.ts whenever api-schema.ts changes
- Document why the change was needed

### DON'T ❌
- Don't modify serializers without updating api-schema.ts
- Don't add fields to React components before they exist in the contract
- Don't rename fields without coordinating both sides
- Don't change field types without careful consideration
- Don't skip testing after a handoff
- Don't make breaking changes without communication

---

## Verification Checklist

After any contract change, verify:

**Frontend:**
- [ ] `api-schema.ts` updated with new/changed interfaces
- [ ] `mockData.ts` includes test data for all new fields
- [ ] TypeScript compiler has no errors
- [ ] UI components render correctly with mock data
- [ ] No console errors when running app

**Backend:**
- [ ] `api-schema.ts` copy matches frontend version
- [ ] Django models match the interface structure
- [ ] DRF serializers return JSON matching TypeScript interface exactly
- [ ] Migrations generated and applied successfully
- [ ] API endpoints tested (Postman/curl/pytest)
- [ ] No SQL errors or validation issues

---

## Emergency: Out of Sync

If the frontend and backend fall out of sync:

1. **Identify the source of truth:** Usually the frontend `api-schema.ts`
2. **Document the differences:** Compare both versions
3. **Choose a direction:** Forward sync (frontend → backend) or backward sync (backend → frontend)
4. **Make a plan:** List all files that need updating
5. **Execute carefully:** Update one repository at a time
6. **Test thoroughly:** Verify the integration works end-to-end

---

## Questions?

- **Which repository owns the contract?** Frontend (SmoothScheduleReact)
- **Can I make changes to both simultaneously?** No - choose one direction and follow the handoff
- **What if I need to rename a field?** Update frontend first, handoff to backend with both old/new names in description
- **Do I need to sync every time?** Only when `api-schema.ts` changes
- **What about internal-only backend fields?** Those don't go in the contract - keep them backend-only

---

**Last Updated:** 2025-11-23
**Version:** 1.0.0
