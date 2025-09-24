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
import GradientText from './components/GradientText';

function App() {
  const {
    isLoading,
    profile,
    posts,
    hashtags,
    trends,
    error,
    progress,
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
    <div className="min-h-screen bg-background flex flex-col relative">
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
                className="btn-primary"
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

    </div>
  );
}

export default App;
