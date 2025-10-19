import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { keywordApi } from '../../services/keywordApi';
import { Keyword, CreateKeywordData, UpdateKeywordData } from '../../types/keyword';

export interface KeywordState {
  keywords: Keyword[];
  selectedKeyword: Keyword | null;
  loading: boolean;
  error: string | null;
}

const initialState: KeywordState = {
  keywords: [],
  selectedKeyword: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchCampaignKeywords = createAsyncThunk(
  'keywords/fetchCampaignKeywords',
  async (campaignId: number) => {
    return await keywordApi.getCampaignKeywords(campaignId);
  }
);

export const fetchAdGroupKeywords = createAsyncThunk(
  'keywords/fetchAdGroupKeywords',
  async (adGroupId: number) => {
    return await keywordApi.getAdGroupKeywords(adGroupId);
  }
);

export const createKeyword = createAsyncThunk(
  'keywords/createKeyword',
  async (data: CreateKeywordData) => {
    return await keywordApi.createKeyword(data);
  }
);

export const updateKeyword = createAsyncThunk(
  'keywords/updateKeyword',
  async ({ id, data }: { id: number; data: UpdateKeywordData }) => {
    return await keywordApi.updateKeyword(id, data);
  }
);

export const deleteKeyword = createAsyncThunk(
  'keywords/deleteKeyword',
  async (id: number) => {
    await keywordApi.deleteKeyword(id);
    return id;
  }
);

const keywordSlice = createSlice({
  name: 'keywords',
  initialState,
  reducers: {
    selectKeyword: (state, action: PayloadAction<Keyword | null>) => {
      state.selectedKeyword = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch campaign keywords
      .addCase(fetchCampaignKeywords.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCampaignKeywords.fulfilled, (state, action) => {
        state.loading = false;
        state.keywords = action.payload;
      })
      .addCase(fetchCampaignKeywords.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch keywords';
      })
      // Fetch ad group keywords
      .addCase(fetchAdGroupKeywords.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAdGroupKeywords.fulfilled, (state, action) => {
        state.loading = false;
        state.keywords = action.payload;
      })
      .addCase(fetchAdGroupKeywords.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch keywords';
      })
      // Create keyword
      .addCase(createKeyword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createKeyword.fulfilled, (state, action) => {
        state.loading = false;
        state.keywords.push(action.payload);
      })
      .addCase(createKeyword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create keyword';
      })
      // Update keyword
      .addCase(updateKeyword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateKeyword.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.keywords.findIndex((k) => k.id === action.payload.id);
        if (index !== -1) {
          state.keywords[index] = action.payload;
        }
      })
      .addCase(updateKeyword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update keyword';
      })
      // Delete keyword
      .addCase(deleteKeyword.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteKeyword.fulfilled, (state, action) => {
        state.loading = false;
        state.keywords = state.keywords.filter((k) => k.id !== action.payload);
      })
      .addCase(deleteKeyword.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to delete keyword';
      });
  },
});

export const { selectKeyword, clearError } = keywordSlice.actions;
export default keywordSlice.reducer;
