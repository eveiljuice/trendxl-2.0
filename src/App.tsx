import React from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Box, HStack } from '@chakra-ui/react';

// Components
import UserProfileDropdown from './components/UserProfileDropdown';
import HomePage from './pages/HomePage';
import MyProfile from './components/MyProfile';
import SubscriptionSuccess from './pages/SubscriptionSuccess';

function App() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-white flex flex-col relative">
      {/* Header with User Profile */}
      {isAuthenticated && (
        <Box className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
          <div className="container mx-auto px-4 sm:px-6 md:px-8 py-4">
            <HStack justify="space-between" align="center">
              <HStack 
                spacing={3} 
                cursor="pointer"
                onClick={() => navigate('/')}
                _hover={{ opacity: 0.8 }}
              >
                <img src="/photo.svg" alt="Trendzl Logo" className="w-8 h-8" />
                <span className="font-orbitron font-bold text-xl text-black">Trendzl</span>
              </HStack>
              <UserProfileDropdown />
            </HStack>
          </div>
        </Box>
      )}
      
      {/* Routes */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile" element={<MyProfile />} />
        <Route path="/subscription/success" element={<SubscriptionSuccess />} />
      </Routes>
    </div>
  );
}

export default App;
