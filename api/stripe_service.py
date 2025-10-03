"""
Stripe subscription service for TrendXL 2.0
Handles customer creation, subscription management, and billing
"""
from typing import Dict, Any, Optional
from stripe import StripeClient, StripeError
from config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe client


def get_stripe_client() -> StripeClient:
    """Get configured Stripe client"""
    if not settings.stripe_api_key or settings.stripe_api_key.strip() == "":
        raise ValueError("Stripe API key is not configured")
    return StripeClient(settings.stripe_api_key)


async def create_stripe_customer(email: str, username: str, user_id: str) -> Dict[str, Any]:
    """
    Create a Stripe customer for a new user

    Args:
        email: User's email address
        username: User's username
        user_id: Supabase user ID

    Returns:
        Dict with customer information
    """
    try:
        client = get_stripe_client()

        # Create customer
        customer = client.customers.create(params={
            "email": email,
            "name": username,
            "metadata": {
                "user_id": user_id,
                "username": username
            }
        })

        logger.info(
            f"✅ Stripe customer created: {customer.id} for user {username}")

        return {
            "customer_id": customer.id,
            "email": customer.email,
            "created": customer.created
        }

    except StripeError as e:
        logger.error(f"❌ Stripe customer creation failed: {e}")
        raise ValueError(f"Failed to create Stripe customer: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating Stripe customer: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")


async def create_subscription(customer_id: str, price_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a subscription for a customer

    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID (defaults to configured price)

    Returns:
        Dict with subscription information
    """
    try:
        client = get_stripe_client()

        # Use configured price ID if not provided
        if not price_id:
            price_id = settings.stripe_price_id

        if not price_id or price_id.strip() == "":
            raise ValueError("Stripe price ID is not configured")

        # Create subscription
        subscription = client.subscriptions.create(params={
            "customer": customer_id,
            "items": [{"price": price_id}],
            "payment_behavior": "default_incomplete",
            "payment_settings": {
                "save_default_payment_method": "on_subscription"
            },
            "expand": ["latest_invoice.payment_intent"]
        })

        logger.info(
            f"✅ Subscription created: {subscription.id} for customer {customer_id}")

        # Extract payment intent client secret for frontend
        client_secret = None
        if subscription.latest_invoice and hasattr(subscription.latest_invoice, 'payment_intent'):
            payment_intent = subscription.latest_invoice.payment_intent
            if hasattr(payment_intent, 'client_secret'):
                client_secret = payment_intent.client_secret

        return {
            "subscription_id": subscription.id,
            "customer_id": subscription.customer,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "client_secret": client_secret
        }

    except StripeError as e:
        logger.error(f"❌ Stripe subscription creation failed: {e}")
        raise ValueError(f"Failed to create subscription: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Unexpected error creating subscription: {e}")
        raise ValueError(f"Unexpected error: {str(e)}")


async def get_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Get subscription details

    Args:
        subscription_id: Stripe subscription ID

    Returns:
        Dict with subscription information
    """
    try:
        client = get_stripe_client()

        subscription = client.subscriptions.retrieve(subscription_id)

        return {
            "subscription_id": subscription.id,
            "customer_id": subscription.customer,
            "status": subscription.status,
            "current_period_start": subscription.current_period_start,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": subscription.canceled_at,
            "plan_amount": subscription.items.data[0].price.unit_amount if subscription.items.data else None,
            "plan_currency": subscription.items.data[0].price.currency if subscription.items.data else None,
            "plan_interval": subscription.items.data[0].price.recurring.interval if subscription.items.data and subscription.items.data[0].price.recurring else None
        }

    except StripeError as e:
        logger.error(f"❌ Failed to retrieve subscription: {e}")
        raise ValueError(f"Failed to retrieve subscription: {str(e)}")


async def get_customer_subscriptions(customer_id: str) -> Dict[str, Any]:
    """
    Get all subscriptions for a customer

    Args:
        customer_id: Stripe customer ID

    Returns:
        Dict with list of subscriptions
    """
    try:
        client = get_stripe_client()

        subscriptions = client.subscriptions.list(params={
            "customer": customer_id,
            "limit": 10
        })

        subscription_list = []
        for sub in subscriptions.data:
            subscription_list.append({
                "subscription_id": sub.id,
                "status": sub.status,
                "current_period_start": sub.current_period_start,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "plan_amount": sub.items.data[0].price.unit_amount if sub.items.data else None,
                "plan_currency": sub.items.data[0].price.currency if sub.items.data else None,
                "plan_interval": sub.items.data[0].price.recurring.interval if sub.items.data and sub.items.data[0].price.recurring else None
            })

        return {
            "customer_id": customer_id,
            "subscriptions": subscription_list,
            "total": len(subscription_list)
        }

    except StripeError as e:
        logger.error(f"❌ Failed to retrieve customer subscriptions: {e}")
        raise ValueError(f"Failed to retrieve subscriptions: {str(e)}")


async def cancel_subscription(subscription_id: str, immediate: bool = False) -> Dict[str, Any]:
    """
    Cancel a subscription

    Args:
        subscription_id: Stripe subscription ID
        immediate: If True, cancel immediately. If False, cancel at period end.

    Returns:
        Dict with cancellation confirmation
    """
    try:
        client = get_stripe_client()

        if immediate:
            subscription = client.subscriptions.cancel(subscription_id)
        else:
            subscription = client.subscriptions.update(
                subscription_id,
                params={"cancel_at_period_end": True}
            )

        logger.info(
            f"✅ Subscription {'canceled immediately' if immediate else 'set to cancel at period end'}: {subscription_id}")

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "canceled_at": subscription.canceled_at,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "current_period_end": subscription.current_period_end
        }

    except StripeError as e:
        logger.error(f"❌ Failed to cancel subscription: {e}")
        raise ValueError(f"Failed to cancel subscription: {str(e)}")


async def reactivate_subscription(subscription_id: str) -> Dict[str, Any]:
    """
    Reactivate a subscription that was set to cancel at period end

    Args:
        subscription_id: Stripe subscription ID

    Returns:
        Dict with subscription information
    """
    try:
        client = get_stripe_client()

        subscription = client.subscriptions.update(
            subscription_id,
            params={"cancel_at_period_end": False}
        )

        logger.info(f"✅ Subscription reactivated: {subscription_id}")

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "current_period_end": subscription.current_period_end
        }

    except StripeError as e:
        logger.error(f"❌ Failed to reactivate subscription: {e}")
        raise ValueError(f"Failed to reactivate subscription: {str(e)}")


async def create_checkout_session(customer_id: str, price_id: Optional[str] = None, success_url: str = "", cancel_url: str = "") -> Dict[str, Any]:
    """
    Create a Stripe Checkout session for subscription payment

    Args:
        customer_id: Stripe customer ID
        price_id: Stripe price ID
        success_url: URL to redirect to after successful payment
        cancel_url: URL to redirect to if payment is canceled

    Returns:
        Dict with checkout session information
    """
    try:
        client = get_stripe_client()

        # Use configured price ID if not provided
        if not price_id:
            price_id = settings.stripe_price_id

        if not price_id or price_id.strip() == "":
            raise ValueError("Stripe price ID is not configured")

        # Create checkout session
        session = client.checkout.sessions.create(params={
            "customer": customer_id,
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "payment_method_collection": "if_required"
        })

        logger.info(
            f"✅ Checkout session created: {session.id} for customer {customer_id}")

        return {
            "session_id": session.id,
            "url": session.url,
            "customer_id": customer_id
        }

    except StripeError as e:
        logger.error(f"❌ Failed to create checkout session: {e}")
        raise ValueError(f"Failed to create checkout session: {str(e)}")


async def create_public_payment_link(user_email: str, success_url: str = "", cancel_url: str = "") -> Dict[str, Any]:
    """
    Create a public payment link for anyone to subscribe
    This doesn't require an existing customer - Stripe will create one

    Args:
        user_email: Email for the subscription (optional)
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if payment is canceled

    Returns:
        Dict with payment link URL
    """
    try:
        client = get_stripe_client()

        # Use configured price ID
        price_id = settings.stripe_price_id
        if not price_id or price_id.strip() == "":
            raise ValueError("Stripe price ID is not configured")

        # Create checkout session without customer (Stripe will create customer)
        session_params = {
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "mode": "subscription",
            "success_url": success_url or "https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": cancel_url or "https://yourdomain.com/",
            "allow_promotion_codes": True,
            "billing_address_collection": "auto",
            "customer_email": user_email if user_email else None
        }

        session = client.checkout.sessions.create(params=session_params)

        logger.info(f"✅ Public payment link created: {session.id}")

        return {
            "session_id": session.id,
            "url": session.url,
            "expires_at": session.expires_at
        }

    except StripeError as e:
        logger.error(f"❌ Failed to create public payment link: {e}")
        raise ValueError(f"Failed to create payment link: {str(e)}")
