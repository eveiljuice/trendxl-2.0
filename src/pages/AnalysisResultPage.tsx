import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TrendVideo } from '../types';
import {
  Box,
  Container,
  VStack,
  Spinner,
  Text,
  Button,
} from '@chakra-ui/react';
import { ArrowLeft } from 'lucide-react';

// Components
import ProfileCard from '../components/ProfileCard';
import HashtagList from '../components/HashtagList';
import TrendGrid from '../components/TrendGrid';
import VideoModal from '../components/VideoModal';
import { supabase } from '../lib/supabase';
import { toaster } from '../components/ui/toaster';

interface AnalysisData {
  id: string;
  username: string;
  profile_data: {
    profile: any;
    trends: any[];
    hashtags: any[];
    posts: any[];
    tokenUsage?: any;
  };
  scan_type: 'free' | 'paid';
  created_at: string;
}

const AnalysisResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTrend, setSelectedTrend] = useState<TrendVideo | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    if (id) {
      loadAnalysisData(id);
    }
  }, [id]);

  const loadAnalysisData = async (analysisId: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const { data, error: fetchError } = await supabase
        .from('scan_history')
        .select('*')
        .eq('id', analysisId)
        .single();

      if (fetchError) {
        console.error('Error loading analysis:', fetchError);
        throw new Error('Failed to load analysis');
      }

      if (!data) {
        throw new Error('Analysis not found');
      }

      setAnalysisData(data);
    } catch (err: any) {
      console.error('Failed to load analysis:', err);
      setError(err.message || 'Failed to load analysis');
      
      toaster.create({
        title: 'Error',
        description: err.message || 'Failed to load analysis',
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTrendClick = (trend: TrendVideo) => {
    setSelectedTrend(trend);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedTrend(null);
  };

  if (isLoading) {
    return (
      <Container maxW="container.lg" py={8}>
        <Box textAlign="center" py={12}>
          <Spinner size="xl" />
          <Text mt={4} color="gray.600">Loading analysis...</Text>
        </Box>
      </Container>
    );
  }

  if (error || !analysisData) {
    return (
      <Container maxW="container.lg" py={8}>
        <VStack gap={4} align="center" py={12}>
          <Text fontSize="xl" fontWeight="bold" color="red.600">
            {error || 'Analysis not found'}
          </Text>
          <Button
            colorPalette="blue"
            onClick={() => navigate('/my-trends')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to My Trends
          </Button>
        </VStack>
      </Container>
    );
  }

  const { profile_data } = analysisData;

  return (
    <div className="container mx-auto px-4 sm:px-6 md:px-8 py-6 sm:py-8">
      {/* Back Button */}
      <Box mb={6}>
        <Button
          variant="ghost"
          onClick={() => navigate('/my-trends')}
          size="sm"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to My Trends
        </Button>
      </Box>

      {/* Results */}
      <div className="space-y-8 sm:space-y-12 md:space-y-16">
        {/* Profile Information */}
        <div className="animate-fade-in">
          <ProfileCard profile={profile_data.profile} />
        </div>

        {/* Hashtags */}
        {profile_data.hashtags && profile_data.hashtags.length > 0 && (
          <div className="animate-slide-up" style={{ animationDelay: '200ms' }}>
            <HashtagList hashtags={profile_data.hashtags} />
          </div>
        )}

        {/* Trends Grid */}
        {profile_data.trends && profile_data.trends.length > 0 && (
          <div className="animate-slide-up" style={{ animationDelay: '400ms' }}>
            <TrendGrid
              trends={profile_data.trends}
              onTrendClick={handleTrendClick}
            />
          </div>
        )}
      </div>

      {/* Video Modal */}
      <VideoModal
        trend={selectedTrend}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default AnalysisResultPage;

