import { useState } from 'react';
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
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import { createCampaign } from '../store/slices/campaignSlice';

interface CampaignFormDialogProps {
  open: boolean;
  onClose: () => void;
}

function CampaignFormDialog({ open, onClose }: CampaignFormDialogProps) {
  const dispatch = useDispatch<AppDispatch>();
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    campaignType: 'SPONSORED_PRODUCTS',
    targetingType: 'MANUAL',
    dailyBudget: '',
    biddingStrategy: 'MANUAL',
    totalBudget: '',
  });

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

      // Create campaign
      await dispatch(createCampaign({
        userId: 1, // TODO: Get from auth context
        data: {
          name: formData.name.trim(),
          campaignType: formData.campaignType as any,
          targetingType: formData.targetingType as any,
          dailyBudget,
          biddingStrategy: formData.biddingStrategy as any,
          totalBudget,
        },
      })).unwrap();

      // Reset form and close dialog
      setFormData({
        name: '',
        campaignType: 'SPONSORED_PRODUCTS',
        targetingType: 'MANUAL',
        dailyBudget: '',
        biddingStrategy: 'MANUAL',
        totalBudget: '',
      });
      setError(null);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to create campaign');
    }
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Create New Campaign</DialogTitle>
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
              placeholder="e.g., Summer Sale 2024"
              required
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Campaign Type</InputLabel>
              <Select
                value={formData.campaignType}
                label="Campaign Type"
                onChange={handleChange('campaignType')}
              >
                <MenuItem value="SPONSORED_PRODUCTS">Sponsored Products</MenuItem>
                <MenuItem value="SPONSORED_BRANDS">Sponsored Brands</MenuItem>
                <MenuItem value="SPONSORED_DISPLAY">Sponsored Display</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Targeting Type</InputLabel>
              <Select
                value={formData.targetingType}
                label="Targeting Type"
                onChange={handleChange('targetingType')}
              >
                <MenuItem value="MANUAL">Manual</MenuItem>
                <MenuItem value="AUTOMATIC">Automatic</MenuItem>
              </Select>
            </FormControl>
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
              <InputLabel>Bidding Strategy</InputLabel>
              <Select
                value={formData.biddingStrategy}
                label="Bidding Strategy"
                onChange={handleChange('biddingStrategy')}
              >
                <MenuItem value="MANUAL">Manual</MenuItem>
                <MenuItem value="DYNAMIC_DOWN">Dynamic Bids - Down Only</MenuItem>
                <MenuItem value="DYNAMIC_UP_DOWN">Dynamic Bids - Up and Down</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          Create Campaign
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default CampaignFormDialog;
