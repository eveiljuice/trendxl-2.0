import React, { useEffect, useState, useCallback } from 'react';
import { Box, HStack, Text, Badge, Icon } from '@chakra-ui/react';
import { Clock, Sparkles, CheckCircle } from 'lucide-react';
import { getFreeTrialInfo, type FreeTrialInfo } from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';
import { useAutoRefresh, calculateTimeUntilReset, formatTimeRemaining } from '@/hooks/useAutoRefresh';

interface FreeTrialCounterProps {
  refreshTrigger?: number;
}

export const FreeTrialCounter: React.FC<FreeTrialCounterProps> = ({ refreshTrigger }) => {
  const { user } = useAuth();
  const [trialInfo, setTrialInfo] = useState<FreeTrialInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [resetTime, setResetTime] = useState('');

  // Memoize loadTrialInfo to prevent unnecessary re-renders
  const loadTrialInfo = useCallback(async () => {
    try {
      setLoading(true);
      const info = await getFreeTrialInfo();
      setTrialInfo(info);
    } catch (error) {
      console.error('Failed to load trial info:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Update reset time every second
  const updateResetTime = useCallback(() => {
    const { hours, minutes } = calculateTimeUntilReset();
    setResetTime(formatTimeRemaining(hours, minutes));
  }, []);

  // Initial load
  useEffect(() => {
    if (user) {
      loadTrialInfo();
      updateResetTime();
    } else {
      setLoading(false);
    }
  }, [user, loadTrialInfo, updateResetTime]);

  // Auto-refresh when refreshTrigger changes
  useEffect(() => {
    if (user && refreshTrigger) {
      loadTrialInfo();
    }
  }, [refreshTrigger, user, loadTrialInfo]);

  // Auto-refresh trial info every 60 seconds (when user is authenticated)
  useAutoRefresh(loadTrialInfo, 60000, !!user);

  // Update reset time every 60 seconds
  useAutoRefresh(updateResetTime, 60000, !!user && !trialInfo?.has_subscription);

  // Don't show if user is not authenticated
  if (!user) {
    return null;
  }

  // Don't show while loading
  if (loading) {
    return null;
  }

  // Don't show if user has active subscription
  if (trialInfo?.has_subscription) {
    return (
      <Box
        bg="green.50"
        border="1px solid"
        borderColor="green.200"
        borderRadius="lg"
        p={3}
        mb={4}
        className="animate-fade-in"
      >
        <HStack gap={3} justify="center">
          <Icon as={CheckCircle} color="green.600" boxSize={5} />
          <Text fontSize="sm" color="green.700" fontWeight="medium" className="font-inter">
            ✨ Premium Active - Unlimited Scans
          </Text>
        </HStack>
      </Box>
    );
  }

  // Show free trial counter
  const canUseToday = trialInfo?.can_use_free_trial ?? false;
  const usedToday = trialInfo?.today_count ?? 0;
  const dailyLimit = trialInfo?.daily_limit ?? 1;
  const remaining = canUseToday ? 1 : 0;

  return (
    <Box
      bg={canUseToday ? "purple.50" : "orange.50"}
      border="1px solid"
      borderColor={canUseToday ? "purple.200" : "orange.200"}
      borderRadius="lg"
      p={3}
      mb={4}
      className="animate-fade-in"
    >
      <HStack gap={4} justify="center" flexWrap="wrap">
        {/* Free Scans Counter */}
        <HStack gap={2}>
          <Icon 
            as={Sparkles} 
            color={canUseToday ? "purple.600" : "orange.600"} 
            boxSize={5} 
          />
          <Text 
            fontSize="sm" 
            color={canUseToday ? "purple.700" : "orange.700"} 
            fontWeight="medium"
            className="font-inter"
          >
            Free Scans Today:
          </Text>
          <Badge 
            colorScheme={canUseToday ? "purple" : "orange"} 
            variant="solid"
            fontSize="sm"
            px={2}
            py={1}
          >
            {remaining}/{dailyLimit}
          </Badge>
        </HStack>

        {/* Reset Timer */}
        {!canUseToday && (
          <>
            <Box h="20px" w="1px" bg="orange.300" />
            <HStack gap={2}>
              <Icon as={Clock} color="orange.600" boxSize={4} />
              <Text fontSize="sm" color="orange.700" className="font-inter">
                Resets in <strong>{resetTime}</strong>
              </Text>
            </HStack>
          </>
        )}
      </HStack>

      {/* Total Usage Stats (optional) */}
      {trialInfo && trialInfo.total_free_analyses > 0 && (
        <Text 
          fontSize="xs" 
          color={canUseToday ? "purple.600" : "orange.600"}
          textAlign="center"
          mt={2}
          className="font-inter"
        >
          Total free scans used: {trialInfo.total_free_analyses}
        </Text>
      )}
    </Box>
  );
};

