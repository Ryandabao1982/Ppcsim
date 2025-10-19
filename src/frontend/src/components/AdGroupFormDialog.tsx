import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Alert,
  InputAdornment,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { createAdGroup, updateAdGroup } from '../store/slices/adGroupSlice';

interface AdGroupFormDialogProps {
  open: boolean;
  onClose: () => void;
  campaignId: number;
  adGroupId?: number | null;
}

function AdGroupFormDialog({
  open,
  onClose,
  campaignId,
  adGroupId,
}: AdGroupFormDialogProps) {
  const dispatch = useDispatch<AppDispatch>();
  const { adGroups } = useSelector((state: RootState) => state.adGroups);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    defaultBid: '',
  });

  // Load existing ad group data when editing
  useEffect(() => {
    if (adGroupId) {
      const adGroup = adGroups.find((ag) => ag.id === adGroupId);
      if (adGroup) {
        setFormData({
          name: adGroup.name,
          defaultBid: adGroup.defaultBid.toString(),
        });
      }
    } else {
      setFormData({ name: '', defaultBid: '' });
    }
  }, [adGroupId, adGroups]);

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
        setError('Ad group name is required');
        return;
      }

      const defaultBid = parseFloat(formData.defaultBid);
      if (isNaN(defaultBid) || defaultBid <= 0) {
        setError('Default bid must be greater than 0');
        return;
      }

      if (adGroupId) {
        // Update existing ad group
        await dispatch(
          updateAdGroup({
            id: adGroupId,
            data: {
              name: formData.name.trim(),
              defaultBid,
            },
          })
        ).unwrap();
      } else {
        // Create new ad group
        await dispatch(
          createAdGroup({
            campaignId,
            name: formData.name.trim(),
            defaultBid,
          })
        ).unwrap();
      }

      // Reset form and close dialog
      setFormData({ name: '', defaultBid: '' });
      setError(null);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save ad group');
    }
  };

  const handleClose = () => {
    setError(null);
    setFormData({ name: '', defaultBid: '' });
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{adGroupId ? 'Edit Ad Group' : 'Create Ad Group'}</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          label="Ad Group Name"
          value={formData.name}
          onChange={handleChange('name')}
          placeholder="e.g., Product Category - Main Keywords"
          required
          sx={{ mt: 2, mb: 2 }}
        />

        <TextField
          fullWidth
          label="Default Bid"
          type="number"
          value={formData.defaultBid}
          onChange={handleChange('defaultBid')}
          InputProps={{
            startAdornment: <InputAdornment position="start">$</InputAdornment>,
          }}
          inputProps={{ min: 0, step: 0.01 }}
          required
          helperText="This bid will be used as the default for new keywords in this ad group"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {adGroupId ? 'Update' : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default AdGroupFormDialog;
