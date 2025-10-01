/**
 * Backend API Service - интеграция с новым Python бэкендом
 */
import axios from 'axios';
import { TikTokProfile, TikTokPost, TrendVideo, CreativeCenterHashtag, NicheHashtagResponse, CreativeCenterAnalysisRequest, CreativeCenterAnalysisResponse } from '../types';

// Backend API configuration
// В production используем отдельный Railway backend service
// В development используем localhost

// Отладка: выводим информацию о переменных окружения
console.log('🔍 Environment Debug:', {
  VITE_BACKEND_API_URL: import.meta.env.VITE_BACKEND_API_URL,
  PROD: import.meta.env.PROD,
  DEV: import.meta.env.DEV,
  MODE: import.meta.env.MODE
});

// В production используем Railway backend URL, в dev - localhost
const BACKEND_API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';

// Отладка: выводим финальный URL
console.log('🌐 Final API Base URL:', BACKEND_API_BASE_URL);

// Create axios instance for backend API
const createBackendClient = (customTimeout?: number) => {
  const client = axios.create({
    baseURL: BACKEND_API_BASE_URL,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    timeout: customTimeout || 180000, // 3 minutes default timeout
  });
  
  // Отладочный interceptor для логирования запросов
  client.interceptors.request.use(request => {
    const fullURL = `${request.baseURL || ''}${request.url || ''}`;
    console.log('🚀 API Request:', {
      method: request.method?.toUpperCase(),
      url: request.url,
      baseURL: request.baseURL,
      fullURL: fullURL,
      timestamp: new Date().toISOString()
    });
    return request;
  });
  
  // Отладочный interceptor для логирования ответов
  client.interceptors.response.use(
    response => {
      console.log('✅ API Success:', {
        status: response.status,
        statusText: response.statusText,
        url: response.config.url,
        data: typeof response.data === 'object' ? Object.keys(response.data) : response.data,
        timestamp: new Date().toISOString()
      });
      return response;
    },
    error => {
      const errorInfo = {
        message: error.message,
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        statusText: error.response?.statusText,
        responseData: error.response?.data,
        timestamp: new Date().toISOString()
      };
      
      console.error('❌ API Error:', errorInfo);
      
      // Специальная обработка для разных типов ошибок
      if (error.code === 'ECONNREFUSED') {
        console.error('🔌 Connection refused - backend not responding');
      } else if (error.response?.status === 502) {
        console.error('🌐 Bad Gateway - nginx cannot reach backend');
      } else if (error.response?.status === 503) {
        console.error('🚫 Service Unavailable - backend service down');
      } else if (error.response?.status === 0) {
        console.error('🌐 Network error - no response from server');
      }
      
      return Promise.reject(error);
    }
  );
  
  return client;
};

/**
 * Analyze TikTok profile trends using Python backend
 */
export async function analyzeProfileTrends(
  profileUrl: string, 
  onProgress?: (stage: string, message: string) => void
): Promise<{
  profile: TikTokProfile;
  posts: TikTokPost[];
  hashtags: string[];
  trends: TrendVideo[];
  analysis_summary: string;
}> {
  try {
    // Use 5-minute timeout for full analysis
    const client = createBackendClient(300000);
    
    // Notify progress start
    onProgress?.('profile', 'Connecting to TikTok API...');
    
    const response = await client.post('/api/v1/analyze', {
      profile_url: profileUrl
    });
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (analyze):', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Profile not found or unavailable');
      } else if (error.response?.status === 429) {
        throw new Error('Too many requests. Please try again later');
      } else if (error.response?.status === 503) {
        throw new Error('Backend service temporarily unavailable');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error('Failed to analyze profile trends');
  }
}

/**
 * Analyze TikTok profile trends with step-by-step progress tracking
 */
export async function analyzeProfileTrendsWithProgress(
  profileUrl: string, 
  onProgress?: (stage: string, message: string, percentage: number) => void
): Promise<{
  profile: TikTokProfile;
  posts: TikTokPost[];
  hashtags: string[];
  trends: TrendVideo[];
  analysis_summary: string;
}> {
  try {
    const username = profileUrl.replace(/@/g, '').replace('https://www.tiktok.com/@', '');
    const client = createBackendClient(300000); // 5-minute timeout
    
    // Step 1: Get profile (20% progress)
    onProgress?.('profile', 'Loading TikTok profile data...', 10);
    const profile = await getTikTokProfile(username);
    onProgress?.('profile', `Profile @${username} loaded successfully`, 20);
    
    // Step 2: Get posts (40% progress) 
    onProgress?.('posts', 'Collecting latest videos and statistics...', 25);
    const postsResult = await getTikTokPosts(username, 20);
    onProgress?.('posts', `Found ${postsResult.posts.length} recent videos`, 40);
    
    // Step 3: AI analysis (60% progress)
    onProgress?.('analysis', 'AI analyzing content for hashtags...', 45);
    
    // Simulate AI analysis delay and call full analyze for AI part
    await new Promise(resolve => setTimeout(resolve, 2000));
    const response = await client.post('/api/v1/analyze', {
      profile_url: profileUrl
    });
    
    onProgress?.('analysis', `GPT-4o extracted ${response.data.hashtags?.length || 0} key hashtags`, 60);
    
    // Step 4: Find trends (100% progress)
    onProgress?.('trends', 'Searching for trending videos by hashtags...', 70);
    await new Promise(resolve => setTimeout(resolve, 3000)); // Allow backend to process
    onProgress?.('trends', `Found ${response.data.trends?.length || 0} trending videos`, 90);
    
    onProgress?.('trends', 'Analysis completed successfully!', 100);
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (step-by-step analyze):', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('Profile not found or unavailable');
      } else if (error.response?.status === 429) {
        throw new Error('Too many requests. Please try again later');
      } else if (error.response?.status === 503) {
        throw new Error('Backend service temporarily unavailable');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error('Failed to analyze profile trends');
  }
}

/**
 * Get TikTok user profile information
 */
export async function getTikTokProfile(username: string): Promise<TikTokProfile> {
  try {
    const client = createBackendClient();
    const response = await client.post('/api/v1/profile', {
      username: username.replace('@', '')
    });
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (profile):', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error(`Profile @${username} not found`);
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error(`Failed to get profile @${username}`);
  }
}

/**
 * Get TikTok user posts
 */
export async function getTikTokPosts(
  username: string, 
  count: number = 20, 
  cursor?: string
): Promise<{ posts: TikTokPost[], cursor?: string }> {
  try {
    const client = createBackendClient();
    const response = await client.post('/api/v1/posts', {
      username: username.replace('@', ''),
      count,
      cursor
    });
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (posts):', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error(`Posts for @${username} not found`);
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error(`Failed to get posts for @${username}`);
  }
}

/**
 * Search TikTok posts by hashtag
 */
export async function searchHashtagPosts(
  hashtag: string,
  count: number = 10,
  period: number = 7,
  sorting: number = 1
): Promise<{ posts: TikTokPost[], cursor?: string, total?: number }> {
  try {
    const client = createBackendClient();
    const response = await client.post('/api/v1/hashtag/search', {
      hashtag: hashtag.replace('#', ''),
      count,
      period,
      sorting
    });
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (hashtag search):', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error(`No posts found for #${hashtag}`);
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error(`Failed to search hashtag #${hashtag}`);
  }
}

/**
 * Search TikTok users
 */
export async function searchTikTokUsers(
  query: string,
  count: number = 10
): Promise<{ users: TikTokProfile[] }> {
  try {
    const client = createBackendClient();
    const response = await client.post('/api/v1/users/search', {
      query,
      count
    });
    
    return response.data;
  } catch (error) {
    console.error('Backend API error (user search):', error);
    
    if (axios.isAxiosError(error) && error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    
    throw new Error(`Failed to search users with query: "${query}"`);
  }
}

/**
 * Check backend health
 */
export async function checkBackendHealth(): Promise<{
  status: string;
  services: Record<string, boolean>;
}> {
  try {
    const client = createBackendClient();
    const response = await client.get('/health');
    
    return response.data;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return {
      status: 'unhealthy',
      services: {
        backend: false,
        cache: false,
        ensemble_api: false,
        openai_api: false
      }
    };
  }
}

/**
 * Get cache statistics
 */
export async function getCacheStats(): Promise<any> {
  try {
    const client = createBackendClient();
    const response = await client.get('/api/v1/cache/stats');
    
    return response.data;
  } catch (error) {
    console.error('Cache stats error:', error);
    return null;
  }
}

/**
 * Clear cache
 */
export async function clearCache(pattern: string = '*'): Promise<any> {
  try {
    const client = createBackendClient();
    const response = await client.post('/api/v1/cache/clear', null, {
      params: { pattern }
    });
    
    return response.data;
  } catch (error) {
    console.error('Cache clear error:', error);
    throw new Error('Failed to clear cache');
  }
}

/**
 * Discover Creative Center hashtags for a specific niche using Perplexity AI
 */
export async function discoverCreativeCenterHashtags(
  niche: string,
  country: string = 'US',
  language: string = 'en',
  limit: number = 10,
  autoDetectGeo: boolean = false,
  profileData?: any
): Promise<NicheHashtagResponse> {
  try {
    const client = createBackendClient(120000); // 2-minute timeout for AI research
    
    console.log(`🔍 Discovering Creative Center hashtags for niche: ${niche}`);
    
    const response = await client.post('/api/v1/creative-center/hashtags', {
      niche,
      country,
      language,
      limit,
      auto_detect_geo: autoDetectGeo,
      profile_data: profileData
    });
    
    console.log(`✅ Found ${response.data.hashtags?.length || 0} Creative Center hashtags`);
    
    return response.data;
  } catch (error) {
    console.error('Creative Center hashtag discovery error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 503) {
        throw new Error('Perplexity API key is not configured. Please check your backend configuration.');
      } else if (error.response?.status === 500) {
        throw new Error('Creative Center discovery failed. Please try again later.');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error(`Failed to discover hashtags for niche: "${niche}"`);
  }
}

/**
 * Complete Creative Center + Ensemble Data analysis
 * This implements the advanced architecture with step-by-step navigation
 */
export async function analyzeCreativeCenterComplete(
  profileUrl: string,
  country: string = 'US',
  language: string = 'en',
  hashtagLimit: number = 5,
  videosPerHashtag: number = 3,
  autoDetectGeo: boolean = true,
  onProgress?: (stage: string, message: string, percentage: number) => void
): Promise<CreativeCenterAnalysisResponse> {
  try {
    const client = createBackendClient(300000); // 5-minute timeout for complete analysis
    
    console.log(`🚀 Starting complete Creative Center analysis for: ${profileUrl}`);
    
    // Notify progress start
    onProgress?.('discovery', 'Analyzing user profile and niche...', 10);
    
    const requestData: CreativeCenterAnalysisRequest = {
      profile_url: profileUrl,
      country,
      language,
      hashtag_limit: hashtagLimit,
      videos_per_hashtag: videosPerHashtag,
      auto_detect_geo: autoDetectGeo
    };
    
    // Step progress notifications
    onProgress?.('navigation', 'AI agent navigating Creative Center...', 25);
    
    const response = await client.post('/api/v1/analyze-creative-center', requestData);
    
    onProgress?.('analysis', 'Analyzing trending videos via Ensemble Data...', 70);
    
    // Simulate processing time for user feedback
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    onProgress?.('completion', 'Analysis completed successfully!', 100);
    
    const result: CreativeCenterAnalysisResponse = response.data;
    
    console.log(`✅ Complete Creative Center analysis finished:`);
    console.log(`   - Profile: @${result.profile.username}`);
    console.log(`   - Creative Center hashtags: ${result.creative_center_hashtags.length}`);
    console.log(`   - Trending videos: ${result.trends.length}`);
    console.log(`   - Category: ${result.metadata.creative_center_category}`);
    
    return result;
    
  } catch (error) {
    console.error('Complete Creative Center analysis error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        throw new Error('No relevant Creative Center hashtags found for this profile\'s niche');
      } else if (error.response?.status === 503) {
        throw new Error('Perplexity API key is not configured. Please check your backend configuration.');
      } else if (error.response?.status === 500) {
        throw new Error('Creative Center analysis failed. Please try again later.');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error(`Failed to analyze Creative Center for profile: "${profileUrl}"`);
  }
}

/**
 * Get token usage summary for the current user
 */
export async function getTokenUsageSummary(authToken: string): Promise<any> {
  try {
    const client = createBackendClient();
    const response = await client.get('/api/v1/usage/summary', {
      headers: {
        Authorization: `Bearer ${authToken}`
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Token usage summary error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error('Failed to get token usage summary');
  }
}

/**
 * Get detailed token usage history for the current user
 */
export async function getTokenUsageHistory(
  authToken: string,
  limit: number = 50,
  offset: number = 0
): Promise<any> {
  try {
    const client = createBackendClient();
    const response = await client.get('/api/v1/usage/history', {
      headers: {
        Authorization: `Bearer ${authToken}`
      },
      params: {
        limit,
        offset
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Token usage history error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error('Failed to get token usage history');
  }
}

/**
 * Get token usage for a specific period
 */
export async function getTokenUsageByPeriod(
  authToken: string,
  periodDays: number = 30
): Promise<any> {
  try {
    const client = createBackendClient();
    const response = await client.get('/api/v1/usage/period', {
      headers: {
        Authorization: `Bearer ${authToken}`
      },
      params: {
        period_days: periodDays
      }
    });
    
    return response.data.data;
  } catch (error) {
    console.error('Token usage by period error:', error);
    
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        throw new Error('Authentication required');
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error);
      }
    }
    
    throw new Error('Failed to get token usage by period');
  }
}
