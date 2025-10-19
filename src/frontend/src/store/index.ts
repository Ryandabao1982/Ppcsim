import { configureStore } from '@reduxjs/toolkit';
import campaignsReducer from './slices/campaignSlice';
import keywordsReducer from './slices/keywordSlice';
import adGroupsReducer from './slices/adGroupSlice';

export const store = configureStore({
  reducer: {
    campaigns: campaignsReducer,
    keywords: keywordsReducer,
    adGroups: adGroupsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
