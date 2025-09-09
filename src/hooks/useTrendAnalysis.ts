import { useState, useCallback } from 'react';
import { TikTokProfile, TikTokPost, TrendVideo, AppState } from '../types';
import { analyzeProfileTrends, analyzeProfileTrendsWithProgress, checkBackendHealth } from '../services/backendApi';
// Mock data service removed - using only real data
import { extractTikTokUsername } from '../utils';

export const useTrendAnalysis = () => {
  const [state, setState] = useState<AppState>({
    isLoading: false,
    profile: null,
    posts: [],
    hashtags: [],
    trends: [],
    error: null,
  });

  // Progress tracking state
  const [progress, setProgress] = useState({
    stage: 'profile' as 'profile' | 'posts' | 'analysis' | 'trends',
    message: '',
    percentage: 0,
    startTime: null as Date | null,
  });

  const setLoading = useCallback((loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState(prev => ({ ...prev, error }));
  }, []);

  const updateState = useCallback((updates: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  /**
   * Main analysis function with progress tracking
   */
  const analyzeTrends = useCallback(async (profileInput: string) => {
    try {
      setLoading(true);
      setError(null);
      setProgress({
        stage: 'profile',
        message: 'Initializing analysis...',
        percentage: 0,
        startTime: new Date(),
      });
      
      const username = extractTikTokUsername(profileInput);
      console.log(`🚀 Начинаем анализ профиля через Python бэкенд: ${username}`);

      // Check backend health first
      const health = await checkBackendHealth();
      if (health.status !== 'healthy' && health.status !== 'degraded') {
        throw new Error('Backend сервис недоступен. Попробуйте позже.');
      }

      // Progress callback
      const onProgress = (stage: string, message: string, percentage: number) => {
        console.log(`📊 Progress: ${stage} - ${message} (${percentage}%)`);
        setProgress(prev => ({
          ...prev,
          stage: stage as 'profile' | 'posts' | 'analysis' | 'trends',
          message,
          percentage,
        }));
      };

      try {
        // Call Python backend with progress tracking
        const result = await analyzeProfileTrendsWithProgress(profileInput, onProgress);
        
        updateState({
          profile: result.profile,
          posts: result.posts,
          hashtags: result.hashtags,
          trends: result.trends
        });
        
        console.log(`✅ Анализ завершен через Python бэкенд! Найдено ${result.trends.length} трендовых видео`);
        
      } catch (backendError) {
        console.error('❌ Backend анализ не удался:', backendError);
        
        // Fallback to simple analysis if progress version fails
        console.log('🔄 Пытаемся простой анализ без отслеживания прогресса...');
        const result = await analyzeProfileTrends(profileInput);
        
        updateState({
          profile: result.profile,
          posts: result.posts,
          hashtags: result.hashtags,
          trends: result.trends
        });
      }
      
    } catch (error) {
      console.error('❌ Ошибка анализа трендов:', error);
      const errorMessage = error instanceof Error ? error.message : 'Произошла неизвестная ошибка';
      setError(errorMessage);
    } finally {
      setLoading(false);
      setProgress(prev => ({ ...prev, percentage: 100 }));
    }
  }, [setLoading, setError, updateState]);

  /**
   * Reset analysis state
   */
  const resetAnalysis = useCallback(() => {
    setState({
      isLoading: false,
      profile: null,
      posts: [],
      hashtags: [],
      trends: [],
      error: null,
    });
    setProgress({
      stage: 'profile',
      message: '',
      percentage: 0,
      startTime: null,
    });
  }, []);

  /**
   * Retry analysis with the same profile
   */
  const retryAnalysis = useCallback(() => {
    if (state.profile) {
      analyzeTrends(state.profile.username);
    }
  }, [state.profile, analyzeTrends]);

  return {
    ...state,
    progress,
    analyzeTrends,
    resetAnalysis,
    retryAnalysis,
  };
};

