import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  InputAdornment,
  Alert,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { updateCampaign } from '../store/slices/campaignSlice';

interface CampaignEditDialogProps {
  open: boolean;
  onClose: () => void;
  campaignId: number;
}

function CampaignEditDialog({ open, onClose, campaignId }: CampaignEditDialogProps) {
  const dispatch = useDispatch<AppDispatch>();
  const { campaigns } = useSelector((state: RootState) => state.campaigns);
  const campaign = campaigns.find((c) => c.id === campaignId);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    dailyBudget: '',
    status: 'ACTIVE',
    totalBudget: '',
  });

  useEffect(() => {
    if (campaign) {
      setFormData({
        name: campaign.name,
        dailyBudget: campaign.dailyBudget.toString(),
        status: campaign.status,
        totalBudget: campaign.totalBudget?.toString() || '',
      });
    }
  }, [campaign, open]);

  const handleChange = (field: string) => (event: any) => {
    setFormData({
      ...formData,
      [field]: event.target.value,
    });
    setError(null);
  };

  const handleSubmit = async () => {
    try {
      // Validation
      if (!formData.name.trim()) {
        setError('Campaign name is required');
        return;
      }

      const dailyBudget = parseFloat(formData.dailyBudget);
      if (isNaN(dailyBudget) || dailyBudget <= 0) {
        setError('Daily budget must be greater than 0');
        return;
      }

      const totalBudget = formData.totalBudget ? parseFloat(formData.totalBudget) : undefined;
      if (totalBudget !== undefined && (isNaN(totalBudget) || totalBudget <= 0)) {
        setError('Total budget must be greater than 0');
        return;
      }

      // Update campaign
      await dispatch(
        updateCampaign({
          id: campaignId,
          userId: 1, // TODO: Get from auth context
          data: {
            name: formData.name.trim(),
            dailyBudget,
            status: formData.status as any,
            totalBudget,
          },
        })
      ).unwrap();

      setError(null);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to update campaign');
    }
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  if (!campaign) return null;

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Edit Campaign</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Campaign Name"
              value={formData.name}
              onChange={handleChange('name')}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Daily Budget"
              type="number"
              value={formData.dailyBudget}
              onChange={handleChange('dailyBudget')}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              inputProps={{ min: 0, step: 0.01 }}
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Total Budget (Optional)"
              type="number"
              value={formData.totalBudget}
              onChange={handleChange('totalBudget')}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              inputProps={{ min: 0, step: 0.01 }}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select value={formData.status} label="Status" onChange={handleChange('status')}>
                <MenuItem value="ACTIVE">Active</MenuItem>
                <MenuItem value="PAUSED">Paused</MenuItem>
                <MenuItem value="ARCHIVED">Archived</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Update Campaign
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default CampaignEditDialog;
