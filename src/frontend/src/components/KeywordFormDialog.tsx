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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Grid,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../store';
import { createKeyword, updateKeyword } from '../store/slices/keywordSlice';
import { MatchType } from '../types/keyword';

interface KeywordFormDialogProps {
  open: boolean;
  onClose: () => void;
  campaignId: number;
  keywordId?: number | null;
}

function KeywordFormDialog({
  open,
  onClose,
  campaignId,
  keywordId,
}: KeywordFormDialogProps) {
  const dispatch = useDispatch<AppDispatch>();
  const { keywords } = useSelector((state: RootState) => state.keywords);
  const { adGroups } = useSelector((state: RootState) => state.adGroups);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    keywordText: '',
    adGroupId: '',
    matchType: 'EXACT' as MatchType,
    bid: '',
    isNegative: false,
  });

  // Load existing keyword data when editing
  useEffect(() => {
    if (keywordId) {
      const keyword = keywords.find((k) => k.id === keywordId);
      if (keyword) {
        setFormData({
          keywordText: keyword.keywordText,
          adGroupId: keyword.adGroupId.toString(),
          matchType: keyword.matchType,
          bid: keyword.bid.toString(),
          isNegative: keyword.isNegative,
        });
      }
    } else {
      // Pre-select first ad group if available
      const defaultAdGroupId = adGroups.length > 0 ? adGroups[0].id.toString() : '';
      setFormData({
        keywordText: '',
        adGroupId: defaultAdGroupId,
        matchType: 'EXACT',
        bid: '',
        isNegative: false,
      });
    }
  }, [keywordId, keywords, adGroups, open]);

  const handleChange = (field: string) => (event: any) => {
    const value = field === 'isNegative' ? event.target.checked : event.target.value;
    setFormData({
      ...formData,
      [field]: value,
    });
    setError(null);
  };

  const handleSubmit = async () => {
    try {
      // Validation
      if (!formData.keywordText.trim()) {
        setError('Keyword text is required');
        return;
      }

      if (!formData.adGroupId) {
        setError('Please select an ad group');
        return;
      }

      const bid = parseFloat(formData.bid);
      if (!formData.isNegative && (isNaN(bid) || bid <= 0)) {
        setError('Bid must be greater than 0 for non-negative keywords');
        return;
      }

      if (keywordId) {
        // Update existing keyword
        await dispatch(
          updateKeyword({
            id: keywordId,
            data: {
              keywordText: formData.keywordText.trim(),
              matchType: formData.matchType,
              bid: formData.isNegative ? 0 : bid,
            },
          })
        ).unwrap();
      } else {
        // Create new keyword
        await dispatch(
          createKeyword({
            campaignId,
            adGroupId: parseInt(formData.adGroupId),
            keywordText: formData.keywordText.trim(),
            matchType: formData.matchType,
            bid: formData.isNegative ? 0 : bid,
            isNegative: formData.isNegative,
          })
        ).unwrap();
      }

      // Reset form and close dialog
      setFormData({
        keywordText: '',
        adGroupId: adGroups.length > 0 ? adGroups[0].id.toString() : '',
        matchType: 'EXACT',
        bid: '',
        isNegative: false,
      });
      setError(null);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save keyword');
    }
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  if (adGroups.length === 0) {
    return (
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{keywordId ? 'Edit Keyword' : 'Add Keyword'}</DialogTitle>
        <DialogContent>
          <Alert severity="warning">
            Please create at least one ad group before adding keywords.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>{keywordId ? 'Edit Keyword' : 'Add Keyword'}</DialogTitle>
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
              label="Keyword"
              value={formData.keywordText}
              onChange={handleChange('keywordText')}
              placeholder="e.g., wireless headphones"
              required
              helperText="Enter a single keyword or phrase"
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth required>
              <InputLabel>Ad Group</InputLabel>
              <Select
                value={formData.adGroupId}
                label="Ad Group"
                onChange={handleChange('adGroupId')}
              >
                {adGroups.map((ag) => (
                  <MenuItem key={ag.id} value={ag.id.toString()}>
                    {ag.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth required>
              <InputLabel>Match Type</InputLabel>
              <Select
                value={formData.matchType}
                label="Match Type"
                onChange={handleChange('matchType')}
              >
                <MenuItem value="EXACT">Exact Match</MenuItem>
                <MenuItem value="PHRASE">Phrase Match</MenuItem>
                <MenuItem value="BROAD">Broad Match</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Bid"
              type="number"
              value={formData.bid}
              onChange={handleChange('bid')}
              disabled={formData.isNegative}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
              inputProps={{ min: 0, step: 0.01 }}
              required={!formData.isNegative}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.isNegative}
                  onChange={handleChange('isNegative')}
                />
              }
              label="Negative Keyword (blocks this keyword from triggering ads)"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {keywordId ? 'Update' : 'Add'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default KeywordFormDialog;
