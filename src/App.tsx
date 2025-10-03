import { useState } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import { Box, HStack, Button } from '@chakra-ui/react';
import { User } from 'lucide-react';

// Components
import UserProfileDropdown from './components/UserProfileDropdown';
import AuthModal from './components/AuthModal';
import HomePage from './pages/HomePage';
import MyProfile from './components/MyProfile';
import SubscriptionSuccess from './pages/SubscriptionSuccess';
import MyTrends from './pages/MyTrends';
import AnalysisResultPage from './pages/AnalysisResultPage';

function App() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-white flex flex-col relative">
      {/* Header - Always Visible */}
      <Box className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="container mx-auto px-4 sm:px-6 md:px-8 py-4">
          <HStack justify="space-between" align="center">
            {/* Logo */}
            <HStack 
              gap={3} 
              cursor="pointer"
              onClick={() => navigate('/')}
              _hover={{ opacity: 0.8 }}
            >
              <img src="/photo.svg" alt="Trendzl Logo" className="w-8 h-8" />
              <span className="font-orbitron font-bold text-xl text-black">Trendzl</span>
            </HStack>
            
            {/* Right Side - Auth or Profile */}
            {isAuthenticated ? (
              <UserProfileDropdown />
            ) : (
              <Button
                onClick={() => setIsAuthModalOpen(true)}
                bg="black"
                color="white"
                size="md"
                className="font-orbitron font-bold"
                _hover={{ bg: 'gray.800' }}
              >
                <HStack gap={2}>
                  <User className="w-4 h-4" />
                  <span>Sign In / Sign Up</span>
                </HStack>
              </Button>
            )}
          </HStack>
        </div>
      </Box>
      
      {/* Routes */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile" element={<MyProfile />} />
        <Route path="/my-trends" element={<MyTrends />} />
        <Route path="/analysis/:id" element={<AnalysisResultPage />} />
        <Route path="/subscription/success" element={<SubscriptionSuccess />} />
      </Routes>
      
      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </div>
  );
}

export default App;
