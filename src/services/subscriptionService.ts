/**
 * Subscription Service
 * Handles all subscription-related API calls
 */

import { supabase } from '@/lib/supabase';

// Get API URL from window or environment
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined' && window.location) {
    // In production, use the same origin
    if (window.location.hostname !== 'localhost') {
      return window.location.origin;
    }
  }
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export interface SubscriptionInfo {
  has_subscription: boolean;
  subscription: {
    subscription_id: string;
    customer_id: string;
    status: string;
    current_period_start: number;
    current_period_end: number;
    cancel_at_period_end: boolean;
    canceled_at: number | null;
    plan_amount: number;
    plan_currency: string;
    plan_interval: string;
  } | null;
}

export interface SubscriptionStatus {
  has_active_subscription: boolean;
  subscription_status: string | null;
  subscription_end_date: string | null;
}

export interface PaymentLinkResponse {
  success: boolean;
  payment_url: string;
  session_id: string;
  expires_at: number;
}

/**
 * Get authentication token from Supabase
 */
async function getAuthToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
}

/**
 * Get current user's subscription information
 */
export async function getSubscriptionInfo(): Promise<SubscriptionInfo> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/subscription/info`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get subscription info');
  }

  return response.json();
}

/**
 * Check if user has an active subscription
 */
export async function checkSubscriptionStatus(): Promise<SubscriptionStatus> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/subscription/check`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to check subscription status');
  }

  return response.json();
}

/**
 * Create a public payment link for subscription
 * This doesn't require authentication
 */
export async function createPublicPaymentLink(
  email?: string,
  successUrl?: string,
  cancelUrl?: string
): Promise<PaymentLinkResponse> {
  const params = new URLSearchParams();
  if (email) params.append('user_email', email);
  if (successUrl) params.append('success_url', successUrl);
  if (cancelUrl) params.append('cancel_url', cancelUrl);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/subscription/create-payment-link?${params.toString()}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create payment link');
  }

  return response.json();
}

/**
 * Create a checkout session for an authenticated user
 */
export async function createCheckoutSession(
  successUrl: string,
  cancelUrl: string
): Promise<{ checkout_url: string; session_id: string }> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const params = new URLSearchParams({
    success_url: successUrl,
    cancel_url: cancelUrl,
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/subscription/checkout?${params.toString()}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create checkout session');
  }

  return response.json();
}

/**
 * Cancel user's subscription
 */
export async function cancelSubscription(immediate: boolean = false): Promise<any> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(
    `${API_BASE_URL}/api/v1/subscription/cancel?immediate=${immediate}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to cancel subscription');
  }

  return response.json();
}

/**
 * Reactivate a canceled subscription
 */
export async function reactivateSubscription(): Promise<any> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/subscription/reactivate`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to reactivate subscription');
  }

  return response.json();
}

/**
 * Format subscription price for display
 */
export function formatPrice(amount: number, currency: string): string {
  // Amount is in cents, convert to dollars/euros etc
  const value = amount / 100;
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(value);
}

/**
 * Format subscription interval for display
 */
export function formatInterval(interval: string): string {
  const intervals: Record<string, string> = {
    day: 'daily',
    week: 'weekly',
    month: 'monthly',
    year: 'yearly',
  };
  
  return intervals[interval] || interval;
}

/**
 * Get subscription status badge color
 */
export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'green',
    trialing: 'blue',
    past_due: 'yellow',
    canceled: 'gray',
    incomplete: 'orange',
    incomplete_expired: 'red',
    unpaid: 'red',
  };
  
  return colors[status] || 'gray';
}

/**
 * Get subscription status display text
 */
export function getStatusText(status: string): string {
  const texts: Record<string, string> = {
    active: 'Active',
    trialing: 'Trial',
    past_due: 'Past Due',
    canceled: 'Canceled',
    incomplete: 'Incomplete',
    incomplete_expired: 'Expired',
    unpaid: 'Unpaid',
  };
  
  return texts[status] || status;
}
