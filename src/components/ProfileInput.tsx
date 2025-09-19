import React, { useState } from 'react';
import { Search, Sparkles, AlertCircle } from 'lucide-react';
import { Box, Button, Input, VStack, HStack, Text } from '@chakra-ui/react';
import ApiStatusBanner from './ApiStatusBanner';
import GradientText from './GradientText';
import { ProfileInputProps } from '../types';
import { isValidTikTokInput } from '../utils';

const ProfileInput: React.FC<ProfileInputProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValidTikTokInput(input)) {
      setError('Please enter a valid TikTok profile link or username');
      return;
    }
    
    setError('');
    onSubmit(input);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <Box className="min-h-screen flex items-center justify-center">
      <VStack spacing={8} maxW="2xl" w="full" px={4}>
        {/* API Status Banner */}
        <ApiStatusBanner />
        
        {/* Header */}
        <VStack spacing={6} textAlign="center">
          <Box className="inline-flex items-center justify-center w-20 h-20 bg-primary-card rounded-full">
            <Sparkles className="w-10 h-10 text-primary-accent" />
          </Box>
          
          <Box>
            <Text fontSize="5xl" fontWeight="bold" className="font-orbitron mb-4">
              <GradientText
                colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                animationSpeed={3}
                showBorder={false}
              >
                TrendXL 2.0
              </GradientText>
            </Text>
            <Text fontSize="xl" color="text.secondary" maxW="2xl" className="font-inter">
              Analyze TikTok profiles and discover the hottest trends with AI-powered insights
            </Text>
          </Box>
        </VStack>

        {/* Input Form */}
        <Box w="full" maxW="xl">
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <Box position="relative" w="full">
                <Box position="absolute" left={4} top="50%" transform="translateY(-50%)" zIndex={2}>
                  <Search className="h-5 w-5 text-text-secondary" />
                </Box>
                <Input
                  value={input}
                  onChange={handleInputChange}
                  placeholder="Enter TikTok profile link or @username"
                  pl={12}
                  py={6}
                  fontSize="md"
                  bg="primary.card"
                  border="1px"
                  borderColor={error ? "red.500" : "primary.line"}
                  color="text.primary"
                  _placeholder={{ color: "text.secondary" }}
                  _hover={{ borderColor: "primary.accent/30" }}
                  _focus={{ 
                    outline: "none", 
                    ring: 2, 
                    ringColor: "primary.accent", 
                    borderColor: "transparent" 
                  }}
                  borderRadius="card"
                  isDisabled={isLoading}
                  className="font-jetbrains"
                />
              </Box>
              
              {/* Error Message */}
              {error && (
                <HStack color="red.400" fontSize="sm" className="animate-fade-in">
                  <AlertCircle className="w-4 h-4" />
                  <Text>{error}</Text>
                </HStack>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                isDisabled={isLoading || !input.trim()}
                w="full"
                size="lg"
                bg="primary.accent"
                color="white"
                _hover={{ bg: "primary.accent-hover" }}
                _disabled={{ opacity: 0.5, cursor: "not-allowed" }}
                className={`font-orbitron ${isLoading ? 'animate-pulse' : ''}`}
                borderRadius="btn"
                py={6}
              >
                {isLoading ? (
                  <HStack>
                    <Box className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <Text>Analyzing profile...</Text>
                  </HStack>
                ) : (
                  <HStack>
                    <Sparkles className="w-5 h-5" />
                    <Text>Discover Trends</Text>
                  </HStack>
                )}
              </Button>
            </VStack>
          </form>
        </Box>
      </VStack>
    </Box>
  );
};

export default ProfileInput;
