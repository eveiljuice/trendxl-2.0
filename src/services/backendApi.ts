/**
 * Backend API Service - интеграция с новым Python бэкендом
 */
import axios from 'axios';
import { TikTokProfile, TikTokPost, TrendVideo } from '../types';

// Backend API configuration
// В production ВСЕГДА используем относительные пути (nginx прокси)
// В development можем использовать прямое подключение к backend

// Отладка: выводим информацию о переменных окружения
console.log('🔍 Environment Debug:', {
  VITE_BACKEND_API_URL: import.meta.env.VITE_BACKEND_API_URL,
  PROD: import.meta.env.PROD,
  DEV: import.meta.env.DEV,
  MODE: import.meta.env.MODE
});

// Принудительно используем пустую строку в production для относительных путей
const BACKEND_API_BASE_URL = import.meta.env.PROD 
  ? '' // В production ВСЕГДА используем относительные пути
  : (import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000');

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
    console.log('🚀 API Request:', {
      method: request.method?.toUpperCase(),
      url: request.url,
      baseURL: request.baseURL,
      fullURL: `${request.baseURL || ''}${request.url || ''}`
    });
    return request;
  });
  
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
