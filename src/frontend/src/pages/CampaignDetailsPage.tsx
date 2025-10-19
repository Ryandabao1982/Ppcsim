import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { RootState, AppDispatch } from '../store';
import { fetchCampaignAdGroups } from '../store/slices/adGroupSlice';
import { fetchCampaignKeywords } from '../store/slices/keywordSlice';
import AdGroupList from '../components/AdGroupList';
import KeywordList from '../components/KeywordList';
import CampaignEditDialog from '../components/CampaignEditDialog';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`campaign-tabpanel-${index}`}
      aria-labelledby={`campaign-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function CampaignDetailsPage() {
  const { campaignId } = useParams<{ campaignId: string }>();
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const [tabValue, setTabValue] = useState(0);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  const { campaigns, loading: campaignsLoading } = useSelector(
    (state: RootState) => state.campaigns
  );

  const campaign = campaigns.find((c) => c.id === Number(campaignId));

  useEffect(() => {
    if (campaignId) {
      dispatch(fetchCampaignAdGroups(Number(campaignId)));
      dispatch(fetchCampaignKeywords(Number(campaignId)));
    }
  }, [dispatch, campaignId]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

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

  if (campaignsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!campaign) {
    return (
      <Box>
        <Alert severity="error">Campaign not found</Alert>
        <Button onClick={() => navigate('/campaigns')} sx={{ mt: 2 }}>
          Back to Campaigns
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/campaigns')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h4">{campaign.name}</Typography>
            <Chip label={campaign.status} color={getStatusColor(campaign.status)} />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {campaign.campaignType.replace(/_/g, ' ')} • {campaign.targetingType}
          </Typography>
        </Box>
        <IconButton onClick={() => setEditDialogOpen(true)}>
          <EditIcon />
        </IconButton>
      </Box>

      {/* Campaign Stats */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Daily Budget
            </Typography>
            <Typography variant="h6">${Number(campaign.dailyBudget).toFixed(2)}</Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Total Spend
            </Typography>
            <Typography variant="h6">${Number(campaign.totalSpend).toFixed(2)}</Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Impressions
            </Typography>
            <Typography variant="h6">{campaign.totalImpressions.toString()}</Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Clicks
            </Typography>
            <Typography variant="h6">{campaign.totalClicks}</Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Conversions
            </Typography>
            <Typography variant="h6">{campaign.totalConversions}</Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              CTR
            </Typography>
            <Typography variant="h6">
              {Number(campaign.totalImpressions) > 0
                ? ((campaign.totalClicks / Number(campaign.totalImpressions)) * 100).toFixed(2)
                : '0.00'}
              %
            </Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              CVR
            </Typography>
            <Typography variant="h6">
              {campaign.totalClicks > 0
                ? ((campaign.totalConversions / campaign.totalClicks) * 100).toFixed(2)
                : '0.00'}
              %
            </Typography>
          </Grid>
          <Grid item xs={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              ACOS
            </Typography>
            <Typography variant="h6">
              {Number(campaign.totalSales) > 0
                ? ((Number(campaign.totalSpend) / Number(campaign.totalSales)) * 100).toFixed(2)
                : '0.00'}
              %
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Ad Groups" />
          <Tab label="Keywords" />
          <Tab label="Performance" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <AdGroupList campaignId={Number(campaignId)} />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <KeywordList campaignId={Number(campaignId)} />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Alert severity="info">Performance metrics coming soon...</Alert>
        </TabPanel>
      </Paper>

      <CampaignEditDialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        campaignId={Number(campaignId)}
      />
    </Box>
  );
}

export default CampaignDetailsPage;
