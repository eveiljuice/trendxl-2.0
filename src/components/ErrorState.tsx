import React from 'react';
import { AlertTriangle, RefreshCw, ArrowLeft, Sparkles } from 'lucide-react';
// DemoModePanel removed - no mock data allowed

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
  onReset?: () => void;
  onDemoProfile?: (profile: string) => void;
  isLoading?: boolean;
}

const ErrorState: React.FC<ErrorStateProps> = ({ 
  error, 
  onRetry, 
  onReset, 
  onDemoProfile, 
  isLoading = false 
}) => {
  return (
    <div className="section-spacing animate-fade-in">
      <div className="max-w-md mx-auto text-center">
        {/* Error Icon */}
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-500/10 rounded-full mb-6">
          <AlertTriangle className="w-8 h-8 text-red-400" />
        </div>

        {/* Error Message */}
        <h2 className="text-xl font-bold text-text-primary mb-2">
          Something went wrong
        </h2>
        <p className="text-text-secondary mb-8 leading-relaxed">
          {error}
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {onRetry && (
            <button
              onClick={onRetry}
              className="btn-primary flex items-center justify-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Try again</span>
            </button>
          )}
          
          {onReset && (
            <button
              onClick={onReset}
              className="
                px-6 py-3 
                bg-primary-card border border-primary-line rounded-btn
                text-text-primary hover:text-text-primary hover:border-primary-accent/30
                transition-all duration-150
                flex items-center justify-center space-x-2
              "
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Start over</span>
            </button>
          )}
        </div>

        {/* Help Text */}
        <div className="mt-8 p-4 bg-primary-card rounded-card border border-primary-line">
          <h3 className="text-sm font-medium text-text-primary mb-2">
            Common Issues & Solutions:
          </h3>
          <ul className="text-xs text-text-secondary space-y-1 text-left">
            <li>• <strong>Profile not found:</strong> Check if profile is public and URL is correct</li>
            <li>• <strong>Rate limit exceeded:</strong> Wait 5-10 minutes before trying again</li>
            <li>• <strong>API connection issues:</strong> Check internet connection and API keys</li>
            <li>• <strong>Protected profile:</strong> Some popular accounts may be protected from parsing</li>
            <li>• <strong>Regional restrictions:</strong> Profile might be restricted in your region</li>
          </ul>
          
          <div className="mt-3 text-xs text-text-tertiary">
            💡 <strong>Tip:</strong> Try using just the username (e.g., "zachking") instead of the full URL
          </div>
        </div>

        {/* Real data only - no demo mode */}
      </div>
    </div>
  );
};

export default ErrorState;
