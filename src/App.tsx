import React, { useState } from 'react';
import { TrendVideo } from './types';
import { useTrendAnalysis } from './hooks/useTrendAnalysis';

// Components
import ProfileInput from './components/ProfileInput';
import ProfileCard from './components/ProfileCard';
import HashtagList from './components/HashtagList';
import TrendGrid from './components/TrendGrid';
import LoadingStates from './components/LoadingStates';
import ErrorState from './components/ErrorState';
import VideoModal from './components/VideoModal';

function App() {
  const {
    isLoading,
    profile,
    posts,
    hashtags,
    trends,
    error,
    analyzeTrends,
    resetAnalysis,
    retryAnalysis,
  } = useTrendAnalysis();

  const [selectedTrend, setSelectedTrend] = useState<TrendVideo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
    analyzeTrends(profileInput);
  };

  const handleReset = () => {
    resetAnalysis();
    setSelectedTrend(null);
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen bg-primary-bg flex flex-col">
      <div className="container mx-auto px-4 py-8 flex-grow">
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
          <LoadingStates stage={getLoadingStage()} />
        )}

        {/* Initial State - Profile Input */}
        {!isLoading && !error && !profile && (
          <ProfileInput
            onSubmit={handleProfileSubmit}
            isLoading={isLoading}
          />
        )}

        {/* Results State */}
        {!isLoading && !error && profile && (
          <div className="space-y-16">
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
                className="
                  px-8 py-3 
                  bg-primary-card border border-primary-line rounded-btn
                  text-text-primary hover:text-text-primary hover:border-primary-accent/30
                  transition-all duration-150
                "
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
      </div>

      {/* Footer */}
      <footer className="border-t border-primary-line bg-primary-card/50 backdrop-blur-sm mt-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-text-secondary text-sm">
            <p className="mb-2">
              TrendXL 2.0 - Powered by{' '}
              <span className="text-primary-accent font-medium">Ensemble Data API</span>{' '}
              &{' '}
              <span className="text-primary-accent font-medium">OpenAI GPT-4o</span>
            </p>
            <p className="text-xs opacity-75">
              Analyzing TikTok trends with artificial intelligence
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
