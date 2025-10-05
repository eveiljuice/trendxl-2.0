import { useState, useCallback, useEffect } from 'react';
import { TikTokProfile, AppState } from '../types';
import { analyzeProfileTrends, analyzeProfileTrendsWithProgress, analyzeCreativeCenterComplete, checkBackendHealth } from '../services/backendApi';
import { saveScanToHistory, saveLastSearchedUsername, getLastSearchedUsername } from '../services/scanHistoryService';
import { checkSubscriptionStatus } from '../services/subscriptionService';
import { useAuth } from '../contexts/AuthContext';
// Mock data service removed - using only real data
import { extractTikTokUsername } from '../utils';

/**
 * Determine scan type based on subscription status
 */
const determineScanType = async (): Promise<'free' | 'paid'> => {
  try {
    const status = await checkSubscriptionStatus();
    return status.has_active_subscription ? 'paid' : 'free';
  } catch (error) {
    console.error('Failed to check subscription status:', error);
    return 'free'; // Default to free if check fails
  }
};

export const useTrendAnalysis = () => {
  const { user } = useAuth();
  const [state, setState] = useState<AppState>({
    isLoading: false,
    profile: null,
    posts: [],
    hashtags: [],
    trends: [],
    error: null,
    tokenUsage: null,
  });

  // Progress tracking state
  const [progress, setProgress] = useState({
    stage: 'profile' as 'profile' | 'posts' | 'analysis' | 'trends',
    message: '',
    percentage: 0,
    startTime: null as Date | null,
  });

  // Load last searched username on mount
  const [lastSearchedUsername, setLastSearchedUsername] = useState<string | null>(null);
  
  useEffect(() => {
    const savedUsername = getLastSearchedUsername();
    if (savedUsername) {
      setLastSearchedUsername(savedUsername);
    }
  }, []);

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
        // First, try the new Creative Center complete analysis
        // Country and language will be auto-detected from the TikTok account itself
        console.log('🎯 Attempting Creative Center + Ensemble analysis with auto-detection...');
        const creativeResult = await analyzeCreativeCenterComplete(
          profileInput, 
          'US',   // Default - will be overridden by profile analysis
          'en',   // Default - will be overridden by profile analysis  
          5,      // hashtag limit
          3,      // videos per hashtag
          true,   // auto detect geo from TikTok account
          onProgress
        );
        
        // Extract hashtags from Creative Center result
        const creativeCenterHashtags = creativeResult.creative_center_hashtags.map(h => h.name);
        
        updateState({
          profile: creativeResult.profile,
          posts: [], // Creative Center analysis doesn't return user posts
          hashtags: creativeCenterHashtags,
          trends: creativeResult.trends,
          tokenUsage: null
        });
        
        // Determine scan type based on subscription status
        const scanType = await determineScanType();
        
        // Save FULL analysis to history and store last searched username
        const scanId = user?.id ? await saveScanToHistory(user.id, username, {
          profile: creativeResult.profile,
          trends: creativeResult.trends,
          hashtags: creativeCenterHashtags,
          posts: [],
          tokenUsage: null
        }, scanType) : null;
        saveLastSearchedUsername(username);
        setLastSearchedUsername(username);
        
        // Open analysis result in new tab if scan was saved
        if (scanId) {
          const url = `${window.location.origin}/analysis/${scanId}`;
          window.open(url, '_blank');
        }
        
        console.log(`✅ Creative Center анализ завершен! Найдено ${creativeResult.trends.length} трендовых видео и ${creativeCenterHashtags.length} хештегов из Creative Center`);
        
      } catch (creativeCenterError) {
        console.error('❌ Creative Center анализ не удался:', creativeCenterError);
        
        // Fallback to traditional analysis with progress tracking
        // НО БЕЗ хештегов - они должны приходить только из Creative Center!
        console.log('🔄 Переключаемся на традиционный анализ с отслеживанием прогресса...');
        try {
          const result = await analyzeProfileTrendsWithProgress(profileInput, onProgress);
          
          updateState({
            profile: result.profile,
            posts: result.posts,
            hashtags: result.hashtags, // Показываем хештеги из традиционного анализа
            trends: result.trends,
            tokenUsage: null
          });
          
          // Determine scan type based on subscription status
          const scanTypeTraditional = await determineScanType();
          
          // Save FULL analysis to history and store last searched username
          const scanId = user?.id ? await saveScanToHistory(user.id, username, {
            profile: result.profile,
            trends: result.trends,
            hashtags: result.hashtags,
            posts: result.posts || [],
            tokenUsage: null
          }, scanTypeTraditional) : null;
          saveLastSearchedUsername(username);
          setLastSearchedUsername(username);
          
          // Open analysis result in new tab if scan was saved
          if (scanId) {
            const url = `${window.location.origin}/analysis/${scanId}`;
            window.open(url, '_blank');
          }
          
          console.log(`✅ Традиционный анализ завершен! Найдено ${result.trends.length} трендовых видео и ${result.hashtags.length} хештегов`);
          
        } catch (backendError) {
          console.error('❌ Backend анализ не удался:', backendError);
          
          // Final fallback to simple analysis
          console.log('🔄 Пытаемся простой анализ без отслеживания прогресса...');
          const result = await analyzeProfileTrends(profileInput);
          
          updateState({
            profile: result.profile,
            posts: result.posts,
            hashtags: result.hashtags, // Показываем хештеги из простого анализа
            trends: result.trends,
            tokenUsage: null
          });
          
          // Determine scan type based on subscription status
          const scanTypeFinal = await determineScanType();
          
          // Save FULL analysis to history and store last searched username
          const scanId = user?.id ? await saveScanToHistory(user.id, username, {
            profile: result.profile,
            trends: result.trends,
            hashtags: result.hashtags,
            posts: result.posts || [],
            tokenUsage: null
          }, scanTypeFinal) : null;
          saveLastSearchedUsername(username);
          setLastSearchedUsername(username);
          
          // Open analysis result in new tab if scan was saved
          if (scanId) {
            const url = `${window.location.origin}/analysis/${scanId}`;
            window.open(url, '_blank');
          }
          
          console.log(`✅ Простой анализ завершен! Найдено ${result.trends.length} трендовых видео и ${result.hashtags.length} хештегов`);
        }
      }
      
    } catch (error) {
      console.error('❌ Ошибка анализа трендов:', error);
      const errorMessage = error instanceof Error ? error.message : 'Произошла неизвестная ошибка';
      setError(errorMessage);
    } finally {
      setLoading(false);
      // Reset progress after a short delay to allow UI to show completion
      setTimeout(() => {
        setProgress({
          stage: 'profile',
          message: '',
          percentage: 0,
          startTime: null,
        });
      }, 500);
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
      tokenUsage: null,
    });
    setProgress({
      stage: 'profile',
      message: '',
      percentage: 0,
      startTime: null,
    });
  }, []);

  /**
   * Load a saved analysis from history (FULL data: profile, trends, hashtags, etc.)
   */
  const loadSavedAnalysis = useCallback((analysisData: {
    profile: TikTokProfile;
    trends: any[];
    hashtags: any[];
    posts?: any[];
    tokenUsage?: any;
  }, username: string) => {
    try {
      console.log(`📂 Loading saved analysis: @${username}`);
      console.log(`📊 Restoring: ${analysisData.trends?.length || 0} trends, ${analysisData.hashtags?.length || 0} hashtags`);
      
      updateState({
        profile: analysisData.profile,
        posts: analysisData.posts || [],
        hashtags: analysisData.hashtags || [],
        trends: analysisData.trends || [],
        tokenUsage: analysisData.tokenUsage || null,
      });
      
      // Update last searched username
      saveLastSearchedUsername(username);
      setLastSearchedUsername(username);
      
      console.log(`✅ Saved analysis loaded successfully`);
    } catch (error) {
      console.error('Failed to load saved analysis:', error);
      setError('Failed to load saved analysis');
    }
  }, [updateState, setError]);

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
    loadSavedAnalysis,
    lastSearchedUsername,
  };
};

