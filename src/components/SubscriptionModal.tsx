import React from 'react';
import { Box, VStack, Button, Text, HStack, Icon } from '@chakra-ui/react';
import { Crown, Clock, X } from 'lucide-react';
import { createPublicPaymentLink } from '@/services/subscriptionService';
import { calculateResetTime } from '@/utils/timeUtils';
import { useAuth } from '@/contexts/AuthContext';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SubscriptionModal: React.FC<SubscriptionModalProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const [loading, setLoading] = React.useState(false);
  const resetTime = calculateResetTime();

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const response = await createPublicPaymentLink(
        user?.email,
        `${window.location.origin}/subscription/success`,
        `${window.location.origin}/`
      );
      
      // Redirect to Stripe Checkout
      window.location.href = response.payment_url;
    } catch (error) {
      console.error('Failed to create payment link:', error);
      alert('Failed to create payment link. Please try again.');
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Box
      position="fixed"
      top="0"
      left="0"
      right="0"
      bottom="0"
      bg="rgba(0, 0, 0, 0.7)"
      backdropFilter="blur(10px)"
      zIndex={1000}
      display="flex"
      alignItems="center"
      justifyContent="center"
      onClick={onClose}
      className="animate-fade-in"
    >
      <Box
        bg="white"
        borderRadius="2xl"
        maxW="md"
        w="full"
        mx={4}
        onClick={(e) => e.stopPropagation()}
        position="relative"
        p={8}
        boxShadow="2xl"
        className="animate-slide-up"
      >
        {/* Close Button */}
        <Button
          position="absolute"
          top={4}
          right={4}
          onClick={onClose}
          variant="ghost"
          p={2}
          minW="auto"
          h="auto"
          color="gray.400"
          _hover={{ color: 'gray.600' }}
        >
          <X className="w-5 h-5" />
        </Button>

        {/* Content */}
        <VStack spacing={6} align="stretch">
          {/* Icon */}
          <Box className="flex justify-center">
            <Box className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center">
              <Icon as={Crown} color="white" boxSize={8} />
            </Box>
          </Box>

          {/* Title */}
          <VStack spacing={2}>
            <Text fontSize="2xl" fontWeight="bold" textAlign="center" className="font-orbitron">
              Daily Limit Reached 🎯
            </Text>
            <Text fontSize="md" color="gray.600" textAlign="center" className="font-inter">
              You've used your free analysis today. Subscribe for unlimited access!
            </Text>
          </VStack>

          {/* Benefits */}
          <Box bg="purple.50" borderRadius="xl" p={4}>
            <VStack align="start" spacing={2}>
              <HStack>
                <Text fontSize="lg">✨</Text>
                <Text fontSize="sm" className="font-inter">Unlimited trend analyses</Text>
              </HStack>
              <HStack>
                <Text fontSize="lg">🚀</Text>
                <Text fontSize="sm" className="font-inter">Priority support</Text>
              </HStack>
              <HStack>
                <Text fontSize="lg">📊</Text>
                <Text fontSize="sm" className="font-inter">Advanced insights & analytics</Text>
              </HStack>
              <HStack>
                <Text fontSize="lg">💾</Text>
                <Text fontSize="sm" className="font-inter">Save unlimited analyses</Text>
              </HStack>
            </VStack>
          </Box>

          {/* CTA Button */}
          <Button
            onClick={handleSubscribe}
            size="lg"
            bg="black"
            color="white"
            _hover={{ bg: 'gray.800' }}
            disabled={loading}
            className="font-orbitron font-bold"
            h="56px"
          >
            {loading ? 'Loading...' : 'Get Subscription for $49/month'}
          </Button>

          {/* Reset Time */}
          <HStack justify="center" spacing={2} color="gray.500">
            <Icon as={Clock} boxSize={4} />
            <Text fontSize="sm" className="font-inter">
              Free limit resets in <strong>{resetTime}</strong>
            </Text>
          </HStack>

          {/* Maybe Later */}
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            color="gray.500"
            _hover={{ color: 'gray.700' }}
            className="font-inter"
          >
            Maybe later
          </Button>
        </VStack>
      </Box>
    </Box>
  );
};

export default SubscriptionModal;

