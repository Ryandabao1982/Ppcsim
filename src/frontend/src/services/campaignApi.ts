import axios from 'axios';
import { Campaign, CampaignStats, CreateCampaignDto, UpdateCampaignDto } from '../types/campaign';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

interface ApiResponse<T> {
  status: string;
  data: T;
}

export const campaignApi = {
  /**
   * Get all campaigns for a user
   */
  getCampaigns: async (userId: number, filters?: {
    status?: string;
    campaignType?: string;
  }) => {
    const params = new URLSearchParams({ userId: userId.toString() });
    if (filters?.status) params.append('status', filters.status);
    if (filters?.campaignType) params.append('campaignType', filters.campaignType);
    
    return axios.get<ApiResponse<{ campaigns: Campaign[] }>>(
      `${API_BASE_URL}/campaigns?${params.toString()}`
    );
  },

  /**
   * Get a single campaign by ID
   */
  getCampaign: async (id: number, userId: number) => {
    return axios.get<ApiResponse<{ campaign: Campaign }>>(
      `${API_BASE_URL}/campaigns/${id}?userId=${userId}`
    );
  },

  /**
   * Create a new campaign
   */
  createCampaign: async (userId: number, data: CreateCampaignDto) => {
    return axios.post<ApiResponse<{ campaign: Campaign }>>(
      `${API_BASE_URL}/campaigns`,
      { ...data, userId }
    );
  },

  /**
   * Update a campaign
   */
  updateCampaign: async (id: number, userId: number, data: UpdateCampaignDto) => {
    return axios.put<ApiResponse<{ campaign: Campaign }>>(
      `${API_BASE_URL}/campaigns/${id}`,
      { ...data, userId }
    );
  },

  /**
   * Delete a campaign
   */
  deleteCampaign: async (id: number, userId: number) => {
    return axios.delete(
      `${API_BASE_URL}/campaigns/${id}?userId=${userId}`
    );
  },

  /**
   * Get campaign statistics
   */
  getCampaignStats: async (id: number, userId: number) => {
    return axios.get<ApiResponse<{ stats: CampaignStats }>>(
      `${API_BASE_URL}/campaigns/${id}/stats?userId=${userId}`
    );
  },
};
