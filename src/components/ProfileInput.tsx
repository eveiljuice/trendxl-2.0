import React, { useState } from 'react';
import { Search, User, AlertCircle } from 'lucide-react';
import ApiStatusBanner from './ApiStatusBanner';
import { ProfileInputProps } from '../types';
import { isValidTikTokInput } from '../utils';

const ProfileInput: React.FC<ProfileInputProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValidTikTokInput(input)) {
      setError('Please enter a valid TikTok profile link or username');
      return;
    }
    
    setError('');
    onSubmit(input);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    if (error) setError(''); // Clear error when user starts typing
  };

  return (
    <div className="section-spacing animate-fade-in">
      {/* API Status Banner */}
      <ApiStatusBanner />
      
      {/* Header */}
      <div className="text-center element-spacing">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-card rounded-full mb-6">
          <User className="w-8 h-8 text-primary-accent" />
        </div>
        <h1 className="text-4xl font-bold text-text-primary mb-4">
          TrendXL 2.0
        </h1>
        <p className="text-lg text-text-secondary max-w-2xl mx-auto">
          Analyze TikTok profiles and find the hottest trends with AI
        </p>
      </div>

      {/* Input Form */}
      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-text-secondary" />
            </div>
            <input
              type="text"
              value={input}
              onChange={handleInputChange}
              placeholder="Enter TikTok profile link or @username"
              className={`
                w-full pl-12 pr-4 py-4 
                bg-primary-card border rounded-card
                text-text-primary placeholder-text-secondary
                focus:outline-none focus:ring-2 focus:ring-primary-accent focus:border-transparent
                transition-all duration-200
                ${error ? 'border-red-500' : 'border-primary-line hover:border-primary-accent/30'}
              `}
              disabled={isLoading}
            />
          </div>
          
          {/* Error Message */}
          {error && (
            <div className="flex items-center space-x-2 text-red-400 text-sm animate-fade-in">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={`
              w-full btn-primary
              disabled:opacity-50 disabled:cursor-not-allowed
              ${isLoading ? 'animate-pulse' : ''}
            `}
          >
            {isLoading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Analyzing profile...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <Search className="w-5 h-5" />
                <span>Find Trends</span>
              </div>
            )}
          </button>
        </form>

        {/* Examples */}
        <div className="mt-8 text-center">
          <p className="text-sm text-text-secondary mb-3">Examples:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              '@username',
              'https://www.tiktok.com/@username',
              'https://vm.tiktok.com/ZMhKqJ7Lx/',
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setInput(example)}
                className="
                  px-3 py-1 text-xs
                  bg-primary-card border border-primary-line rounded-btn
                  text-text-secondary hover:text-text-primary hover:border-primary-accent/30
                  transition-all duration-150
                "
                disabled={isLoading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileInput;
