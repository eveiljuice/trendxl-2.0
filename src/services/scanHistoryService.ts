/**
 * Scan History Service
 * Handles saving and retrieving TikTok profile scan history
 */

import { supabase } from '@/lib/supabase';
import { TikTokProfile } from '@/types';

export interface ScanHistoryItem {
  id: string;
  user_id: string;
  username: string;
  profile_data: {
    profile: TikTokProfile;
    trends: any[];
    hashtags: any[];
    posts: any[];
    tokenUsage?: any;
  };
  scan_type: 'free' | 'paid';
  created_at: string;
  updated_at: string;
}

/**
 * Save a scan to history with full analysis data
 * Returns the ID of the created scan
 */
export async function saveScanToHistory(
  username: string,
  analysisData: {
    profile: TikTokProfile;
    trends: any[];
    hashtags: any[];
    posts?: any[];
    tokenUsage?: any;
  },
  scanType: 'free' | 'paid' = 'free'
): Promise<string | null> {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      console.warn('User not authenticated, cannot save scan history');
      return null;
    }

    const { data, error } = await supabase
      .from('scan_history')
      .insert({
        user_id: user.id,
        username,
        profile_data: analysisData,
        scan_type: scanType,
      })
      .select('id')
      .single();

    if (error) {
      console.error('Error saving scan to history:', error);
      throw error;
    }

    console.log(`✅ Scan saved to history: @${username} (${scanType} scan, ${analysisData.trends?.length || 0} trends, ${analysisData.hashtags?.length || 0} hashtags)`);
    
    return data?.id || null;
  } catch (error) {
    console.error('Failed to save scan to history:', error);
    // Don't throw - this is a non-critical operation
    return null;
  }
}

/**
 * Get user's scan history
 */
export async function getScanHistory(): Promise<ScanHistoryItem[]> {
  try {
    const { data, error } = await supabase
      .from('scan_history')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error loading scan history:', error);
      throw error;
    }

    return data || [];
  } catch (error) {
    console.error('Failed to load scan history:', error);
    throw error;
  }
}

/**
 * Get a single scan by ID
 */
export async function getScanById(scanId: string): Promise<ScanHistoryItem | null> {
  try {
    const { data, error } = await supabase
      .from('scan_history')
      .select('*')
      .eq('id', scanId)
      .single();

    if (error) {
      console.error('Error loading scan:', error);
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Failed to load scan:', error);
    throw error;
  }
}

/**
 * Delete a scan from history
 */
export async function deleteScanFromHistory(scanId: string): Promise<void> {
  try {
    const { error } = await supabase
      .from('scan_history')
      .delete()
      .eq('id', scanId);

    if (error) {
      console.error('Error deleting scan from history:', error);
      throw error;
    }

    console.log(`✅ Scan deleted from history: ${scanId}`);
  } catch (error) {
    console.error('Failed to delete scan from history:', error);
    throw error;
  }
}

/**
 * Get the last searched username for the current user
 */
export function getLastSearchedUsername(): string | null {
  return localStorage.getItem('last_searched_username');
}

/**
 * Save the last searched username
 */
export function saveLastSearchedUsername(username: string): void {
  localStorage.setItem('last_searched_username', username);
}

/**
 * Clear the last searched username
 */
export function clearLastSearchedUsername(): void {
  localStorage.removeItem('last_searched_username');
}

