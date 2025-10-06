import { useEffect, useState } from 'react';
import { Box, Text, Button, HStack, VStack, Icon, Badge } from '@chakra-ui/react';
import { AlertCircle, CreditCard, Check, Gift } from 'lucide-react';
import {
  checkSubscriptionStatus,
  createPublicPaymentLink,
  getFreeTrialInfo,
  type SubscriptionStatus,
  type FreeTrialInfo,
} from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';

interface SubscriptionBannerProps {
  refreshTrigger?: number;
}

export function SubscriptionBanner({ refreshTrigger }: SubscriptionBannerProps = {}) {
  const { user } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [freeTrialInfo, setFreeTrialInfo] = useState<FreeTrialInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingPayment, setCreatingPayment] = useState(false);

  useEffect(() => {
    if (user) {
      loadSubscriptionStatus();
      loadFreeTrialInfo();
    }
  }, [user]);

  // Auto-refresh when refreshTrigger changes (after successful analysis)
  useEffect(() => {
    if (user && refreshTrigger) {
      console.log('🔄 SubscriptionBanner: Refreshing free trial info after analysis');
      loadFreeTrialInfo();
    }
  }, [refreshTrigger, user]);

  const loadSubscriptionStatus = async () => {
    try {
      setLoading(true);
      const status = await checkSubscriptionStatus();
      setSubscriptionStatus(status);
    } catch (error) {
      console.error('Failed to load subscription status:', error);
      // Set fallback status to show banner even if API fails
      setSubscriptionStatus({
        has_active_subscription: false,
        subscription_status: 'none',
        subscription_end_date: null,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadFreeTrialInfo = async () => {
    try {
      const info = await getFreeTrialInfo();
      setFreeTrialInfo(info);
    } catch (error) {
      console.error('Failed to load free trial info:', error);
      // Set fallback info to show banner even if API fails
      setFreeTrialInfo({
        can_use_free_trial: true,
        today_count: 0,
        daily_limit: 1,
        total_free_analyses: 0,
        has_subscription: false,
        message: 'You get 1 free profile analysis per day!',
      });
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

  // Show free trial or subscription required banner
  const canUseTrial = freeTrialInfo?.can_use_free_trial ?? false;
  const isTrialAvailable = !freeTrialInfo?.has_subscription && (freeTrialInfo?.today_count === 0 || canUseTrial);
  
  return (
    <Box
      bg={isTrialAvailable ? "purple.50" : "blue.50"}
      border="2px"
      borderColor={isTrialAvailable ? "purple.400" : "blue.400"}
      borderRadius="lg"
      p={4}
      mb={4}
    >
      <VStack align="stretch" gap={3}>
        <HStack gap={4} justify="space-between" align="start">
          <HStack gap={3} flex={1}>
            <Icon 
              as={isTrialAvailable ? Gift : AlertCircle} 
              color={isTrialAvailable ? "purple.500" : "blue.500"} 
              boxSize={5} 
            />
            <VStack align="start" gap={1}>
              <HStack gap={2}>
                <Text fontWeight="bold" color={isTrialAvailable ? "purple.700" : "blue.700"}>
                  {isTrialAvailable ? "🎁 Free Trial Available!" : "Subscription Required"}
                </Text>
                {freeTrialInfo && (
                  <Badge colorScheme={canUseTrial ? "purple" : "orange"} variant="solid">
                    {canUseTrial ? "1 Free Scan Today" : `${freeTrialInfo.today_count}/${freeTrialInfo.daily_limit} Used Today`}
                  </Badge>
                )}
              </HStack>
              <Text fontSize="sm" color={isTrialAvailable ? "purple.600" : "blue.600"}>
                {isTrialAvailable 
                  ? "You get 1 free profile analysis per day! Try it now or subscribe for unlimited access."
                  : freeTrialInfo?.message || "Subscribe to TrendXL Pro to access unlimited trend analysis and AI insights. Only $49/month."}
              </Text>
              {freeTrialInfo && freeTrialInfo.total_free_analyses > 0 && (
                <Text fontSize="xs" color={isTrialAvailable ? "purple.500" : "blue.500"}>
                  📊 Total free analyses used: {freeTrialInfo.total_free_analyses}
                </Text>
              )}
            </VStack>
          </HStack>
          <Button
            onClick={handleSubscribe}
            loading={creatingPayment}
            colorScheme={isTrialAvailable ? "purple" : "blue"}
            size="sm"
          >
            <HStack gap={2}>
              <Icon as={CreditCard} />
              <span>Subscribe Now</span>
            </HStack>
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
}

