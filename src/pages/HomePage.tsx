import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { TrendVideo } from '../types';
import { useTrendAnalysis } from '../hooks/useTrendAnalysis';
import { useAuth } from '../contexts/AuthContext';
import { getFreeTrialInfo } from '../services/subscriptionService';

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
import { UnifiedSubscriptionBanner } from '../components/UnifiedSubscriptionBanner';

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
  const [canUseFreeTrialState, setCanUseFreeTrialState] = useState<boolean | null>(null);

  // Load saved analysis from My Trends navigation
  useEffect(() => {
    if (location.state?.savedAnalysis && location.state?.username) {
      loadSavedAnalysis(location.state.savedAnalysis, location.state.username);
      // Clear the state after loading
      window.history.replaceState({}, document.title);
    }
  }, [location.state, loadSavedAnalysis]);

  // Check free trial status on mount and when authenticated
  useEffect(() => {
    const checkFreeTrialStatus = async () => {
      if (isAuthenticated) {
        try {
          const trialInfo = await getFreeTrialInfo();
          // User can use free trial if: is admin OR has subscription OR can use free trial
          const canUse = trialInfo.is_admin || trialInfo.has_subscription || trialInfo.can_use_free_trial;
          setCanUseFreeTrialState(canUse);
          
          console.log('🔍 Free trial status check:', {
            is_admin: trialInfo.is_admin,
            has_subscription: trialInfo.has_subscription,
            can_use_free_trial: trialInfo.can_use_free_trial,
            today_count: trialInfo.today_count,
            daily_limit: trialInfo.daily_limit,
            RESULT_canUse: canUse
          });
          
          // If user cannot use trial, show subscription modal immediately
          if (!canUse && !trialInfo.is_admin && !trialInfo.has_subscription) {
            console.log('⚠️ Free trial exhausted on load, user should see blocked UI');
          }
        } catch (error) {
          console.error('❌ Failed to check free trial status:', error);
          setCanUseFreeTrialState(true); // Default to allowing if check fails
        }
      } else {
        setCanUseFreeTrialState(null); // Not authenticated
      }
    };

    checkFreeTrialStatus();
  }, [isAuthenticated]);
  
  // Auto-refresh free trial status every 30 seconds when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const interval = setInterval(async () => {
      try {
        const trialInfo = await getFreeTrialInfo();
        const canUse = trialInfo.is_admin || trialInfo.has_subscription || trialInfo.can_use_free_trial;
        setCanUseFreeTrialState(canUse);
        console.log('🔄 Auto-refreshed free trial status:', canUse);
      } catch (error) {
        console.error('❌ Failed to auto-refresh free trial status:', error);
      }
    }, 30000); // Every 30 seconds
    
    return () => clearInterval(interval);
  }, [isAuthenticated]);

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

    // CRITICAL: Check free trial status BEFORE calling analyzeTrends
    // This prevents unnecessary API calls and provides immediate feedback
    try {
      const trialInfo = await getFreeTrialInfo();
      
      console.log('🔍 Free trial check before analysis:', {
        is_admin: trialInfo.is_admin,
        has_subscription: trialInfo.has_subscription,
        can_use_free_trial: trialInfo.can_use_free_trial,
        today_count: trialInfo.today_count,
        daily_limit: trialInfo.daily_limit,
        FULL_OBJECT: trialInfo
      });
      
      // If user is not admin and doesn't have subscription
      if (!trialInfo.is_admin && !trialInfo.has_subscription) {
        // Check if they can use free trial
        if (!trialInfo.can_use_free_trial) {
          console.log('🔒 Free trial exhausted, showing subscription modal');
          setShowSubscriptionModal(true);
          return; // Don't proceed with analysis
        } else {
          console.log('🎁 Free trial AVAILABLE:', `${trialInfo.today_count}/${trialInfo.daily_limit} used today`);
        }
      } else {
        console.log('✨ Admin or subscription user, unlimited access');
      }
      
      // If checks passed, proceed with analysis
      console.log('✅ Free trial check passed, proceeding with analysis');
      analyzeTrends(profileInput);
      
    } catch (error) {
      console.error('Failed to check free trial status:', error);
      // If check fails, still try to analyze - backend will handle it
      analyzeTrends(profileInput);
    }
  };

  const handleReset = () => {
    resetAnalysis();
    setSelectedTrend(null);
    setIsModalOpen(false);
  };

  return (
    <div className="container mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8 flex-grow">
      {/* Unified Subscription Banner */}
      {isAuthenticated && <UnifiedSubscriptionBanner refreshTrigger={profile ? Date.now() : undefined} />}
      
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
        <ProfileInput
          onSubmit={handleProfileSubmit}
          isLoading={isLoading}
          canUseTrial={canUseFreeTrialState}
          onSubscribeClick={() => setShowSubscriptionModal(true)}
        />
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

