import axios from 'axios';
import { Keyword, CreateKeywordData, UpdateKeywordData, BulkKeywordOperation } from '../types/keyword';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const keywordApi = {
  // Get all keywords for a campaign
  getCampaignKeywords: async (campaignId: number): Promise<Keyword[]> => {
    const response = await api.get<Keyword[]>(`/keywords/campaign/${campaignId}`);
    return response.data;
  },

  // Get all keywords for an ad group
  getAdGroupKeywords: async (adGroupId: number): Promise<Keyword[]> => {
    const response = await api.get<Keyword[]>(`/keywords/adgroup/${adGroupId}`);
    return response.data;
  },

  // Get a single keyword by ID
  getKeywordById: async (id: number): Promise<Keyword> => {
    const response = await api.get<Keyword>(`/keywords/${id}`);
    return response.data;
  },

  // Create a new keyword
  createKeyword: async (data: CreateKeywordData): Promise<Keyword> => {
    const response = await api.post<Keyword>('/keywords', data);
    return response.data;
  },

  // Update a keyword
  updateKeyword: async (id: number, data: UpdateKeywordData): Promise<Keyword> => {
    const response = await api.put<Keyword>(`/keywords/${id}`, data);
    return response.data;
  },

  // Delete a keyword
  deleteKeyword: async (id: number): Promise<void> => {
    await api.delete(`/keywords/${id}`);
  },

  // Bulk operations on keywords
  bulkOperation: async (operation: BulkKeywordOperation): Promise<void> => {
    await api.post('/keywords/bulk', operation);
  },
};
