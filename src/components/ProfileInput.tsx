import React, { useState } from 'react';
import { Search, Sparkles, AlertCircle, Zap, Star } from 'lucide-react';
import { Box, Button, Input, VStack, HStack, Text } from '@chakra-ui/react';
import ApiStatusBanner from './ApiStatusBanner';
import { ProfileInputProps } from '../types';
import { isValidTikTokInput } from '../utils';

const ProfileInput: React.FC<ProfileInputProps> = ({ 
  onSubmit, 
  isLoading, 
  canUseTrial = true, // Default to true for backward compatibility
  onSubscribeClick 
}) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  
  // Determine if input should be disabled
  const isDisabled = isLoading || canUseTrial === false;
  
  // Log the state for debugging
  console.log('🎨 ProfileInput render:', {
    canUseTrial,
    isDisabled,
    isLoading,
    hasInput: !!input
  });

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
    <Box className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-white relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Subtle pattern - скрываем на мобильных для производительности */}
        <div className="hidden sm:block absolute top-20 left-10 w-24 h-24 sm:w-32 sm:h-32 rounded-full bg-gray-200 opacity-30"></div>
        <div className="hidden md:block absolute bottom-40 right-20 w-20 h-20 md:w-24 md:h-24 rounded-full bg-gray-200 opacity-25"></div>
        <div className="hidden lg:block absolute top-1/2 right-10 w-16 h-16 rounded-full bg-gray-200 opacity-20"></div>
      </div>

      <div className="flex items-center justify-center min-h-screen relative z-10">
        <VStack spacing={8} md:spacing={12} maxW="4xl" w="full" px={4} sm:px={6} md:px={8}>
          {/* API Status Banner */}
          <ApiStatusBanner />
          
          {/* Hero Section */}
          <VStack spacing={8} textAlign="center">
            {/* Logo and Icons - адаптивные размеры */}
            <div className="relative animate-float">
              <Box className="inline-flex items-center justify-center w-20 h-20 sm:w-24 sm:h-24 bg-white rounded-xl sm:rounded-2xl shadow-xl border-2 border-gray-200 relative overflow-hidden hover:shadow-2xl transition-all duration-300">
                <div className="absolute inset-0 bg-gradient-to-br from-transparent to-gray-50 opacity-50"></div>
                <img
                  src="/photo.svg"
                  alt="Trendzl Logo"
                  className="w-10 h-10 sm:w-12 sm:h-12 relative z-10"
                />
              </Box>

              {/* Floating icons with enhanced animations - скрываем на самых маленьких экранах */}
              <div className="hidden xs:flex absolute -top-2 -right-2 w-7 h-7 sm:w-8 sm:h-8 bg-black rounded-full items-center justify-center animate-bounce-subtle shadow-lg">
                <Star className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" fill="currentColor" />
              </div>
              <div className="hidden xs:flex absolute -bottom-1 -left-3 w-5 h-5 sm:w-6 sm:h-6 bg-gray-600 rounded-full items-center justify-center animate-pulse shadow-md">
                <Zap className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" fill="currentColor" />
              </div>
            </div>
            
            {/* Main Heading - адаптивные размеры текста */}
            <div className="space-y-4 sm:space-y-6">
              <div>
                <Text fontSize={{ base: "4xl", sm: "5xl", md: "6xl" }} fontWeight="900" className="font-orbitron text-black leading-none tracking-tight">
                  Trendzl
                </Text>
                <Text fontSize={{ base: "md", sm: "lg", md: "xl" }} fontWeight="bold" className="font-orbitron text-gray-600 -mt-1 sm:-mt-2">
                  AI Trend Hunter
                </Text>
              </div>
              
              {/* Subtitle with enhanced styling - адаптивные размеры */}
              <div className="max-w-3xl mx-auto">
                <Text fontSize={{ base: "xl", sm: "2xl" }} className="font-inter text-black font-semibold mb-2 sm:mb-3">
                  Discover What's Trending
                </Text>
                <Text fontSize={{ base: "sm", sm: "md", md: "lg" }} className="font-inter leading-relaxed text-gray-700">
                  Analyze TikTok profiles and uncover the hottest trends with AI-powered insights. 
                  Get data-driven recommendations for your content strategy.
                </Text>
              </div>
              
              {/* Feature badges - адаптивные отступы и размеры */}
              <HStack spacing={{ base: 2, sm: 3, md: 4 }} justify="center" flexWrap="wrap">
                <Box className="bg-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-full border border-gray-200 shadow-md hover:shadow-lg transition-shadow">
                  <Text fontSize={{ base: "xs", sm: "sm" }} className="font-medium text-gray-700">AI-Powered</Text>
                </Box>
                <Box className="bg-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-full border border-gray-200 shadow-md hover:shadow-lg transition-shadow">
                  <Text fontSize={{ base: "xs", sm: "sm" }} className="font-medium text-gray-700">Real-time Data</Text>
                </Box>
                <Box className="bg-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-full border border-gray-200 shadow-md hover:shadow-lg transition-shadow">
                  <Text fontSize={{ base: "xs", sm: "sm" }} className="font-medium text-gray-700">Trend Analysis</Text>
                </Box>
              </HStack>
            </div>
          </VStack>

          {/* Enhanced Input Form - адаптивные размеры */}
          <Box w="full" maxW="2xl">
            <form onSubmit={handleSubmit}>
              <VStack spacing={{ base: 4, sm: 5, md: 6 }}>
                {/* Input Section with better styling - адаптивные отступы */}
                <Box w="full" className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-200 p-1.5 sm:p-2">
                  <Box position="relative" w="full">
                    <Box position="absolute" left={{ base: 4, sm: 6 }} top="50%" transform="translateY(-50%)" zIndex={2}>
                      <Search className="h-5 w-5 sm:h-6 sm:w-6 text-gray-500" />
                    </Box>
                    <Input
                      value={input}
                      onChange={handleInputChange}
                      placeholder={isDisabled && canUseTrial === false ? "🔒 Subscribe to continue analyzing profiles" : "Enter TikTok profile link or @username"}
                      pl={{ base: 12, sm: 14, md: 16 }}
                      pr={{ base: 4, sm: 6 }}
                      py={{ base: 5, sm: 6, md: 7 }}
                      fontSize={{ base: "md", sm: "lg" }}
                      bg={isDisabled && canUseTrial === false ? "gray.100" : "transparent"}
                      border="none"
                      color={isDisabled && canUseTrial === false ? "gray.400" : "black"}
                      _placeholder={{ 
                        color: isDisabled && canUseTrial === false ? "red.600" : "gray.500", 
                        fontSize: { base: "sm", sm: "md" },
                        fontWeight: isDisabled && canUseTrial === false ? "bold" : "normal"
                      }}
                      _hover={{ bg: isDisabled && canUseTrial === false ? "gray.100" : "transparent" }}
                      _focus={{ 
                        outline: "none",
                        bg: isDisabled && canUseTrial === false ? "gray.100" : "transparent"
                      }}
                      borderRadius={{ base: "lg", sm: "xl" }}
                      disabled={isDisabled}
                      className="font-jetbrains"
                      cursor={isDisabled && canUseTrial === false ? "not-allowed" : "text"}
                    />
                  </Box>
                </Box>
                
                {/* Error Message */}
                {error && (
                  <HStack color="red.500" fontSize="sm" className="animate-fade-in bg-red-50 p-3 rounded-lg">
                    <AlertCircle className="w-4 h-4" />
                    <Text fontWeight="medium">{error}</Text>
                  </HStack>
                )}

                {/* Enhanced Submit Button - адаптивные размеры */}
                {canUseTrial === false && onSubscribeClick ? (
                  // Show "Subscribe" button when free trial exhausted
                  <Button
                    onClick={(e) => {
                      e.preventDefault();
                      console.log('🔴 Subscribe button clicked - opening modal');
                      onSubscribeClick();
                    }}
                    w="full"
                    size={{ base: "md", sm: "lg" }}
                    bg="gradient-to-r from-red-500 to-orange-500"
                    color="white"
                    _hover={{ 
                      bg: "gradient-to-r from-red-600 to-orange-600",
                      transform: "translateY(-2px)",
                      shadow: "xl"
                    }}
                    _active={{
                      transform: "translateY(0px)"
                    }}
                    className="font-orbitron font-bold text-base sm:text-lg transition-all duration-200 animate-pulse"
                    borderRadius={{ base: "lg", sm: "xl" }}
                    py={{ base: 6, sm: 7, md: 8 }}
                    shadow="xl"
                  >
                    <HStack spacing={{ base: 2, sm: 3 }}>
                      <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
                      <Text fontSize={{ base: "sm", sm: "md" }}>🚀 Subscribe for Unlimited Access</Text>
                    </HStack>
                  </Button>
                ) : (
                  // Show normal "Discover Trends" button
                  <Button
                    type="submit"
                    disabled={isDisabled || !input.trim()}
                    w="full"
                    size={{ base: "md", sm: "lg" }}
                    bg="black"
                    color="white"
                    _hover={{ 
                      bg: "gray.800",
                      transform: "translateY(-2px)",
                      shadow: "xl"
                    }}
                    _active={{
                      transform: "translateY(0px)"
                    }}
                    _disabled={{ 
                      opacity: 0.5, 
                      cursor: "not-allowed",
                      bg: "gray.400"
                    }}
                    className={`font-orbitron font-bold text-base sm:text-lg transition-all duration-200 ${isLoading ? 'animate-pulse' : ''}`}
                    borderRadius={{ base: "lg", sm: "xl" }}
                    py={{ base: 6, sm: 7, md: 8 }}
                    shadow="lg"
                  >
                    {isLoading ? (
                      <HStack spacing={{ base: 2, sm: 3 }}>
                        <Box className="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <Text fontSize={{ base: "sm", sm: "md" }}>Analyzing...</Text>
                      </HStack>
                    ) : (
                      <HStack spacing={{ base: 2, sm: 3 }}>
                        <img
                          src="/photo.svg"
                          alt="Logo"
                          className="w-4 h-4 sm:w-5 sm:h-5"
                        />
                        <Text fontSize={{ base: "sm", sm: "md" }}>Discover Trends</Text>
                      </HStack>
                    )}
                  </Button>
                )}
                
                {/* Help text - адаптивный размер */}
                <Text fontSize={{ base: "xs", sm: "sm" }} color="gray.600" textAlign="center" className="font-inter">
                  Enter a TikTok username like "@zachking" or paste a profile link
                </Text>
              </VStack>
            </form>
          </Box>
        </VStack>
      </div>
    </Box>
  );
};

export default ProfileInput;
