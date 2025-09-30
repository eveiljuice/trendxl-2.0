import React, { useEffect, useRef, useState } from 'react';
import { Search, Brain, TrendingUp, Sparkles, CheckCircle2, Clock, Activity, ChevronDown, ChevronUp, Eye, EyeOff } from 'lucide-react';
import { Line } from '@rc-component/progress';
import LoadingSpinner from './LoadingSpinner';

interface LoadingStatesProps {
  stage: 'profile' | 'posts' | 'analysis' | 'trends';
  message?: string;
  percentage?: number;
  startTime?: Date | null;
}

const LoadingStates: React.FC<LoadingStatesProps> = ({ 
  stage, 
  message = '',
  percentage = 0,
  startTime 
}) => {
  const [pulseIntensity, setPulseIntensity] = useState(0);
  const [stageProgress, setStageProgress] = useState({});
  const [showDetails, setShowDetails] = useState(false); // По умолчанию скрыто
  const progressRef = useRef<HTMLDivElement>(null);

  const stages = [
    {
      id: 'profile',
      icon: Search,
      title: 'Getting profile',
      description: 'Initializing analysis...',
      color: '#3b82f6',
      estimatedTime: '10-15s',
    },
    {
      id: 'posts',
      icon: TrendingUp,
      title: 'Analyzing posts',
      description: 'Collecting latest videos and statistics...',
      color: '#8b5cf6',
      estimatedTime: '15-20s',
    },
    {
      id: 'analysis',
      icon: Brain,
      title: 'AI analysis',
      description: 'GPT-4o extracts key hashtags...',
      color: '#06b6d4',
      estimatedTime: '20-30s',
    },
    {
      id: 'trends',
      icon: Sparkles,
      title: 'Finding trends',
      description: 'Finding popular videos by hashtags...',
      color: '#10b981',
      estimatedTime: '10-15s',
    },
  ];

  const currentStageIndex = stages.findIndex(s => s.id === stage);
  
  // Calculate elapsed time and estimated remaining time
  const elapsedTime = startTime ? Math.floor((Date.now() - startTime.getTime()) / 1000) : 0;
  const estimatedTotal = 75; // Total estimated seconds
  const remainingTime = Math.max(0, estimatedTotal - elapsedTime);
  
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Pulse effect for active stage
  useEffect(() => {
    const interval = setInterval(() => {
      setPulseIntensity(prev => (prev + 1) % 100);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  // Calculate individual stage progress
  useEffect(() => {
    const baseProgress = Math.floor(percentage / stages.length);
    const stageSpecificProgress = percentage % (100 / stages.length);
    
    const newStageProgress = {};
    stages.forEach((_, index) => {
      if (index < currentStageIndex) {
        newStageProgress[index] = 100;
      } else if (index === currentStageIndex) {
        newStageProgress[index] = Math.min(100, (percentage - (index * 25)));
      } else {
        newStageProgress[index] = 0;
      }
    });
    
    setStageProgress(newStageProgress);
  }, [percentage, currentStageIndex, stages.length]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center animate-fade-in px-4 sm:px-6">
      <div className="max-w-3xl mx-auto w-full">
        {/* Enhanced Header - адаптивные отступы */}
        <div className="text-center mb-8 sm:mb-12">
          <div 
            className="inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 rounded-full mb-4 sm:mb-6 relative overflow-hidden"
            style={{
              background: `conic-gradient(from 0deg, ${stages[currentStageIndex]?.color || '#000'}, transparent 60%, ${stages[currentStageIndex]?.color || '#000'})`,
              animation: 'spin 3s linear infinite'
            }}
          >
            <div className="w-12 h-12 sm:w-16 sm:h-16 bg-white rounded-full flex items-center justify-center">
              <Activity className="w-6 h-6 sm:w-8 sm:h-8 text-gray-700 animate-pulse" />
            </div>
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Analyzing trends
          </h2>
          <p className="text-sm sm:text-base text-gray-600 mb-3 sm:mb-4">
            Using AI to find the hottest videos
          </p>
          
          {/* Enhanced Time Display - адаптивно скрываем некоторые элементы */}
          <div className="flex flex-wrap justify-center items-center gap-2 sm:gap-4 md:gap-6 text-xs sm:text-sm">
            {startTime && (
              <>
                <div className="flex items-center space-x-1 text-blue-600">
                  <Clock className="w-3 h-3 sm:w-4 sm:h-4" />
                  <span className="hidden xs:inline">Elapsed: </span>{formatTime(elapsedTime)}
                </div>
                <div className="text-gray-400 hidden sm:inline">•</div>
                <div className="flex items-center space-x-1 text-green-600">
                  <Activity className="w-3 h-3 sm:w-4 sm:h-4" />
                  <span>{Math.round(percentage)}%</span>
                </div>
                <div className="text-gray-400 hidden md:inline">•</div>
                <div className="text-gray-500 hidden md:inline">
                  ~{formatTime(remainingTime)} remaining
                </div>
              </>
            )}
          </div>
        </div>

        {/* Main Progress Bar - адаптивные отступы */}
        <div className="mb-6 sm:mb-8">
          <Line
            percent={percentage}
            strokeWidth={3}
            strokeColor={{
              '0%': stages[0].color,
              '25%': stages[1].color,
              '50%': stages[2].color,
              '75%': stages[3].color,
              '100%': stages[3].color,
            }}
            trailColor="#f3f4f6"
            strokeLinecap="round"
            className="mb-2"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Start</span>
            <span className="font-medium">{Math.round(percentage)}%</span>
            <span>Complete</span>
          </div>
        </div>

        {/* Toggle Details Button - адаптивные размеры */}
        <div className="mb-4 sm:mb-6 text-center">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="inline-flex items-center space-x-1.5 sm:space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm text-gray-600 hover:text-gray-900 bg-white hover:bg-gray-50 border border-gray-200 rounded-full transition-all duration-200 hover:shadow-sm"
          >
            {showDetails ? <EyeOff className="w-3 h-3 sm:w-4 sm:h-4" /> : <Eye className="w-3 h-3 sm:w-4 sm:h-4" />}
            <span className="hidden xs:inline">{showDetails ? 'Hide Details' : 'Show Details'}</span>
            {showDetails ? <ChevronUp className="w-3 h-3 sm:w-4 sm:h-4" /> : <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4" />}
          </button>
        </div>

        {/* Enhanced Progress Steps - Collapsible */}
        <div 
          className={`
            transition-all duration-500 ease-in-out overflow-hidden
            ${showDetails 
              ? 'max-h-screen opacity-100 transform translate-y-0' 
              : 'max-h-0 opacity-0 transform -translate-y-4'
            }
          `}
        >
          <div className="space-y-4">
            {stages.map((stageItem, index) => {
              const isActive = index === currentStageIndex;
              const isCompleted = index < currentStageIndex;
              const isPending = index > currentStageIndex;
              const stagePercentage = stageProgress[index] || 0;
              
              const Icon = stageItem.icon;

              return (
                <div
                  key={stageItem.id}
                  className={`
                    relative overflow-hidden rounded-lg sm:rounded-xl p-3 sm:p-4 md:p-6 transition-all duration-500 transform
                    ${isActive ? 'bg-gradient-to-r from-blue-50 to-purple-50 border-2 sm:scale-105 shadow-lg' : ''}
                    ${isCompleted ? 'bg-green-50 border border-green-200' : ''}
                    ${isPending ? 'bg-gray-50 border border-gray-200 opacity-60' : ''}
                  `}
                  style={{
                    borderColor: isActive ? stageItem.color : undefined,
                  }}
                >
                  {/* Stage Progress Background */}
                  {isActive && (
                    <div
                      className="absolute inset-0 transition-all duration-1000"
                      style={{
                        background: `linear-gradient(90deg, ${stageItem.color}15 0%, ${stageItem.color}05 ${stagePercentage}%, transparent ${stagePercentage}%)`,
                      }}
                    />
                  )}

                  <div className="relative flex items-center space-x-3 sm:space-x-4 md:space-x-6">
                    {/* Enhanced Icon - адаптивные размеры */}
                    <div className="relative flex-shrink-0">
                      <div 
                        className={`
                          flex items-center justify-center w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 rounded-full transition-all duration-300
                          ${isActive ? 'shadow-lg animate-pulse' : ''}
                          ${isCompleted ? 'bg-green-500 text-white' : ''}
                          ${isPending ? 'bg-gray-200 text-gray-500' : ''}
                        `}
                        style={{
                          backgroundColor: isActive ? stageItem.color : undefined,
                          color: isActive ? 'white' : undefined,
                        }}
                      >
                        {isActive ? (
                          <Icon className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8" />
                        ) : isCompleted ? (
                          <CheckCircle2 className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8" />
                        ) : (
                          <Icon className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8" />
                        )}
                      </div>
                      
                      {/* Pulse ring for active stage */}
                      {isActive && (
                        <div 
                          className="absolute inset-0 rounded-full opacity-75 animate-ping"
                          style={{
                            backgroundColor: stageItem.color,
                          }}
                        />
                      )}
                    </div>

                    {/* Enhanced Content - адаптивные размеры */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1.5 sm:mb-2 gap-1 sm:gap-0">
                        <h3 className={`
                          text-base sm:text-lg font-semibold transition-colors duration-300
                          ${isActive ? 'text-gray-900' : 
                            isCompleted ? 'text-green-700' : 
                            'text-gray-500'}
                        `}>
                          {stageItem.title}
                        </h3>
                        
                        {/* Stage Status - адаптивные размеры */}
                        <div className="text-xs sm:text-sm font-medium">
                          {isCompleted && (
                            <span className="text-green-600 flex items-center">
                              <CheckCircle2 className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 sm:mr-1" />
                              <span className="text-xs sm:text-sm">Completed</span>
                            </span>
                          )}
                          {isActive && (
                            <span className="text-blue-600 flex items-center">
                              <Activity className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 sm:mr-1 animate-pulse" />
                              <span className="text-xs sm:text-sm">{Math.round(stagePercentage)}%</span>
                            </span>
                          )}
                          {isPending && (
                            <span className="text-gray-400 flex items-center">
                              <Clock className="w-3 h-3 sm:w-4 sm:h-4 mr-0.5 sm:mr-1" />
                              <span className="text-xs sm:text-sm hidden sm:inline">{stageItem.estimatedTime}</span>
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <p className={`
                        text-xs sm:text-sm mb-2 sm:mb-3 transition-colors duration-300
                        ${isActive ? 'text-gray-700' : 
                          isCompleted ? 'text-green-600' : 
                          'text-gray-500'}
                      `}>
                        {isActive && message ? message : stageItem.description}
                      </p>

                      {/* Individual Stage Progress Bar */}
                      {isActive && (
                        <div className="w-full">
                          <Line
                            percent={stagePercentage}
                            strokeWidth={2}
                            strokeColor={stageItem.color}
                            trailColor="#f3f4f6"
                            strokeLinecap="round"
                          />
                        </div>
                      )}
                    </div>

                    {/* Animated Status Indicator - скрываем на мобильных */}
                    {isActive && (
                      <div className="hidden sm:flex flex-col items-center space-y-1">
                        <div className="flex space-x-1">
                          {[...Array(3)].map((_, i) => (
                            <div
                              key={i}
                              className="w-2 h-2 rounded-full animate-bounce"
                              style={{
                                backgroundColor: stageItem.color,
                                animationDelay: `${i * 0.2}s`,
                              }}
                            />
                          ))}
                        </div>
                        <span className="text-xs text-gray-500">Processing...</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Compact Stage Indicators (когда детали скрыты) - адаптивные отступы */}
        {!showDetails && (
          <div className="flex justify-center items-center space-x-3 sm:space-x-4 md:space-x-6 mb-4 sm:mb-6">
            {stages.map((stageItem, index) => {
              const isActive = index === currentStageIndex;
              const isCompleted = index < currentStageIndex;
              const isPending = index > currentStageIndex;
              
              const Icon = stageItem.icon;

              return (
                <div key={stageItem.id} className="flex flex-col items-center space-y-1 sm:space-y-2">
                  <div 
                    className={`
                      flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-full transition-all duration-300
                      ${isActive ? 'shadow-lg animate-pulse' : ''}
                      ${isCompleted ? 'bg-green-500 text-white' : ''}
                      ${isPending ? 'bg-gray-200 text-gray-500' : ''}
                    `}
                    style={{
                      backgroundColor: isActive ? stageItem.color : undefined,
                      color: isActive ? 'white' : undefined,
                    }}
                  >
                    {isActive ? (
                      <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                    ) : isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 sm:w-6 sm:h-6" />
                    ) : (
                      <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                    )}
                  </div>
                  <span className={`
                    text-xs font-medium transition-colors hidden sm:block
                    ${isActive ? 'text-gray-900' : 
                      isCompleted ? 'text-green-600' : 
                      'text-gray-400'}
                  `}>
                    {stageItem.title}
                  </span>
                  {isActive && (
                    <div className="flex space-x-0.5 sm:space-x-1">
                      {[...Array(3)].map((_, i) => (
                        <div
                          key={i}
                          className="w-1 h-1 rounded-full animate-bounce"
                          style={{
                            backgroundColor: stageItem.color,
                            animationDelay: `${i * 0.2}s`,
                          }}
                        />
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Activity Footer - адаптивные отступы */}
        <div className="mt-6 sm:mt-8 text-center">
          <div className="inline-flex items-center space-x-1.5 sm:space-x-2 text-xs sm:text-sm text-gray-600 bg-gray-50 rounded-full px-3 py-1.5 sm:px-4 sm:py-2">
            <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-blue-500 rounded-full animate-pulse flex-shrink-0"></div>
            <span className="hidden sm:inline">System is actively processing your request</span>
            <span className="sm:hidden">Processing...</span>
          </div>
          {startTime && percentage > 0 && percentage < 100 && (
            <div className="mt-2 sm:mt-3 text-xs text-gray-500">
              <div className="flex flex-wrap justify-center items-center gap-2 sm:gap-4">
                <span className="hidden sm:inline">Speed: {(percentage / Math.max(elapsedTime, 1)).toFixed(1)}%/s</span>
                <span className="hidden md:inline">•</span>
                <span className="hidden md:inline">ETA: ~{formatTime(Math.max(0, Math.ceil((elapsedTime / percentage) * (100 - percentage))))}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LoadingStates;
