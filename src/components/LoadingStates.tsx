import React from 'react';
import { Search, Brain, TrendingUp, Sparkles } from 'lucide-react';
import LoadingSpinner from './LoadingSpinner';

interface LoadingStatesProps {
  stage: 'profile' | 'posts' | 'analysis' | 'trends';
}

const LoadingStates: React.FC<LoadingStatesProps> = ({ stage }) => {
  const stages = [
    {
      id: 'profile',
      icon: Search,
      title: 'Getting profile',
      description: 'Loading TikTok profile data...',
    },
    {
      id: 'posts',
      icon: TrendingUp,
      title: 'Analyzing posts',
      description: 'Collecting latest videos and statistics...',
    },
    {
      id: 'analysis',
      icon: Brain,
      title: 'AI analysis',
      description: 'GPT-4o extracts key hashtags...',
    },
    {
      id: 'trends',
      icon: Sparkles,
      title: 'Finding trends',
      description: 'Finding popular videos by hashtags...',
    },
  ];

  const currentStageIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="section-spacing animate-fade-in">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-accent/10 rounded-full mb-6 animate-pulse-slow">
            <Brain className="w-8 h-8 text-primary-accent" />
          </div>
          <h2 className="text-2xl font-bold text-text-primary mb-2">
            Analyzing trends
          </h2>
          <p className="text-text-secondary">
            Using AI to find the hottest videos
          </p>
        </div>

        {/* Progress Steps */}
        <div className="space-y-6">
          {stages.map((stageItem, index) => {
            const isActive = index === currentStageIndex;
            const isCompleted = index < currentStageIndex;
            const isPending = index > currentStageIndex;
            
            const Icon = stageItem.icon;

            return (
              <div
                key={stageItem.id}
                className={`
                  flex items-center space-x-4 p-4 rounded-card transition-all duration-300
                  ${isActive ? 'bg-primary-accent/5 border border-primary-accent/20' : ''}
                  ${isCompleted ? 'opacity-60' : ''}
                  ${isPending ? 'opacity-40' : ''}
                `}
              >
                {/* Icon */}
                <div className={`
                  flex items-center justify-center w-12 h-12 rounded-full
                  ${isActive ? 'bg-primary-accent text-white' : 
                    isCompleted ? 'bg-green-500 text-white' : 
                    'bg-primary-card border border-primary-line text-text-secondary'}
                `}>
                  {isActive ? (
                    <LoadingSpinner size="sm" className="text-white" />
                  ) : isCompleted ? (
                    <div className="w-6 h-6 flex items-center justify-center">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1">
                  <h3 className={`
                    font-semibold
                    ${isActive ? 'text-text-primary' : 
                      isCompleted ? 'text-green-400' : 
                      'text-text-secondary'}
                  `}>
                    {stageItem.title}
                  </h3>
                  <p className="text-text-secondary text-sm">
                    {stageItem.description}
                  </p>
                </div>

                {/* Status Indicator */}
                {isActive && (
                  <div className="flex items-center space-x-2 text-primary-accent">
                    <div className="w-2 h-2 bg-current rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-current rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Progress Bar */}
        <div className="mt-8">
          <div className="bg-primary-line rounded-full h-2 overflow-hidden">
            <div 
              className="bg-primary-accent h-full transition-all duration-500 ease-out"
              style={{ 
                width: `${((currentStageIndex + 1) / stages.length) * 100}%` 
              }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-text-secondary">
            <span>Start</span>
            <span>{Math.round(((currentStageIndex + 1) / stages.length) * 100)}%</span>
            <span>Complete</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingStates;
