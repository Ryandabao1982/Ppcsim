import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Campaign, CreateCampaignDto, UpdateCampaignDto } from '../../types/campaign';
import { campaignApi } from '../../services/campaignApi';

interface CampaignsState {
  campaigns: Campaign[];
  currentCampaign: Campaign | null;
  loading: boolean;
  error: string | null;
}

const initialState: CampaignsState = {
  campaigns: [],
  currentCampaign: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchCampaigns = createAsyncThunk(
  'campaigns/fetchAll',
  async (userId: number) => {
    const response = await campaignApi.getCampaigns(userId);
    return response.data.campaigns;
  }
);

export const fetchCampaignById = createAsyncThunk(
  'campaigns/fetchById',
  async ({ id, userId }: { id: number; userId: number }) => {
    const response = await campaignApi.getCampaign(id, userId);
    return response.data.campaign;
  }
);

export const createCampaign = createAsyncThunk(
  'campaigns/create',
  async ({ userId, data }: { userId: number; data: CreateCampaignDto }) => {
    const response = await campaignApi.createCampaign(userId, data);
    return response.data.campaign;
  }
);

export const updateCampaign = createAsyncThunk(
  'campaigns/update',
  async ({ id, userId, data }: { id: number; userId: number; data: UpdateCampaignDto }) => {
    const response = await campaignApi.updateCampaign(id, userId, data);
    return response.data.campaign;
  }
);

export const deleteCampaign = createAsyncThunk(
  'campaigns/delete',
  async ({ id, userId }: { id: number; userId: number }) => {
    await campaignApi.deleteCampaign(id, userId);
    return id;
  }
);

const campaignsSlice = createSlice({
  name: 'campaigns',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentCampaign: (state) => {
      state.currentCampaign = null;
    },
  },
  extraReducers: (builder) => {
    // Fetch campaigns
    builder.addCase(fetchCampaigns.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchCampaigns.fulfilled, (state, action: PayloadAction<Campaign[]>) => {
      state.loading = false;
      state.campaigns = action.payload;
    });
    builder.addCase(fetchCampaigns.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch campaigns';
    });

    // Fetch campaign by ID
    builder.addCase(fetchCampaignById.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(fetchCampaignById.fulfilled, (state, action: PayloadAction<Campaign>) => {
      state.loading = false;
      state.currentCampaign = action.payload;
    });
    builder.addCase(fetchCampaignById.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch campaign';
    });

    // Create campaign
    builder.addCase(createCampaign.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(createCampaign.fulfilled, (state, action: PayloadAction<Campaign>) => {
      state.loading = false;
      state.campaigns.unshift(action.payload);
    });
    builder.addCase(createCampaign.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to create campaign';
    });

    // Update campaign
    builder.addCase(updateCampaign.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(updateCampaign.fulfilled, (state, action: PayloadAction<Campaign>) => {
      state.loading = false;
      const index = state.campaigns.findIndex(c => c.id === action.payload.id);
      if (index !== -1) {
        state.campaigns[index] = action.payload;
      }
      if (state.currentCampaign?.id === action.payload.id) {
        state.currentCampaign = action.payload;
      }
    });
    builder.addCase(updateCampaign.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to update campaign';
    });

    // Delete campaign
    builder.addCase(deleteCampaign.pending, (state) => {
      state.loading = true;
      state.error = null;
    });
    builder.addCase(deleteCampaign.fulfilled, (state, action: PayloadAction<number>) => {
      state.loading = false;
      state.campaigns = state.campaigns.filter(c => c.id !== action.payload);
      if (state.currentCampaign?.id === action.payload) {
        state.currentCampaign = null;
      }
    });
    builder.addCase(deleteCampaign.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to delete campaign';
    });
  },
});

export const { clearError, clearCurrentCampaign } = campaignsSlice.actions;
export default campaignsSlice.reducer;
