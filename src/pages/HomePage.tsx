import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { TrendVideo } from '../types';
import { useTrendAnalysis } from '../hooks/useTrendAnalysis';
import { useAuth } from '../contexts/AuthContext';

// Components
import ProfileInput from '../components/ProfileInput';
import ProfileCard from '../components/ProfileCard';
import HashtagList from '../components/HashtagList';
import TrendGrid from '../components/TrendGrid';
import LoadingStates from '../components/LoadingStates';
import ErrorState from '../components/ErrorState';
import VideoModal from '../components/VideoModal';
import AuthModal from '../components/AuthModal';
import SubscriptionModal from '../components/SubscriptionModal';
import { SubscriptionBanner } from '../components/SubscriptionBanner';
import { FreeTrialCounter } from '../components/FreeTrialCounter';

function HomePage() {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
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
    loadSavedAnalysis,
    showSubscriptionModal,
    setShowSubscriptionModal,
  } = useTrendAnalysis();

  const [selectedTrend, setSelectedTrend] = useState<TrendVideo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  // Load saved analysis from My Trends navigation
  useEffect(() => {
    if (location.state?.savedAnalysis && location.state?.username) {
      loadSavedAnalysis(location.state.savedAnalysis, location.state.username);
      // Clear the state after loading
      window.history.replaceState({}, document.title);
    }
  }, [location.state, loadSavedAnalysis]);

  const handleTrendClick = (trend: TrendVideo) => {
    setSelectedTrend(trend);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedTrend(null);
  };

  const handleProfileSubmit = async (profileInput: string) => {
    // Check if user is authenticated
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      return;
    }

    // Let backend handle subscription and free trial checks
    // Backend will return proper error if user has no access
    analyzeTrends(profileInput);
  };

  const handleReset = () => {
    resetAnalysis();
    setSelectedTrend(null);
    setIsModalOpen(false);
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 flex-grow">
      {/* Subscription Banner */}
      {isAuthenticated && <SubscriptionBanner />}
      
      {/* Error State */}
      {error && (
        <ErrorState
          error={error}
          onRetry={retryAnalysis}
          onReset={handleReset}
          onDemoProfile={undefined}
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
        <>
          {/* Free Trial Counter */}
          {isAuthenticated && <FreeTrialCounter refreshTrigger={profile ? Date.now() : undefined} />}
          
          <ProfileInput
            onSubmit={handleProfileSubmit}
            isLoading={isLoading}
          />
        </>
      )}

      {/* Results State */}
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

          {/* New Analysis Button */}
          <div className="text-center animate-fade-in" style={{ animationDelay: '600ms' }}>
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
      
      {/* Subscription Modal */}
      <SubscriptionModal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
      />
    </div>
  );
}

export default HomePage;

