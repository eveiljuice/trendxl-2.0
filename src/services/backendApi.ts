/**
 * Backend API Service - интеграция с новым Python бэкендом
 */
import axios from 'axios';
import { TikTokProfile, TikTokPost, TrendVideo } from '../types';

// Backend API configuration
const BACKEND_API_BASE_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000';

// Create axios instance for backend API
const createBackendClient = () => {
  return axios.create({
    baseURL: BACKEND_API_BASE_URL,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    timeout: 60000, // 60 seconds timeout for analysis
  });
};

/**
 * Analyze TikTok profile trends using Python backend
 */
export async function analyzeProfileTrends(profileUrl: string): Promise<{
  profile: TikTokProfile;
  posts: TikTokPost[];
  hashtags: string[];
  trends: TrendVideo[];
  analysis_summary: string;
}> {
  try {
    const client = createBackendClient();
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
