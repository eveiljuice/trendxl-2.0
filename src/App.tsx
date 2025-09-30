import React, { useState } from 'react';
import { TrendVideo } from './types';
import { useTrendAnalysis } from './hooks/useTrendAnalysis';
import { useAuth } from './contexts/AuthContext';
import { Box, HStack } from '@chakra-ui/react';

// Components
import ProfileInput from './components/ProfileInput';
import ProfileCard from './components/ProfileCard';
import HashtagList from './components/HashtagList';
import TrendGrid from './components/TrendGrid';
import LoadingStates from './components/LoadingStates';
import ErrorState from './components/ErrorState';
import VideoModal from './components/VideoModal';
import AuthModal from './components/AuthModal';
import UserProfileDropdown from './components/UserProfileDropdown';
import GradientText from './components/GradientText';
import TokenUsageDisplay from './components/TokenUsageDisplay';
// import Footer from './components/Footer';

function App() {
  const { isAuthenticated, user } = useAuth();
  const {
    isLoading,
    profile,
    posts,
    hashtags,
    trends,
    error,
    tokenUsage,
    progress,
    analyzeTrends,
    resetAnalysis,
    retryAnalysis,
  } = useTrendAnalysis();

  const [selectedTrend, setSelectedTrend] = useState<TrendVideo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Determine current loading stage based on available data
  const getLoadingStage = () => {
    if (!profile) return 'profile';
    if (posts.length === 0) return 'posts';
    if (hashtags.length === 0) return 'analysis';
    return 'trends';
  };

  const handleTrendClick = (trend: TrendVideo) => {
    setSelectedTrend(trend);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedTrend(null);
  };

  const handleProfileSubmit = (profileInput: string) => {
    // Check if user is authenticated
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      return;
    }
    analyzeTrends(profileInput);
  };

  const handleReset = () => {
    resetAnalysis();
    setSelectedTrend(null);
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-white flex flex-col relative">
      {/* Header with User Profile */}
      {isAuthenticated && (
        <Box className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
          <div className="container mx-auto px-4 sm:px-6 md:px-8 py-4">
            <HStack justify="space-between" align="center">
              <HStack spacing={3}>
                <img src="/photo.svg" alt="Trendzl Logo" className="w-8 h-8" />
                <span className="font-orbitron font-bold text-xl text-black">Trendzl</span>
              </HStack>
              <UserProfileDropdown />
            </HStack>
          </div>
        </Box>
      )}
      
      <div className="container mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 flex-grow">
        {/* Error State */}
        {error && (
          <ErrorState
            error={error}
            onRetry={retryAnalysis}
            onReset={handleReset}
            onDemoProfile={undefined} // No demo mode
            isLoading={isLoading}
          />
        )}

        {/* Loading State */}
        {isLoading && !error && (
          <LoadingStates 
            stage={progress.stage}
            message={progress.message}
            percentage={progress.percentage}
            startTime={progress.startTime}
          />
        )}

        {/* Initial State - Profile Input */}
        {!isLoading && !error && !profile && (
          <ProfileInput
            onSubmit={handleProfileSubmit}
            isLoading={isLoading}
          />
        )}

        {/* Results State - адаптивные отступы */}
        {!isLoading && !error && profile && (
          <div className="space-y-8 sm:space-y-12 md:space-y-16">
            {/* Profile Information */}
            <div className="animate-fade-in">
              <ProfileCard profile={profile} />
            </div>

            {/* Hashtags */}
            {hashtags.length > 0 && (
              <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
                <HashtagList hashtags={hashtags} />
              </div>
            )}

            {/* Trends Grid */}
            {trends.length > 0 && (
              <div className="animate-slide-up" style={{ animationDelay: '400ms' }}>
                <TrendGrid
                  trends={trends}
                  onTrendClick={handleTrendClick}
                />
              </div>
            )}

            {/* Token Usage Display */}
            {tokenUsage && (
              <div className="animate-slide-up" style={{ animationDelay: '600ms' }}>
                <TokenUsageDisplay tokenUsage={tokenUsage} />
              </div>
            )}

            {/* New Analysis Button - адаптивный */}
            <div className="text-center animate-fade-in" style={{ animationDelay: '800ms' }}>
              <button
                onClick={handleReset}
                className="btn-primary text-sm sm:text-base px-5 py-2.5 sm:px-6 sm:py-3"
              >
                Analyze another profile
              </button>
            </div>
          </div>
        )}

        {/* Video Modal */}
        <VideoModal
          trend={selectedTrend}
          isOpen={isModalOpen}
          onClose={handleCloseModal}
        />
        
        {/* Auth Modal */}
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
        />
      </div>

      {/* Footer */}
      {/* <Footer /> */}
    </div>
  );
}

export default App;
