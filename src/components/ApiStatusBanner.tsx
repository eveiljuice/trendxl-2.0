import React, { useEffect, useState } from 'react';
import { AlertTriangle, Wifi, WifiOff } from 'lucide-react';
import { checkBackendHealth } from '../services/backendApi';

const ApiStatusBanner: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline' | null>(null);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const checkApiStatus = async () => {
      setApiStatus('checking');
      
      try {
        const health = await checkBackendHealth();
        const isOnline = health.status === 'healthy' || health.status === 'degraded';
        setApiStatus(isOnline ? 'online' : 'offline');
        
        // Only show banner if API is offline
        if (!isOnline) {
          setShowBanner(true);
          // Auto-hide banner after 10 seconds
          setTimeout(() => setShowBanner(false), 10000);
        }
      } catch (error) {
        setApiStatus('offline');
        setShowBanner(true);
        setTimeout(() => setShowBanner(false), 10000);
      }
    };

    checkApiStatus();
  }, []);

  if (!showBanner || apiStatus !== 'offline') {
    return null;
  }

  return (
    <div className="relative">
      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-card p-4 mb-6 animate-slide-down">
        <div className="flex items-center gap-3">
          <WifiOff className="w-5 h-5 text-yellow-500 flex-shrink-0" />
          
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">
              API Currently Unavailable
            </p>
            <p className="text-xs text-yellow-600 dark:text-yellow-400">
              TikTok data API is not responding. You can still explore the app using demo profiles below.
            </p>
          </div>
          
          <button
            onClick={() => setShowBanner(false)}
            className="text-yellow-500 hover:text-yellow-600 transition-colors p-1 rounded"
            aria-label="Close banner"
          >
            ×
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApiStatusBanner;
