import { useState, useCallback } from 'react';
import { TikTokProfile, TikTokPost, TrendVideo, AppState } from '../types';
import { analyzeProfileTrends, checkBackendHealth } from '../services/backendApi';
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
   * Main analysis function - uses new Python backend
   */
  const analyzeTrends = useCallback(async (profileInput: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const username = extractTikTokUsername(profileInput);
      console.log(`🚀 Начинаем анализ профиля через Python бэкенд: ${username}`);

      // Check backend health first
      const health = await checkBackendHealth();
      if (health.status !== 'healthy' && health.status !== 'degraded') {
        throw new Error('Backend сервис недоступен. Попробуйте позже.');
      }

      try {
        // Call Python backend for complete analysis
        const result = await analyzeProfileTrends(profileInput);
        
        updateState({
          profile: result.profile,
          posts: result.posts,
          hashtags: result.hashtags,
          trends: result.trends
        });
        
        console.log(`✅ Анализ завершен через Python бэкенд! Найдено ${result.trends.length} трендовых видео`);
        
      } catch (backendError) {
        console.error('❌ Backend анализ не удался:', backendError);
        
        // No mock data fallback - throw the actual error
        throw backendError;
      }
      
    } catch (error) {
      console.error('❌ Ошибка анализа трендов:', error);
      const errorMessage = error instanceof Error ? error.message : 'Произошла неизвестная ошибка';
      setError(errorMessage);
    } finally {
      setLoading(false);
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
    analyzeTrends,
    resetAnalysis,
    retryAnalysis,
  };
};

