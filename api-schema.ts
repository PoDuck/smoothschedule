
// SHARED API CONTRACT
// This file defines the shape of data exchanged between Frontend and Backend.
// Both React (Frontend) and Django (Backend) must adhere to these interfaces.

// --- Enums / Unions ---

export type UserRole = 'superuser' | 'platform_manager' | 'platform_support' | 'owner' | 'manager' | 'staff' | 'resource' | 'customer';
export type ResourceType = 'STAFF' | 'ROOM' | 'EQUIPMENT';
export type AppointmentStatus = 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';
export type TicketStatus = 'Open' | 'In Progress' | 'Resolved';
export type TicketPriority = 'Low' | 'Medium' | 'High' | 'Critical';

// --- Domain Models ---

export interface WebsitePage {
  id: string;
  name: string;
  path: string;
  content?: string;
}

export interface WebsiteTemplate {
  id: string;
  name: string;
  description: string;
  html: string;
  css: string;
  js?: string;
  screenshots: {
    desktop: string;
    mobile: string;
  };
}

export type WebsiteContent = Record<string, string>;

export interface Business {
  id: string;
  name: string;
  subdomain: string;
  primaryColor: string;
  secondaryColor: string;
  logoUrl?: string;
  whitelabelEnabled: boolean;
  plan?: 'Free' | 'Professional' | 'Business' | 'Enterprise';
  status?: 'Active' | 'Suspended' | 'Trial';
  joinedAt?: Date;
  
  // Policies
  resourcesCanReschedule?: boolean;
  requirePaymentMethodToBook: boolean;
  cancellationWindowHours: number;
  lateCancellationFeePercent: number;

  // Website Builder Config
  initialSetupComplete?: boolean;
  activeTemplateId?: string;
  websiteContent?: WebsiteContent;
  websitePages?: Record<string, WebsitePage>;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarUrl?: string;
  businessId?: string; // Tenant ID. Null for Platform Staff.
}

export interface Resource {
  id: string;
  name: string;
  type: ResourceType;
  userId?: string; // Link to User if this resource is a person
}

export interface Service {
  id: string;
  name: string;
  durationMinutes: number;
  price: number;
  description: string;
}

export interface PaymentMethod {
  id: string;
  brand: 'Visa' | 'Mastercard' | 'Amex';
  last4: string;
  isDefault: boolean;
}

export interface Customer {
  id: string;
  userId?: string; // Link to login User
  name: string;
  email: string;
  phone: string;
  city?: string;
  state?: string;
  zip?: string;
  totalSpend: number;
  lastVisit: Date | null;
  status: 'Active' | 'Inactive' | 'Blocked';
  avatarUrl?: string;
  tags?: string[];
  paymentMethods: PaymentMethod[];
}

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
}

export interface Blocker {
  id: string;
  resourceId: string;
  startTime: Date;
  durationMinutes: number;
  title: string;
}

export interface Ticket {
  id: string;
  subject: string;
  businessName: string;
  priority: TicketPriority;
  status: TicketStatus;
  createdAt: Date;
}
