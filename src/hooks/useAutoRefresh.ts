import { useEffect, useRef } from 'react';

/**
 * Custom hook for automatic data refresh at specified interval
 * 
 * @param callback - Function to call on each refresh
 * @param interval - Refresh interval in milliseconds (default: 60000ms = 1 minute)
 * @param enabled - Whether auto-refresh is enabled
 */
export function useAutoRefresh(
  callback: () => void | Promise<void>,
  interval: number = 60000, // 1 minute default
  enabled: boolean = true
) {
  const savedCallback = useRef(callback);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);

  // Update callback ref when it changes
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    // Don't schedule if disabled
    if (!enabled) {
      return;
    }

    // Schedule the refresh
    const tick = async () => {
      try {
        await savedCallback.current();
      } catch (error) {
        console.error('Auto-refresh error:', error);
      }
      
      // Schedule next refresh
      timeoutIdRef.current = setTimeout(tick, interval);
    };

    // Start the first refresh
    timeoutIdRef.current = setTimeout(tick, interval);

    // Cleanup function
    return () => {
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
    };
  }, [interval, enabled]);
}

/**
 * Calculate time remaining until midnight UTC (free trial reset)
 * 
 * @returns Object with hours and minutes remaining
 */
export function calculateTimeUntilReset(): { hours: number; minutes: number; seconds: number } {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
  tomorrow.setUTCHours(0, 0, 0, 0);
  
  const diff = tomorrow.getTime() - now.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  
  return { hours, minutes, seconds };
}

/**
 * Format time remaining as a readable string
 * 
 * @param hours - Hours remaining
 * @param minutes - Minutes remaining
 * @returns Formatted string like "5h 30m"
 */
export function formatTimeRemaining(hours: number, minutes: number): string {
  return `${hours}h ${minutes}m`;
}

