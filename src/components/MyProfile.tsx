import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  Heading,
  Badge,
  Spinner,
  Separator,
} from '@chakra-ui/react';
import { toaster } from './ui/toaster';
import { CreditCard, CheckCircle, XCircle, Calendar, DollarSign } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import {
  getSubscriptionInfo,
  createCheckoutSession,
  cancelSubscription,
  reactivateSubscription,
  formatSubscriptionPrice,
  formatPeriodDate,
  getStatusColor,
  getStatusText,
} from '../services/subscriptionService';
import type { SubscriptionInfo } from '../types';

const MyProfile: React.FC = () => {
  const { user, token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Handle success/cancel query params from Stripe redirect
  useEffect(() => {
    const session = searchParams.get('session');
    if (session === 'success') {
      toaster.create({
        title: 'Payment Successful!',
        description: 'Your subscription has been activated. Reloading subscription info...',
        type: 'success',
        duration: 5000,
      });
      // Clear the query param
      searchParams.delete('session');
      setSearchParams(searchParams);
      // Reload subscription info
      loadSubscriptionInfo();
    } else if (session === 'canceled') {
      toaster.create({
        title: 'Payment Canceled',
        description: 'Your payment was canceled. You can try again anytime.',
        type: 'info',
        duration: 5000,
      });
      // Clear the query param
      searchParams.delete('session');
      setSearchParams(searchParams);
    }
  }, [searchParams, setSearchParams]);

  // Load subscription info on mount
  useEffect(() => {
    if (token) {
      loadSubscriptionInfo();
    }
  }, [token]);

  const loadSubscriptionInfo = async () => {
    try {
      setIsLoading(true);
      const info = await getSubscriptionInfo();
      setSubscriptionInfo(info);
    } catch (error: any) {
      console.error('Failed to load subscription info:', error);
      console.error('Error loading subscription info:', error.response?.data?.detail || 'Failed to load subscription information');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubscribe = async () => {
    try {
      setIsProcessing(true);
      
      const currentUrl = window.location.origin;
      const successUrl = `${currentUrl}/profile?session=success`;
      const cancelUrl = `${currentUrl}/profile?session=canceled`;
      
      const session = await createCheckoutSession(successUrl, cancelUrl);
      
      // Redirect to Stripe Checkout
      window.location.href = session.checkout_url;
    } catch (error: any) {
      console.error('Failed to create checkout session:', error);
      toaster.create({
        title: 'Error',
        description: error.message || 'Failed to start checkout process',
        type: 'error',
        duration: 5000,
      });
      setIsProcessing(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will still have access until the end of your billing period.')) {
      return;
    }

    try {
      setIsProcessing(true);
      await cancelSubscription(false);
      
      toaster.create({
        title: 'Subscription Canceled',
        description: 'Your subscription will remain active until the end of your billing period.',
        type: 'info',
        duration: 5000,
      });
      
      // Reload subscription info
      await loadSubscriptionInfo();
    } catch (error: any) {
      console.error('Failed to cancel subscription:', error);
      toaster.create({
        title: 'Error',
        description: error.message || 'Failed to cancel subscription',
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReactivateSubscription = async () => {
    try {
      setIsProcessing(true);
      await reactivateSubscription();
      
      toaster.create({
        title: 'Subscription Reactivated',
        description: 'Your subscription has been successfully reactivated.',
        type: 'success',
        duration: 5000,
      });
      
      // Reload subscription info
      await loadSubscriptionInfo();
    } catch (error: any) {
      console.error('Failed to reactivate subscription:', error);
      toaster.create({
        title: 'Error',
        description: error.message || 'Failed to reactivate subscription',
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsProcessing(false);
    }
  };

  if (!user) {
    return (
      <Container maxW="container.lg" py={8}>
        <Box 
          bg="orange.50" 
          borderLeft="4px solid"
          borderColor="orange.500"
          p={4}
          borderRadius="md"
        >
          <Heading size="sm" mb={2}>Not logged in</Heading>
          <Text fontSize="sm">Please log in to view your profile.</Text>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxW="container.lg" py={8}>
      <VStack gap={6} align="stretch">
        {/* User Info Card */}
        <Card.Root>
          <Card.Header>
            <Heading size="md">Profile Information</Heading>
          </Card.Header>
          <Card.Body>
            <VStack gap={4} align="stretch">
              <HStack>
                <Text fontWeight="bold" minW="120px" color="white">Name:</Text>
                <Text color="white">{user.full_name || user.username}</Text>
              </HStack>
              <HStack>
                <Text fontWeight="bold" minW="120px" color="white">Email:</Text>
                <Text color="white">{user.email}</Text>
              </HStack>
              <HStack>
                <Text fontWeight="bold" minW="120px" color="white">Username:</Text>
                <Text color="white">@{user.username}</Text>
              </HStack>
              {user.bio && (
                <HStack align="start">
                  <Text fontWeight="bold" minW="120px" color="white">Bio:</Text>
                  <Text color="white">{user.bio}</Text>
                </HStack>
              )}
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Subscription Card */}
        <Card.Root>
          <Card.Header>
            <HStack justify="space-between">
              <HStack>
                <CreditCard className="w-5 h-5" />
                <Heading size="md">Subscription</Heading>
              </HStack>
            </HStack>
          </Card.Header>
          <Card.Body>
            {isLoading ? (
              <Box textAlign="center" py={8}>
                <Spinner size="lg" />
                <Text mt={4} color="white">Loading subscription information...</Text>
              </Box>
            ) : subscriptionInfo?.has_subscription && subscriptionInfo.subscription ? (
              <VStack gap={6} align="stretch">
                {/* Subscription Status */}
                <HStack justify="space-between">
                  <Text fontWeight="bold" color="white">Status:</Text>
                  <Badge colorPalette={getStatusColor(subscriptionInfo.subscription.status)} fontSize="md" px={3} py={1}>
                    {getStatusText(subscriptionInfo.subscription.status)}
                  </Badge>
                </HStack>

                <Separator />

                {/* Subscription Details */}
                <VStack gap={3} align="stretch">
                  <HStack justify="space-between">
                    <HStack>
                      <DollarSign className="w-4 h-4 text-white" />
                      <Text fontWeight="bold" color="white">Price:</Text>
                    </HStack>
                    <Text color="white">
                      {formatSubscriptionPrice(
                        subscriptionInfo.subscription.plan_amount ?? 0,
                        subscriptionInfo.subscription.plan_currency ?? 'usd'
                      )}
                      /{subscriptionInfo.subscription.plan_interval ?? 'month'}
                    </Text>
                  </HStack>

                  <HStack justify="space-between">
                    <HStack>
                      <Calendar className="w-4 h-4 text-white" />
                      <Text fontWeight="bold" color="white">Current Period:</Text>
                    </HStack>
                    <Text fontSize="sm" color="white">
                      {formatPeriodDate(subscriptionInfo.subscription.current_period_start)} -{' '}
                      {formatPeriodDate(subscriptionInfo.subscription.current_period_end)}
                    </Text>
                  </HStack>

                  {subscriptionInfo.subscription.cancel_at_period_end && (
                    <Box 
                      bg="orange.50" 
                      borderLeft="4px solid"
                      borderColor="orange.500"
                      p={4}
                      borderRadius="md"
                    >
                      <Heading size="sm" mb={2} color="orange.800">Subscription Ending</Heading>
                      <Text fontSize="sm" color="orange.700">
                        Your subscription will end on{' '}
                        {formatPeriodDate(subscriptionInfo.subscription.current_period_end)}
                      </Text>
                    </Box>
                  )}
                </VStack>

                <Separator />

                {/* Action Buttons */}
                <HStack gap={3}>
                  {subscriptionInfo.subscription.cancel_at_period_end ? (
                    <Button
                      colorPalette="green"
                      onClick={handleReactivateSubscription}
                      loading={isProcessing}
                      flex="1"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Reactivate Subscription
                    </Button>
                  ) : (
                    <Button
                      colorPalette="red"
                      variant="outline"
                      onClick={handleCancelSubscription}
                      loading={isProcessing}
                      flex="1"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Cancel Subscription
                    </Button>
                  )}
                </HStack>
              </VStack>
            ) : (
              <VStack gap={6} align="stretch">
                <Box 
                  bg="blue.50" 
                  borderLeft="4px solid"
                  borderColor="blue.500"
                  p={4}
                  borderRadius="md"
                >
                  <Heading size="sm" mb={2} color="blue.800">No Active Subscription</Heading>
                  <Text fontSize="sm" color="blue.700">
                    Subscribe to TrendXL Pro for $49/month to unlock unlimited trend analysis.
                  </Text>
                </Box>

                <Box bg="gray.800" p={6} borderRadius="lg">
                  <VStack gap={4} align="start">
                    <Heading size="sm" color="white">TrendXL Pro - $49/month</Heading>
                    <VStack gap={2} align="start">
                      <HStack>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <Text fontSize="sm" color="white">Unlimited trend analysis</Text>
                      </HStack>
                      <HStack>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <Text fontSize="sm" color="white">Advanced AI insights</Text>
                      </HStack>
                      <HStack>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <Text fontSize="sm" color="white">Creative Center integration</Text>
                      </HStack>
                      <HStack>
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <Text fontSize="sm" color="white">Priority support</Text>
                      </HStack>
                    </VStack>
                  </VStack>
                </Box>

                <Button
                  colorPalette="blue"
                  size="lg"
                  onClick={handleSubscribe}
                  loading={isProcessing}
                >
                  <CreditCard className="w-5 h-5 mr-2" />
                  Subscribe Now - $49/month
                </Button>
              </VStack>
            )}
          </Card.Body>
        </Card.Root>
      </VStack>
    </Container>
  );
};

export default MyProfile;

