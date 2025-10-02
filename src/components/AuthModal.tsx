import React, { useState } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  HStack,
  Heading,
} from '@chakra-ui/react';
import { Mail, Lock, User, UserPlus, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { parseAuthError, type ErrorDetails } from '../utils/errorMessages';

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

  // Error states with details
  const [loginError, setLoginError] = useState<ErrorDetails | null>(null);
  const [registerError, setRegisterError] = useState<ErrorDetails | null>(null);

  const showToast = (title: string, description: string, status: 'success' | 'error') => {
    console.log(`${status.toUpperCase()}: ${title} - ${description}`);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError(null);
    setLoginLoading(true);

    try {
      await login(loginEmail, loginPassword);
      showToast('Добро пожаловать!', 'Вы успешно вошли в систему.', 'success');
      onClose();
      // Reset form
      setLoginEmail('');
      setLoginPassword('');
    } catch (error: any) {
      const errorDetails = parseAuthError(error);
      setLoginError(errorDetails);
      showToast(errorDetails.title, errorDetails.message, 'error');
      
      // Auto-switch to registration if user not found
      if (errorDetails.actionType === 'switch-tab') {
        const errorLower = (error?.response?.data?.detail || error?.message || '').toLowerCase();
        if (errorLower.includes('not found') || errorLower.includes('does not exist')) {
          // Suggest switching to registration
          setTimeout(() => {
            if (window.confirm(`${errorDetails.message}\n\nПерейти к регистрации?`)) {
              setActiveTab('register');
              setLoginError(null);
              // Pre-fill email
              setRegisterEmail(loginEmail);
            }
          }, 500);
        }
      }
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterError(null);
    setRegisterLoading(true);

    // Basic validation
    if (registerPassword.length < 6) {
      setRegisterError({
        title: 'Слишком короткий пароль',
        message: 'Пароль должен содержать минимум 6 символов.',
        action: 'Попробовать снова',
        actionType: 'retry'
      });
      setRegisterLoading(false);
      return;
    }

    if (registerUsername.length < 3) {
      setRegisterError({
        title: 'Слишком короткое имя',
        message: 'Имя пользователя должно содержать минимум 3 символа.',
        action: 'Попробовать снова',
        actionType: 'retry'
      });
      setRegisterLoading(false);
      return;
    }

    try {
      await register(registerEmail, registerUsername, registerPassword, registerFullName);
      showToast('Аккаунт создан!', 'Добро пожаловать в Trendzl!', 'success');
      onClose();
      // Reset form
      setRegisterEmail('');
      setRegisterUsername('');
      setRegisterPassword('');
      setRegisterFullName('');
    } catch (error: any) {
      const errorDetails = parseAuthError(error);
      setRegisterError(errorDetails);
      showToast(errorDetails.title, errorDetails.message, 'error');
      
      // Auto-switch to login if user already exists
      if (errorDetails.actionType === 'switch-tab') {
        const errorLower = (error?.response?.data?.detail || error?.message || '').toLowerCase();
        if (errorLower.includes('already') || errorLower.includes('exists')) {
          // Suggest switching to login
          setTimeout(() => {
            if (window.confirm(`${errorDetails.message}\n\nПерейти к входу?`)) {
              setActiveTab('login');
              setRegisterError(null);
              // Pre-fill email
              setLoginEmail(registerEmail);
            }
          }, 500);
        }
      }
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
              </Box>

              {/* Enhanced Error Display */}
              {loginError && (
                <Box 
                  bg="red.50" 
                  borderLeft="4px solid"
                  borderColor="red.500"
                  p={4}
                  borderRadius="md"
                >
                  <HStack spacing={2} mb={2}>
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <Heading size="sm" className="font-orbitron">
                      {loginError.title}
                    </Heading>
                  </HStack>
                  <Text fontSize="sm" className="font-inter" mb={loginError.action ? 3 : 0}>
                    {loginError.message}
                  </Text>
                  {loginError.action && loginError.actionType === 'switch-tab' && (
                    <Button
                      size="sm"
                      colorPalette="red"
                      variant="outline"
                      onClick={() => {
                        setActiveTab('register');
                        setLoginError(null);
                        setRegisterEmail(loginEmail);
                      }}
                    >
                      {loginError.action}
                    </Button>
                  )}
                </Box>
              )}

              <Button
                type="submit"
                w="full"
                size="lg"
                bg="black"
                color="white"
                disabled={loginLoading}
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
              </Box>

              {/* Enhanced Error Display */}
              {registerError && (
                <Box 
                  bg="red.50" 
                  borderLeft="4px solid"
                  borderColor="red.500"
                  p={4}
                  borderRadius="md"
                >
                  <HStack spacing={2} mb={2}>
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <Heading size="sm" className="font-orbitron">
                      {registerError.title}
                    </Heading>
                  </HStack>
                  <Text fontSize="sm" className="font-inter" mb={registerError.action ? 3 : 0}>
                    {registerError.message}
                  </Text>
                  {registerError.action && registerError.actionType === 'switch-tab' && (
                    <Button
                      size="sm"
                      colorPalette="red"
                      variant="outline"
                      onClick={() => {
                        setActiveTab('login');
                        setRegisterError(null);
                        setLoginEmail(registerEmail);
                      }}
                    >
                      {registerError.action}
                    </Button>
                  )}
                </Box>
              )}

              <Button
                type="submit"
                w="full"
                size="lg"
                bg="black"
                color="white"
                disabled={registerLoading}
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