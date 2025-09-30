import React, { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  HStack,
} from '@chakra-ui/react';
import { Mail, Lock, User, UserPlus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, register } = useAuth();
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');

  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // Register form state
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');
  const [registerLoading, setRegisterLoading] = useState(false);

  // Error states
  const [loginError, setLoginError] = useState('');
  const [registerError, setRegisterError] = useState('');

  const showToast = (title: string, description: string, status: 'success' | 'error') => {
    // Simple toast replacement - you can enhance this
    console.log(`${status.toUpperCase()}: ${title} - ${description}`);
    alert(`${title}\n${description}`);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setLoginLoading(true);

    try {
      await login(loginEmail, loginPassword);
      showToast('Welcome back!', 'You have successfully logged in.', 'success');
      onClose();
      // Reset form
      setLoginEmail('');
      setLoginPassword('');
    } catch (error: any) {
      setLoginError(error.message || 'Login failed');
      showToast('Login failed', error.message || 'Please check your credentials and try again.', 'error');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError('');
    setRegisterLoading(true);

    // Basic validation
    if (registerPassword.length < 6) {
      setRegisterError('Password must be at least 6 characters');
      setRegisterLoading(false);
      return;
    }

    if (registerUsername.length < 3) {
      setRegisterError('Username must be at least 3 characters');
      setRegisterLoading(false);
      return;
    }

    try {
      await register(registerEmail, registerUsername, registerPassword, registerFullName);
      showToast('Account created!', 'Welcome to Trendzl!', 'success');
      onClose();
      // Reset form
      setRegisterEmail('');
      setRegisterUsername('');
      setRegisterPassword('');
      setRegisterFullName('');
    } catch (error: any) {
      setRegisterError(error.message || 'Registration failed');
      showToast('Registration failed', error.message || 'Please try again.', 'error');
    } finally {
      setRegisterLoading(false);
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
      bg="rgba(0, 0, 0, 0.6)"
      backdropFilter="blur(8px)"
      zIndex={1000}
      display="flex"
      alignItems="center"
      justifyContent="center"
      onClick={onClose}
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
      >
        {/* Close Button */}
        <Button
          position="absolute"
          top={4}
          right={4}
          onClick={onClose}
          variant="ghost"
          fontSize="2xl"
          p={0}
          minW="auto"
          h="auto"
        >
          ×
        </Button>

        {/* Header */}
        <VStack spacing={4} mb={6}>
          <Box className="w-16 h-16 bg-black rounded-xl flex items-center justify-center">
            <img src="/photo.svg" alt="Trendzl Logo" className="w-10 h-10" />
          </Box>
          <Text fontSize="2xl" fontWeight="bold" className="font-orbitron">
            Welcome to Trendzl
          </Text>
        </VStack>

        {/* Tabs */}
        <HStack spacing={2} mb={6}>
          <Button
            flex={1}
            onClick={() => setActiveTab('login')}
            bg={activeTab === 'login' ? 'black' : 'white'}
            color={activeTab === 'login' ? 'white' : 'black'}
            border="1px solid"
            borderColor={activeTab === 'login' ? 'black' : 'gray.200'}
            _hover={{ bg: activeTab === 'login' ? 'gray.800' : 'gray.50' }}
            className="font-orbitron font-bold"
          >
            Login
          </Button>
          <Button
            flex={1}
            onClick={() => setActiveTab('register')}
            bg={activeTab === 'register' ? 'black' : 'white'}
            color={activeTab === 'register' ? 'white' : 'black'}
            border="1px solid"
            borderColor={activeTab === 'register' ? 'black' : 'gray.200'}
            _hover={{ bg: activeTab === 'register' ? 'gray.800' : 'gray.50' }}
            className="font-orbitron font-bold"
          >
            Register
          </Button>
        </HStack>

        {/* Login Form */}
        {activeTab === 'login' && (
          <form onSubmit={handleLogin}>
            <VStack spacing={4}>
              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <Mail className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Email
                  </Text>
                </HStack>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                  size="lg"
                  className="font-jetbrains"
                />
              </Box>

              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <Lock className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Password
                  </Text>
                </HStack>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  size="lg"
                  className="font-jetbrains"
                />
                {loginError && (
                  <Text color="red.500" fontSize="sm" mt={1}>
                    {loginError}
                  </Text>
                )}
              </Box>

              <Button
                type="submit"
                w="full"
                size="lg"
                bg="black"
                color="white"
                isDisabled={loginLoading}
                _hover={{ bg: 'gray.800' }}
                className="font-orbitron font-bold"
                mt={2}
              >
                {loginLoading ? 'Loading...' : 'Login'}
              </Button>
            </VStack>
          </form>
        )}

        {/* Register Form */}
        {activeTab === 'register' && (
          <form onSubmit={handleRegister}>
            <VStack spacing={4}>
              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <Mail className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Email
                  </Text>
                </HStack>
                <Input
                  type="email"
                  placeholder="your@email.com"
                  value={registerEmail}
                  onChange={(e) => setRegisterEmail(e.target.value)}
                  required
                  size="lg"
                  className="font-jetbrains"
                />
              </Box>

              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <User className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Username
                  </Text>
                </HStack>
                <Input
                  type="text"
                  placeholder="johndoe"
                  value={registerUsername}
                  onChange={(e) => setRegisterUsername(e.target.value)}
                  required
                  size="lg"
                  className="font-jetbrains"
                  minLength={3}
                />
              </Box>

              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <UserPlus className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Full Name (Optional)
                  </Text>
                </HStack>
                <Input
                  type="text"
                  placeholder="John Doe"
                  value={registerFullName}
                  onChange={(e) => setRegisterFullName(e.target.value)}
                  size="lg"
                  className="font-jetbrains"
                />
              </Box>

              <Box w="full">
                <HStack spacing={2} mb={2}>
                  <Lock className="w-4 h-4" />
                  <Text fontWeight="medium" className="font-inter">
                    Password
                  </Text>
                </HStack>
                <Input
                  type="password"
                  placeholder="••••••••"
                  value={registerPassword}
                  onChange={(e) => setRegisterPassword(e.target.value)}
                  required
                  size="lg"
                  className="font-jetbrains"
                  minLength={6}
                />
                {registerError && (
                  <Text color="red.500" fontSize="sm" mt={1}>
                    {registerError}
                  </Text>
                )}
              </Box>

              <Button
                type="submit"
                w="full"
                size="lg"
                bg="black"
                color="white"
                isDisabled={registerLoading}
                _hover={{ bg: 'gray.800' }}
                className="font-orbitron font-bold"
                mt={2}
              >
                {registerLoading ? 'Creating...' : 'Create Account'}
              </Button>
            </VStack>
          </form>
        )}
      </Box>
    </Box>
  );
};

export default AuthModal;