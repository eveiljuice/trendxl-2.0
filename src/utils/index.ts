/**
 * Extract username from TikTok URL or return as-is if it's already a username
 * Handles all known TikTok URL formats including short links and regional domains
 */
export function extractTikTokUsername(input: string): string {
  // Remove whitespace and normalize
  const cleaned = input.trim();
  
  // If it's already a username (no URL format), return as-is
  if (!cleaned.includes('/') && !cleaned.includes('tiktok') && !cleaned.includes('.com')) {
    return cleaned.replace('@', ''); // Remove @ if present
  }
  
  // Handle various TikTok URL formats with comprehensive patterns
  const patterns = [
    // Standard TikTok URLs
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([a-zA-Z0-9._-]+)/,     // @username format
    /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/([a-zA-Z0-9._-]+)(?=\/|$|\?)/,  // direct username
    
    // Short link domains
    /(?:https?:\/\/)?vm\.tiktok\.com\/([a-zA-Z0-9]+)/,              // vm.tiktok.com/shortcode
    /(?:https?:\/\/)?vt\.tiktok\.com\/([a-zA-Z0-9]+)/,              // vt.tiktok.com/shortcode  
    /(?:https?:\/\/)?t\.tiktok\.com\/([a-zA-Z0-9]+)/,               // t.tiktok.com/shortcode
    
    // Regional TikTok domains
    /(?:https?:\/\/)?(?:www\.)?tiktok\.co\.uk\/@([a-zA-Z0-9._-]+)/, // UK domain
    /(?:https?:\/\/)?(?:www\.)?tiktok\.de\/@([a-zA-Z0-9._-]+)/,     // German domain
    /(?:https?:\/\/)?(?:www\.)?tiktok\.fr\/@([a-zA-Z0-9._-]+)/,     // French domain
    /(?:https?:\/\/)?(?:www\.)?tiktok\.it\/@([a-zA-Z0-9._-]+)/,     // Italian domain
    /(?:https?:\/\/)?(?:www\.)?tiktok\.es\/@([a-zA-Z0-9._-]+)/,     // Spanish domain
    
    // Mobile app deep links
    /tiktok:\/\/user\/@([a-zA-Z0-9._-]+)/,                          // Mobile app deep link
    
    // User profile URLs with additional paths
    /tiktok\.com\/@([a-zA-Z0-9._-]+)\/video\/[\d]+/,                // Profile with specific video
    /tiktok\.com\/@([a-zA-Z0-9._-]+)\/live/,                        // Live stream URL
  ];
  
  // Try each pattern
  for (const pattern of patterns) {
    const match = cleaned.match(pattern);
    if (match && match[1]) {
      // Clean the extracted username
      let username = match[1];
      
      // Remove any trailing slashes or parameters
      username = username.split('?')[0].split('#')[0].split('/')[0];
      
      // Validate username format
      if (isValidUsernameFormat(username)) {
        return username;
      }
    }
  }
  
  // Handle edge cases - try to extract from path segments
  try {
    const url = new URL(cleaned.startsWith('http') ? cleaned : 'https://' + cleaned);
    const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
    
    for (const segment of pathSegments) {
      const cleanSegment = segment.replace('@', '');
      if (isValidUsernameFormat(cleanSegment) && cleanSegment !== 'user' && cleanSegment !== 'profile') {
        return cleanSegment;
      }
    }
  } catch (urlError) {
    // Continue with fallback logic
  }
  
  // Last resort: extract anything that looks like a username
  const lastSlashIndex = cleaned.lastIndexOf('/');
  if (lastSlashIndex !== -1) {
    const potential = cleaned.substring(lastSlashIndex + 1);
    const cleaned_potential = potential.split('?')[0].split('#')[0].replace('@', '');
    
    if (isValidUsernameFormat(cleaned_potential)) {
      return cleaned_potential;
    }
  }
  
  // Final fallback: return cleaned input if it looks like a valid username
  const finalClean = cleaned.replace('@', '').replace(/^https?:\/\//, '').replace(/^www\./, '');
  return isValidUsernameFormat(finalClean) ? finalClean : cleaned.replace('@', '');
}

/**
 * Validate if a string could be a valid TikTok username
 */
function isValidUsernameFormat(username: string): boolean {
  if (!username || username.length === 0) return false;
  if (username.length > 24) return false; // TikTok username max length
  
  // TikTok usernames can contain letters, numbers, underscores, and dots
  // Must start with a letter or number
  const usernameRegex = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,23}$/;
  return usernameRegex.test(username);
}

/**
 * Format number with K/M suffixes for better readability
 */
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

/**
 * Format date to relative time (e.g., "2 days ago")
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  const intervals = [
    { label: 'год', seconds: 31536000 },
    { label: 'месяц', seconds: 2592000 },
    { label: 'день', seconds: 86400 },
    { label: 'час', seconds: 3600 },
    { label: 'минуту', seconds: 60 },
  ];
  
  for (const interval of intervals) {
    const count = Math.floor(diffInSeconds / interval.seconds);
    if (count > 0) {
      return `${count} ${interval.label}${count > 1 ? (interval.label === 'час' ? 'а' : interval.label === 'день' ? 'я' : interval.label === 'месяц' ? 'а' : interval.label === 'год' ? 'а' : 'ы') : (interval.label === 'минуту' ? 'у' : '')} назад`;
    }
  }
  
  return 'только что';
}

/**
 * Validate TikTok URL or username
 */
export function isValidTikTokInput(input: string): boolean {
  if (!input || input.trim().length === 0) {
    return false;
  }
  
  const cleaned = input.trim();
  
  // Check if it's a valid TikTok URL
  const urlPatterns = [
    /^https?:\/\/(www\.)?tiktok\.com\/@[a-zA-Z0-9._-]+/,
    /^https?:\/\/(vm|vt)\.tiktok\.com\/[a-zA-Z0-9]+/,
  ];
  
  if (urlPatterns.some(pattern => pattern.test(cleaned))) {
    return true;
  }
  
  // Check if it's a valid username (alphanumeric, dots, underscores, hyphens)
  const usernamePattern = /^@?[a-zA-Z0-9._-]{1,24}$/;
  return usernamePattern.test(cleaned);
}

/**
 * Truncate text to specified length with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Generate a random delay for staggered animations
 */
export function getStaggerDelay(index: number, baseDelay: number = 100): number {
  return index * baseDelay;
}

/**
 * Sleep utility for async operations
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Advanced retry logic with exponential backoff for API calls
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    baseDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    retryCondition?: (error: any) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    backoffFactor = 2,
    retryCondition = (error) => {
      // Retry on network errors, rate limits, and temporary server errors
      if (error?.response?.status) {
        const status = error.response.status;
        return status === 429 || status === 502 || status === 503 || status === 504;
      }
      return error?.code === 'ECONNRESET' || error?.code === 'ETIMEDOUT';
    }
  } = options;

  let lastError: any;
  
  for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on last attempt
      if (attempt > maxRetries) {
        break;
      }
      
      // Check if we should retry this error
      if (!retryCondition(error)) {
        break;
      }
      
      // Calculate delay with exponential backoff
      const delay = Math.min(
        baseDelay * Math.pow(backoffFactor, attempt - 1),
        maxDelay
      );
      
      // Add jitter to prevent thundering herd
      const jitterDelay = delay + Math.random() * 1000;
      
      console.warn(`API call failed (attempt ${attempt}/${maxRetries + 1}), retrying in ${Math.round(jitterDelay)}ms:`, error);
      
      await sleep(jitterDelay);
    }
  }
  
  throw lastError;
}

/**
 * Generate rotating User-Agent strings to mimic different browsers
 */
/**
 * Simple in-memory cache for API responses
 */
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number; // Time to live in milliseconds
}

class SimpleCache {
  private cache = new Map<string, CacheEntry<any>>();

  set<T>(key: string, data: T, ttlMinutes: number = 15): void {
    const ttl = ttlMinutes * 60 * 1000; // Convert to milliseconds
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    });
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  clear(): void {
    this.cache.clear();
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  size(): number {
    // Clean expired entries
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
      }
    }
    return this.cache.size;
  }
}

// Global cache instance
export const apiCache = new SimpleCache();

/**
 * Wrapper for cached API calls
 */
export async function withCache<T>(
  cacheKey: string,
  apiCall: () => Promise<T>,
  ttlMinutes: number = 15
): Promise<T> {
  // Try to get from cache first
  const cached = apiCache.get<T>(cacheKey);
  if (cached) {
    console.log(`🎯 Cache hit for key: ${cacheKey}`);
    return cached;
  }

  // If not in cache, make API call
  console.log(`🌐 Cache miss, making API call for key: ${cacheKey}`);
  const result = await apiCall();
  
  // Store in cache
  apiCache.set(cacheKey, result, ttlMinutes);
  
  return result;
}

export function getRandomUserAgent(): string {
  const userAgents = [
    // Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    // Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    // Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
    
    // Firefox on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
    
    // Safari on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    
    // Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
  ];
  
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}
