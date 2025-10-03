import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getTokenUsageSummary, getTokenUsageByPeriod } from '../services/backendApi';

interface TokenSummary {
  total_analyses: number;
  total_openai_tokens: number;
  total_openai_prompt: number;
  total_openai_completion: number;
  total_perplexity_tokens: number;
  total_perplexity_prompt: number;
  total_perplexity_completion: number;
  total_ensemble_units: number;
  total_cost: number;
  first_analysis: string | null;
  last_analysis: string | null;
}

interface PeriodUsage {
  period_days: number;
  analyses_count: number;
  openai_tokens: number;
  perplexity_tokens: number;
  ensemble_units: number;
  total_cost: number;
}

export default function UserTokenUsagePanel() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<TokenSummary | null>(null);
  const [periodUsage, setPeriodUsage] = useState<PeriodUsage | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user && user.token) {
      loadUsageData();
    }
  }, [user, selectedPeriod]);

  const loadUsageData = async () => {
    if (!user?.token) return;

    setLoading(true);
    setError(null);

    try {
      const [summaryData, periodData] = await Promise.all([
        getTokenUsageSummary(user.token),
        getTokenUsageByPeriod(user.token, selectedPeriod)
      ]);

      setSummary(summaryData);
      setPeriodUsage(periodData);
    } catch (err: any) {
      console.error('Failed to load token usage:', err);
      setError(err.message || 'Failed to load token usage data');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number | null | undefined) => {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString();
  };

  const formatCost = (cost: number | null | undefined) => {
    if (cost === null || cost === undefined) return '0.0000';
    return cost.toFixed(4);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    try {
      return new Date(dateStr).toLocaleDateString();
    } catch {
      return 'N/A';
    }
  };

  if (!user) {
    return (
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-8 text-center border border-purple-200 dark:border-purple-700">
        <div className="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
          Sign In Required
        </h3>
        <p className="text-gray-600 dark:text-gray-300">
          Sign in to view your API usage statistics and manage your subscription.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <span className="text-gray-600 dark:text-gray-300">Loading usage data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 rounded-xl p-6 border border-red-200 dark:border-red-700">
        <div className="flex items-center space-x-3">
          <svg className="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="font-semibold text-red-900 dark:text-red-200">Error Loading Data</h3>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">API Usage & Subscription</h2>
            <p className="text-purple-100">Track your token usage and plan your subscription</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-purple-100">Member since</div>
            <div className="font-semibold">{formatDate(summary?.first_analysis || null)}</div>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Analyses */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Analyses</span>
            <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-gray-900 dark:text-white">
            {formatNumber(summary?.total_analyses)}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Last: {formatDate(summary?.last_analysis || null)}
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-5 border border-green-200 dark:border-green-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Cost</span>
            <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="text-3xl font-bold text-green-700 dark:text-green-400">
            ${formatCost(summary?.total_cost)}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            All time estimated
          </div>
        </div>

        {/* OpenAI Tokens */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">OpenAI Tokens</span>
            <div className="w-5 h-5 bg-green-500 rounded flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.051 6.051 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729z"/>
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatNumber(summary?.total_openai_tokens)}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {formatNumber(summary?.total_openai_prompt)} in / {formatNumber(summary?.total_openai_completion)} out
          </div>
        </div>

        {/* Perplexity Tokens */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Perplexity</span>
            <div className="w-5 h-5 bg-blue-500 rounded flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {formatNumber(summary?.total_perplexity_tokens)}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {formatNumber(summary?.total_perplexity_prompt)} in / {formatNumber(summary?.total_perplexity_completion)} out
          </div>
        </div>
      </div>

      {/* Period Stats */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            Usage by Period
          </h3>
          <div className="flex gap-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setSelectedPeriod(days)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedPeriod === days
                    ? 'bg-purple-500 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {days} days
              </button>
            ))}
          </div>
        </div>

        {periodUsage && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Analyses</div>
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {formatNumber(periodUsage.analyses_count)}
              </div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">OpenAI</div>
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {formatNumber(periodUsage.openai_tokens)}
              </div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Perplexity</div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {formatNumber(periodUsage.perplexity_tokens)}
              </div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Ensemble Units</div>
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {formatNumber(periodUsage.ensemble_units)}
              </div>
            </div>

            <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg">
              <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Cost</div>
              <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                ${formatCost(periodUsage.total_cost)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Subscription CTA */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold mb-2">Ready to upgrade?</h3>
            <p className="text-purple-100">
              Get unlimited analyses and access to advanced features with our subscription plans.
            </p>
          </div>
          <button className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors">
            View Plans
          </button>
        </div>
      </div>
    </div>
  );
}

