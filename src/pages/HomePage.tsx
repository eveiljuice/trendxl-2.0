import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendVideo } from '../types';
import { useTrendAnalysis } from '../hooks/useTrendAnalysis';
import { useAuth } from '../contexts/AuthContext';
import { getSubscriptionInfo, createCheckoutSession } from '../services/subscriptionService';

// Components
import ProfileInput from '../components/ProfileInput';
import ProfileCard from '../components/ProfileCard';
import HashtagList from '../components/HashtagList';
import TrendGrid from '../components/TrendGrid';
import LoadingStates from '../components/LoadingStates';
import ErrorState from '../components/ErrorState';
import VideoModal from '../components/VideoModal';
import AuthModal from '../components/AuthModal';
import TokenUsageDisplay from '../components/TokenUsageDisplay';
import { SubscriptionBanner } from '../components/SubscriptionBanner';

function HomePage() {
  const { isAuthenticated, token } = useAuth();
  const navigate = useNavigate();
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
  const [isCheckingSubscription, setIsCheckingSubscription] = useState(false);

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

    // Check if user has an active subscription
    try {
      setIsCheckingSubscription(true);
      const subscriptionInfo = await getSubscriptionInfo(token!);
      
      // Check if user has an active subscription
      if (!subscriptionInfo.has_subscription || 
          !subscriptionInfo.subscription || 
          subscriptionInfo.subscription.status !== 'active') {
        // User doesn't have active subscription - redirect to Stripe Checkout
        const currentUrl = window.location.origin;
        const successUrl = `${currentUrl}/?session=success`;
        const cancelUrl = `${currentUrl}/?session=canceled`;
        
        const session = await createCheckoutSession(token!, successUrl, cancelUrl);
        
        // Redirect to Stripe Checkout page
        window.location.href = session.checkout_url;
        return;
      }
      
      // User has active subscription, proceed with analysis
      analyzeTrends(profileInput);
    } catch (error) {
      console.error('Error checking subscription:', error);
      // In case of error, show user-friendly message and redirect to profile
      alert('Не удалось проверить подписку. Пожалуйста, проверьте ваш профиль.');
      navigate('/profile');
    } finally {
      setIsCheckingSubscription(false);
    }
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
        <ProfileInput
          onSubmit={handleProfileSubmit}
          isLoading={isLoading || isCheckingSubscription}
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

          {/* Token Usage Display */}
          {tokenUsage && (
            <div className="animate-slide-up" style={{ animationDelay: '600ms' }}>
              <TokenUsageDisplay tokenUsage={tokenUsage} />
            </div>
          )}

          {/* New Analysis Button */}
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
  );
}

export default HomePage;

