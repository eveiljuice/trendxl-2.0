import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Loader, Info } from 'lucide-react';
import { checkBackendHealth, getCacheStats } from '../services/backendApi';

interface DiagnosticResult {
  service: string;
  status: 'loading' | 'success' | 'error' | 'unknown';
  message: string;
  details?: string;
}

const DiagnosticPanel: React.FC = () => {
  const [results, setResults] = useState<DiagnosticResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const runDiagnostics = async () => {
    setIsRunning(true);
    setResults([
      { service: 'Python Backend', status: 'loading', message: 'Testing backend connection...' },
      { service: 'Redis Cache', status: 'loading', message: 'Checking cache status...' },
      { service: 'Ensemble API', status: 'loading', message: 'Testing TikTok API...' },
      { service: 'OpenAI API', status: 'loading', message: 'Testing AI service...' },
    ]);

    const updatedResults: DiagnosticResult[] = [];

    // Test Backend Health
    try {
      const health = await checkBackendHealth();
      const backendOnline = health.status === 'healthy' || health.status === 'degraded';
      
      updatedResults.push({
        service: 'Python Backend',
        status: backendOnline ? 'success' : 'error',
        message: backendOnline ? `Backend ${health.status}` : 'Backend offline',
        details: backendOnline 
          ? 'Python FastAPI backend is responding normally'
          : 'Check if backend server is running: cd backend && python run_server.py'
      });

      // Test individual services through backend
      if (backendOnline) {
        // Redis Cache
        updatedResults.push({
          service: 'Redis Cache',
          status: health.services.cache ? 'success' : 'error',
          message: health.services.cache ? 'Cache operational' : 'Cache unavailable',
          details: health.services.cache 
            ? 'Redis cache is working - API responses will be cached for better performance'
            : 'Redis connection failed - check if Redis server is running'
        });

        // Ensemble API
        updatedResults.push({
          service: 'Ensemble API',
          status: health.services.ensemble_api ? 'success' : 'error',
          message: health.services.ensemble_api ? 'TikTok API ready' : 'TikTok API unavailable',
          details: health.services.ensemble_api 
            ? 'Ensemble Data API is ready to fetch TikTok profiles and posts'
            : 'Check backend API token configuration'
        });

        // OpenAI API
        updatedResults.push({
          service: 'OpenAI API',
          status: health.services.openai_api ? 'success' : 'error',
          message: health.services.openai_api ? 'AI analysis ready' : 'AI service unavailable',
          details: health.services.openai_api 
            ? 'OpenAI GPT-4 is ready to analyze posts and extract hashtags'
            : 'Check backend OpenAI API key configuration'
        });
      } else {
        // Mark all services as unknown if backend is offline
        ['Redis Cache', 'Ensemble API', 'OpenAI API'].forEach(serviceName => {
          updatedResults.push({
            service: serviceName,
            status: 'unknown',
            message: 'Cannot test - backend offline',
            details: 'Backend connection required to test this service'
          });
        });
      }

    } catch (error) {
      updatedResults.push({
        service: 'Python Backend',
        status: 'error',
        message: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Make sure backend is running on port 8000'
      });
      
      // Mark all services as unknown
      ['Redis Cache', 'Ensemble API', 'OpenAI API'].forEach(serviceName => {
        updatedResults.push({
          service: serviceName,
          status: 'unknown',
          message: 'Cannot test - backend offline',
          details: 'Backend connection required to test this service'
        });
      });
    }

    setResults(updatedResults);
    setIsRunning(false);
  };

  const getStatusIcon = (status: DiagnosticResult['status']) => {
    switch (status) {
      case 'loading':
        return <Loader className="w-4 h-4 animate-spin text-blue-400" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getStatusColor = (status: DiagnosticResult['status']) => {
    switch (status) {
      case 'success':
        return 'border-green-500/30 bg-green-500/5';
      case 'error':
        return 'border-red-500/30 bg-red-500/5';
      case 'loading':
        return 'border-blue-500/30 bg-blue-500/5';
      default:
        return 'border-yellow-500/30 bg-yellow-500/5';
    }
  };

  return (
    <div className="p-6 bg-primary-card rounded-card border border-primary-line">
      <div className="flex items-center gap-3 mb-4">
        <Info className="w-5 h-5 text-text-secondary" />
        <h3 className="text-lg font-semibold text-text-primary">System Diagnostics</h3>
      </div>

      <p className="text-sm text-text-secondary mb-4">
        Test all system components to identify potential issues with TikTok profile scanning.
      </p>

      <button
        onClick={runDiagnostics}
        disabled={isRunning}
        className={`
          mb-6 px-4 py-2 rounded-btn font-medium transition-all duration-150
          ${isRunning 
            ? 'bg-primary-card border border-primary-line text-text-secondary cursor-not-allowed'
            : 'bg-primary-accent text-white hover:bg-primary-accent/90'
          }
        `}
      >
        {isRunning ? (
          <>
            <Loader className="w-4 h-4 animate-spin inline mr-2" />
            Running Diagnostics...
          </>
        ) : (
          'Run System Diagnostics'
        )}
      </button>

      {results.length > 0 && (
        <div className="space-y-3">
          {results.map((result, index) => (
            <div
              key={index}
              className={`
                p-4 rounded-card border transition-all duration-300
                ${getStatusColor(result.status)}
              `}
            >
              <div className="flex items-center gap-3 mb-2">
                {getStatusIcon(result.status)}
                <span className="font-medium text-text-primary">{result.service}</span>
              </div>
              
              <p className="text-sm text-text-secondary mb-1">{result.message}</p>
              
              {result.details && (
                <p className="text-xs text-text-tertiary italic">{result.details}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {results.length > 0 && !isRunning && (
        <div className="mt-6 p-4 bg-primary-background rounded-card border border-primary-line">
          <h4 className="font-medium text-text-primary mb-2">Troubleshooting Tips:</h4>
          <ul className="text-xs text-text-secondary space-y-1">
            <li>• If backend fails: Make sure Python backend is running on port 8000</li>
            <li>• If cache fails: Check if Redis server is running</li>
            <li>• If API services fail: Check backend logs for API key configuration</li>
            <li>• For 429 errors: Backend handles rate limiting automatically</li>
            <li>• For profile not found: Try a different TikTok profile URL</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default DiagnosticPanel;
