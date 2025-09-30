import React, { useState } from 'react';
import {
  Box,
  Button,
  Text,
  HStack,
  VStack,
} from '@chakra-ui/react';
import { User, Settings, LogOut, TrendingUp, ChevronDown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const UserProfileDropdown: React.FC = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  if (!user) return null;

  const getInitials = (name?: string) => {
    if (!name) return user.username.substring(0, 2).toUpperCase();
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  const getAvatarUrl = () => {
    if (user.avatar_url) return user.avatar_url;
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(
      user.full_name || user.username
    )}&background=000000&color=ffffff&bold=true`;
  };

  return (
    <Box position="relative">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        variant="ghost"
        p={0}
        h="auto"
        _hover={{ bg: 'transparent' }}
        _active={{ bg: 'transparent' }}
      >
        <HStack spacing={3}>
          <Box
            w="32px"
            h="32px"
            borderRadius="full"
            overflow="hidden"
            bg="black"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            {user.avatar_url ? (
              <img
                src={getAvatarUrl()}
                alt={user.full_name || user.username}
                className="w-full h-full object-cover"
              />
            ) : (
              <Text color="white" fontSize="sm" fontWeight="bold">
                {getInitials(user.full_name)}
              </Text>
            )}
          </Box>
          <VStack spacing={0} align="start" display={{ base: 'none', md: 'flex' }}>
            <Text fontSize="sm" fontWeight="bold" className="font-inter">
              {user.full_name || user.username}
            </Text>
            <Text fontSize="xs" color="gray.600" className="font-jetbrains">
              @{user.username}
            </Text>
          </VStack>
          <ChevronDown className="w-4 h-4" />
        </HStack>
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Overlay to close dropdown */}
          <Box
            position="fixed"
            top="0"
            left="0"
            right="0"
            bottom="0"
            zIndex={999}
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <Box
            position="absolute"
            top="100%"
            right="0"
            mt={2}
            bg="white"
            borderWidth="1px"
            borderColor="gray.200"
            borderRadius="xl"
            shadow="xl"
            minW="250px"
            zIndex={1000}
          >
            {/* User Info Header */}
            <Box px={4} py={3} borderBottomWidth={1} borderColor="gray.100">
              <VStack spacing={1} align="start">
                <Text fontSize="md" fontWeight="bold" className="font-inter">
                  {user.full_name || user.username}
                </Text>
                <Text fontSize="sm" color="gray.600" className="font-jetbrains">
                  {user.email}
                </Text>
                {user.bio && (
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    {user.bio}
                  </Text>
                )}
              </VStack>
            </Box>

            {/* Menu Items */}
            <VStack spacing={0} p={2}>
              <Button
                w="full"
                justifyContent="flex-start"
                variant="ghost"
                onClick={() => {
                  setIsOpen(false);
                  console.log('Open profile');
                }}
                className="font-inter"
              >
                <HStack spacing={2}>
                  <User className="w-4 h-4" />
                  <Text>My Profile</Text>
                </HStack>
              </Button>

              <Button
                w="full"
                justifyContent="flex-start"
                variant="ghost"
                onClick={() => {
                  setIsOpen(false);
                  console.log('Open saved trends');
                }}
                className="font-inter"
              >
                <HStack spacing={2}>
                  <TrendingUp className="w-4 h-4" />
                  <Text>Saved Trends</Text>
                </HStack>
              </Button>

              <Button
                w="full"
                justifyContent="flex-start"
                variant="ghost"
                onClick={() => {
                  setIsOpen(false);
                  console.log('Open settings');
                }}
                className="font-inter"
              >
                <HStack spacing={2}>
                  <Settings className="w-4 h-4" />
                  <Text>Settings</Text>
                </HStack>
              </Button>

              <Box w="full" h="1px" bg="gray.200" my={2} />

              <Button
                w="full"
                justifyContent="flex-start"
                variant="ghost"
                onClick={() => {
                  setIsOpen(false);
                  logout();
                }}
                className="font-inter"
                color="red.500"
                _hover={{ bg: 'red.50' }}
              >
                <HStack spacing={2}>
                  <LogOut className="w-4 h-4" />
                  <Text>Logout</Text>
                </HStack>
              </Button>
            </VStack>
          </Box>
        </>
      )}
    </Box>
  );
};

export default UserProfileDropdown;