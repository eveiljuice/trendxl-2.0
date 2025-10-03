import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  Card,
  Heading,
  Badge,
  Spinner,
  Button,
} from '@chakra-ui/react';
import { History, Trash2, Eye, Calendar } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { toaster } from '../components/ui/toaster';
import { supabase } from '../lib/supabase';

interface ScanHistoryItem {
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

const MyTrends: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadScanHistory();
    }
  }, [user]);

  const loadScanHistory = async () => {
    try {
      setIsLoading(true);
      
      const { data, error } = await supabase
        .from('scan_history')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error('Error loading scan history:', error);
        throw error;
      }

      setScans(data || []);
    } catch (error: any) {
      console.error('Failed to load scan history:', error);
      toaster.create({
        title: 'Error',
        description: 'Failed to load scan history',
        type: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const deleteScan = async (id: string) => {
    if (!confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    try {
      const { error } = await supabase
        .from('scan_history')
        .delete()
        .eq('id', id);

      if (error) throw error;

      setScans(scans.filter(scan => scan.id !== id));
      
      toaster.create({
        title: 'Deleted',
        description: 'Scan deleted successfully',
        type: 'success',
        duration: 3000,
      });
    } catch (error: any) {
      console.error('Failed to delete scan:', error);
      toaster.create({
        title: 'Error',
        description: 'Failed to delete scan',
        type: 'error',
        duration: 5000,
      });
    }
  };

  const viewScan = (scan: ScanHistoryItem) => {
    // Open analysis in new tab
    const url = `/analysis/${scan.id}`;
    window.open(url, '_blank');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!user) {
    return (
      <Container maxW="container.lg" py={8}>
        <Box 
          bg="orange.50" 
          borderLeft="4px solid"
          borderColor="orange.500"
          p={4}
          borderRadius="md"
        >
          <Heading size="sm" mb={2}>Not logged in</Heading>
          <Text fontSize="sm">Please log in to view your scan history.</Text>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <Box>
          <HStack gap={3} mb={2}>
            <History className="w-8 h-8" />
            <Heading size="lg" className="font-orbitron">My Trends</Heading>
          </HStack>
          <Text color="gray.600">
            View and manage your saved TikTok profile analyses
          </Text>
        </Box>

        {/* Scan History List */}
        {isLoading ? (
          <Box textAlign="center" py={12}>
            <Spinner size="xl" />
            <Text mt={4} color="gray.600">Loading your scan history...</Text>
          </Box>
        ) : scans.length === 0 ? (
          <Card.Root>
            <Card.Body>
              <VStack gap={4} py={8}>
                <History className="w-16 h-16 text-gray-400" />
                <Heading size="md" color="gray.600">No Scans Yet</Heading>
                <Text color="gray.500" textAlign="center">
                  Start analyzing TikTok profiles to see them here!
                </Text>
                <Button
                  colorPalette="blue"
                  onClick={() => navigate('/')}
                  mt={4}
                >
                  Start Analyzing
                </Button>
              </VStack>
            </Card.Body>
          </Card.Root>
        ) : (
          <VStack gap={4} align="stretch">
            {scans.map((scan) => (
              <Card.Root key={scan.id} className="hover:shadow-lg transition-shadow">
                <Card.Body>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" gap={2} flex={1}>
                      <HStack gap={3}>
                        <Heading size="md" className="font-orbitron">
                          @{scan.username}
                        </Heading>
                        <Badge 
                          colorPalette={scan.scan_type === 'paid' ? 'green' : 'purple'}
                          variant="solid"
                        >
                          {scan.scan_type === 'paid' ? 'Premium' : 'Free Trial'}
                        </Badge>
                      </HStack>
                      
                      <HStack gap={2} color="gray.600" fontSize="sm">
                        <Calendar className="w-4 h-4" />
                        <Text>{formatDate(scan.created_at)}</Text>
                      </HStack>

                      {/* Show analysis stats */}
                      <HStack gap={4} fontSize="sm" color="gray.600" mt={2}>
                        {scan.profile_data?.trends?.length > 0 && (
                          <Text>
                            <Text as="span" fontWeight="bold" color="blue.600">
                              {scan.profile_data.trends.length}
                            </Text>
                            {' '}trends
                          </Text>
                        )}
                        {scan.profile_data?.hashtags?.length > 0 && (
                          <Text>
                            <Text as="span" fontWeight="bold" color="purple.600">
                              {scan.profile_data.hashtags.length}
                            </Text>
                            {' '}hashtags
                          </Text>
                        )}
                      </HStack>

                      {scan.profile_data?.profile?.bio && (
                        <Text fontSize="sm" color="gray.700" mt={2} css={{
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}>
                          {scan.profile_data.profile.bio}
                        </Text>
                      )}
                    </VStack>

                    <HStack gap={2}>
                      <Button
                        size="sm"
                        colorPalette="blue"
                        onClick={() => viewScan(scan)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View
                      </Button>
                      <Button
                        size="sm"
                        colorPalette="red"
                        variant="outline"
                        onClick={() => deleteScan(scan.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </HStack>
                  </HStack>
                </Card.Body>
              </Card.Root>
            ))}
          </VStack>
        )}
      </VStack>
    </Container>
  );
};

export default MyTrends;

