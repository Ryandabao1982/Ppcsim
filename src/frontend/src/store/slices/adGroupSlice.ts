import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { adGroupApi } from '../../services/adGroupApi';
import { AdGroup, CreateAdGroupData, UpdateAdGroupData } from '../../types/adGroup';

export interface AdGroupState {
  adGroups: AdGroup[];
  selectedAdGroup: AdGroup | null;
  loading: boolean;
  error: string | null;
}

const initialState: AdGroupState = {
  adGroups: [],
  selectedAdGroup: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchCampaignAdGroups = createAsyncThunk(
  'adGroups/fetchCampaignAdGroups',
  async (campaignId: number) => {
    return await adGroupApi.getCampaignAdGroups(campaignId);
  }
);

export const createAdGroup = createAsyncThunk(
  'adGroups/createAdGroup',
  async (data: CreateAdGroupData) => {
    return await adGroupApi.createAdGroup(data);
  }
);

export const updateAdGroup = createAsyncThunk(
  'adGroups/updateAdGroup',
  async ({ id, data }: { id: number; data: UpdateAdGroupData }) => {
    return await adGroupApi.updateAdGroup(id, data);
  }
);

export const deleteAdGroup = createAsyncThunk(
  'adGroups/deleteAdGroup',
  async (id: number) => {
    await adGroupApi.deleteAdGroup(id);
    return id;
  }
);

const adGroupSlice = createSlice({
  name: 'adGroups',
  initialState,
  reducers: {
    selectAdGroup: (state, action: PayloadAction<AdGroup | null>) => {
      state.selectedAdGroup = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch campaign ad groups
      .addCase(fetchCampaignAdGroups.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCampaignAdGroups.fulfilled, (state, action) => {
        state.loading = false;
        state.adGroups = action.payload;
      })
      .addCase(fetchCampaignAdGroups.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch ad groups';
      })
      // Create ad group
      .addCase(createAdGroup.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAdGroup.fulfilled, (state, action) => {
        state.loading = false;
        state.adGroups.push(action.payload);
      })
      .addCase(createAdGroup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create ad group';
      })
      // Update ad group
      .addCase(updateAdGroup.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAdGroup.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.adGroups.findIndex((ag) => ag.id === action.payload.id);
        if (index !== -1) {
          state.adGroups[index] = action.payload;
        }
      })
      .addCase(updateAdGroup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update ad group';
      })
      // Delete ad group
      .addCase(deleteAdGroup.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteAdGroup.fulfilled, (state, action) => {
        state.loading = false;
        state.adGroups = state.adGroups.filter((ag) => ag.id !== action.payload);
      })
      .addCase(deleteAdGroup.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete ad group';
      });
  },
});

export const { selectAdGroup, clearError } = adGroupSlice.actions;
export default adGroupSlice.reducer;
