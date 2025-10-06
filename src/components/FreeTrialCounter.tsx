import React, { useEffect, useState } from 'react';
import { Box, HStack, Text, Badge, Icon } from '@chakra-ui/react';
import { Clock, Sparkles, CheckCircle } from 'lucide-react';
import { getFreeTrialInfo, type FreeTrialInfo } from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';

interface FreeTrialCounterProps {
  refreshTrigger?: number;
}

export const FreeTrialCounter: React.FC<FreeTrialCounterProps> = ({ refreshTrigger }) => {
  const { user } = useAuth();
  const [trialInfo, setTrialInfo] = useState<FreeTrialInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadTrialInfo();
    } else {
      setLoading(false);
    }
  }, [user]);

  // Auto-refresh when refreshTrigger changes
  useEffect(() => {
    if (user && refreshTrigger) {
      loadTrialInfo();
    }
  }, [refreshTrigger, user]);

  const loadTrialInfo = async () => {
    try {
      setLoading(true);
      const info = await getFreeTrialInfo();
      setTrialInfo(info);
    } catch (error) {
      console.error('Failed to load trial info:', error);
    } finally {
      setLoading(false);
    }
  };

  const getResetTime = () => {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    const diff = tomorrow.getTime() - now.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

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
            colorPalette={canUseToday ? "purple" : "orange"} 
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
                Resets in <strong>{getResetTime()}</strong>
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

