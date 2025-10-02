import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';
import { checkSubscriptionStatus } from '@/services/subscriptionService';

export function SubscriptionSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [verifying, setVerifying] = useState(true);
  const [subscriptionActive, setSubscriptionActive] = useState(false);

  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    verifySubscription();
  }, []);

  const verifySubscription = async () => {
    try {
      // Wait a bit for webhook to process
      await new Promise(resolve => setTimeout(resolve, 2000));

      const status = await checkSubscriptionStatus();
      setSubscriptionActive(status.has_active_subscription);
    } catch (error) {
      console.error('Failed to verify subscription:', error);
    } finally {
      setVerifying(false);
    }
  };

  const handleContinue = () => {
    navigate('/');
  };

  if (verifying) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50">
        <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full text-center space-y-4">
          <div className="animate-spin h-16 w-16 mx-auto border-4 border-blue-500 border-t-transparent rounded-full"></div>
          <h2 className="text-xl font-bold">Verifying Your Subscription</h2>
          <p className="text-gray-600">
            Please wait while we confirm your payment...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full space-y-6">
        {/* Success Icon */}
        <div className="text-center">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto" />
        </div>

        {/* Title */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">
            {subscriptionActive ? 'Subscription Activated!' : 'Payment Successful!'}
          </h2>
          <p className="text-gray-600">
            {subscriptionActive 
              ? 'Your TrendXL Pro subscription is now active. You have full access to all features!'
              : 'Your payment was successful. Your subscription will be activated shortly.'}
          </p>
        </div>

        {/* Session ID */}
        {sessionId && (
          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-xs text-gray-500">Session ID:</p>
            <p className="text-sm font-mono break-all">{sessionId}</p>
          </div>
        )}

        {/* Features List */}
        <div className="space-y-3">
          <h3 className="font-semibold">What's included:</h3>
          <ul className="space-y-2">
            <li className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              <span className="text-sm">Unlimited trend analysis</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              <span className="text-sm">AI-powered insights</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              <span className="text-sm">Advanced content relevance scoring</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              <span className="text-sm">Priority support</span>
            </li>
          </ul>
        </div>

        {/* Continue Button */}
        <button
          onClick={handleContinue}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
        >
          Start Analyzing Trends
        </button>

        {/* Footer */}
        <p className="text-xs text-gray-500 text-center">
          You can manage your subscription anytime from your account settings.
        </p>
      </div>
    </div>
  );
}

export default SubscriptionSuccess;

