import { useEffect, useState } from 'react';
import { Box, Text, Button, HStack, VStack, Icon } from '@chakra-ui/react';
import { AlertCircle, CreditCard, Check } from 'lucide-react';
import {
  checkSubscriptionStatus,
  createPublicPaymentLink,
  type SubscriptionStatus,
} from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';

export function SubscriptionBanner() {
  const { user } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingPayment, setCreatingPayment] = useState(false);

  useEffect(() => {
    if (user) {
      loadSubscriptionStatus();
    }
  }, [user]);

  const loadSubscriptionStatus = async () => {
    try {
      setLoading(true);
      const status = await checkSubscriptionStatus();
      setSubscriptionStatus(status);
    } catch (error) {
      console.error('Failed to load subscription status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    try {
      setCreatingPayment(true);
      
      const successUrl = `${window.location.origin}/subscription/success`;
      const cancelUrl = window.location.origin;

      const paymentLink = await createPublicPaymentLink(
        user?.email,
        successUrl,
        cancelUrl
      );

      // Redirect to Stripe Checkout
      window.location.href = paymentLink.payment_url;
    } catch (error) {
      console.error('Failed to create payment link:', error);
      alert('Failed to create payment link. Please try again.');
    } finally {
      setCreatingPayment(false);
    }
  };

  // Don't show banner if user is not authenticated
  if (!user) {
    return null;
  }

  // Don't show banner while loading
  if (loading) {
    return null;
  }

  // Don't show banner if user has active subscription
  if (subscriptionStatus?.has_active_subscription) {
    return (
      <Box
        bg="green.50"
        border="2px"
        borderColor="green.400"
        borderRadius="lg"
        p={4}
        mb={4}
      >
        <HStack gap={3}>
          <Icon as={Check} color="green.500" boxSize={5} />
          <VStack align="start" gap={1}>
            <Text fontWeight="bold" color="green.700">
              Active Subscription
            </Text>
            <Text fontSize="sm" color="green.600">
              You have full access to all TrendXL features. Thank you for being a subscriber!
            </Text>
          </VStack>
        </HStack>
      </Box>
    );
  }

  // Show subscription required banner
  return (
    <Box
      bg="blue.50"
      border="2px"
      borderColor="blue.400"
      borderRadius="lg"
      p={4}
      mb={4}
    >
      <HStack gap={4} justify="space-between" align="center">
        <HStack gap={3} flex={1}>
          <Icon as={AlertCircle} color="blue.500" boxSize={5} />
          <VStack align="start" gap={1}>
            <Text fontWeight="bold" color="blue.700">
              Subscription Required
            </Text>
            <Text fontSize="sm" color="blue.600">
              Subscribe to TrendXL Pro to access unlimited trend analysis and AI insights.
              Only $29/month.
            </Text>
          </VStack>
        </HStack>
        <Button
          onClick={handleSubscribe}
          loading={creatingPayment}
          colorScheme="blue"
        >
          <HStack gap={2}>
            <Icon as={CreditCard} />
            <span>Subscribe Now</span>
          </HStack>
        </Button>
      </HStack>
    </Box>
  );
}

