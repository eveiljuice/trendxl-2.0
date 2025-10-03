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
    <div className="section-spacing animate-fade-in px-4 sm:px-6">
      <div className="max-w-md mx-auto text-center">
        {/* Error Icon - адаптивные размеры */}
        <div className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-red-500/10 rounded-full mb-4 sm:mb-6">
          <AlertTriangle className="w-7 h-7 sm:w-8 sm:h-8 text-red-400" />
        </div>

        {/* Error Message - адаптивные размеры */}
        <h2 className="text-lg sm:text-xl font-bold text-text-primary mb-2">
          Something went wrong
        </h2>
        <p className="text-sm sm:text-base text-content-subtitle mb-6 sm:mb-8 leading-relaxed">
          {error}
        </p>

        {/* Action Buttons - адаптивные отступы */}
        <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 justify-center">
          {onRetry && (
            <button
              onClick={onRetry}
              className="btn-primary flex items-center justify-center space-x-1.5 sm:space-x-2 text-sm sm:text-base px-4 py-2 sm:px-6 sm:py-3"
            >
              <RefreshCw className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>Try again</span>
            </button>
          )}
          
          {onReset && (
            <button
              onClick={onReset}
              className="
                px-4 py-2 sm:px-6 sm:py-3 text-sm sm:text-base
                bg-white border border-gray-200 rounded-btn
                text-black hover:text-black hover:border-black/30
                transition-all duration-150
                flex items-center justify-center space-x-1.5 sm:space-x-2
              "
            >
              <ArrowLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span>Start over</span>
            </button>
          )}
        </div>

        {/* Help Text - адаптивные отступы */}
        <div className="mt-6 sm:mt-8 p-3 sm:p-4 bg-gray-50 rounded-lg sm:rounded-card border border-gray-200">
          <h3 className="text-xs sm:text-sm font-medium text-text-primary mb-1.5 sm:mb-2">
            Common Issues & Solutions:
          </h3>
          <ul className="text-xs text-content-subtitle space-y-0.5 sm:space-y-1 text-left">
            <li>• <strong>Profile not found:</strong> Check if profile is public and URL is correct</li>
            <li>• <strong>Rate limit exceeded:</strong> Wait 5-10 minutes before trying again</li>
            <li>• <strong>API connection issues:</strong> Check internet connection and API keys</li>
            <li>• <strong>Protected profile:</strong> Some popular accounts may be protected from parsing</li>
            <li>• <strong>Regional restrictions:</strong> Profile might be restricted in your region</li>
          </ul>
          
          <div className="mt-3 text-xs text-content-placeholder">
            💡 <strong>Tip:</strong> Try using just the username (e.g., "zachking") instead of the full URL
          </div>
        </div>

        {/* Real data only - no demo mode */}
      </div>
    </div>
  );
};

export default ErrorState;
