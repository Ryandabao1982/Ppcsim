import axios from 'axios';
import { AdGroup, CreateAdGroupData, UpdateAdGroupData } from '../types/adGroup';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const adGroupApi = {
  // Get all ad groups for a campaign
  getCampaignAdGroups: async (campaignId: number): Promise<AdGroup[]> => {
    const response = await api.get<AdGroup[]>(`/adgroups/campaign/${campaignId}`);
    return response.data;
  },

  // Get a single ad group by ID
  getAdGroupById: async (id: number): Promise<AdGroup> => {
    const response = await api.get<AdGroup>(`/adgroups/${id}`);
    return response.data;
  },

  // Create a new ad group
  createAdGroup: async (data: CreateAdGroupData): Promise<AdGroup> => {
    const response = await api.post<AdGroup>('/adgroups', data);
    return response.data;
  },

  // Update an ad group
  updateAdGroup: async (id: number, data: UpdateAdGroupData): Promise<AdGroup> => {
    const response = await api.put<AdGroup>(`/adgroups/${id}`, data);
    return response.data;
  },

  // Delete an ad group
  deleteAdGroup: async (id: number): Promise<void> => {
    await api.delete(`/adgroups/${id}`);
  },
};
