import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Button,
  CardActionArea,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { fetchCampaigns } from '../store/slices/campaignSlice';
import { RootState, AppDispatch } from '../store';
import CampaignFormDialog from '../components/CampaignFormDialog';

// Temporary authentication hook to centralize user logic
function useAuth() {
  // TODO: Replace with real authentication logic
  return { id: 1 };
}

function CampaignListPage() {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { campaigns, loading, error } = useSelector((state: RootState) => state.campaigns);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const user = useAuth();

  useEffect(() => {
    // Get userId from auth context (temporary implementation)
    dispatch(fetchCampaigns(user.id));
  }, [dispatch, user.id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'PAUSED':
        return 'warning';
      case 'ARCHIVED':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          My Campaigns
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Campaign
        </Button>
      </Box>

      {campaigns.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              No campaigns yet. Create your first campaign to get started!
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {campaigns.map((campaign) => (
            <Grid item xs={12} md={6} lg={4} key={campaign.id}>
              <Card>
                <CardActionArea onClick={() => navigate(`/campaigns/${campaign.id}`)}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                      <Typography variant="h6" component="div">
                        {campaign.name}
                      </Typography>
                      <Chip
                        label={campaign.status}
                        color={getStatusColor(campaign.status)}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {campaign.campaignType.replace('_', ' ')}
                    </Typography>

                    <Box mt={2}>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Daily Budget
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            ${Number(campaign.dailyBudget).toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Total Spend
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            ${Number(campaign.totalSpend).toFixed(2)}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Clicks
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {campaign.totalClicks}
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">
                            Conversions
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {campaign.totalConversions}
                          </Typography>
                        </Grid>
                      </Grid>
                    </Box>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <CampaignFormDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
      />
    </Box>
  );
}

export default CampaignListPage;
