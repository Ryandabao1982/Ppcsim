export interface Campaign {
  id: number;
  userId: number;
  name: string;
  campaignType: 'SPONSORED_PRODUCTS' | 'SPONSORED_BRANDS' | 'SPONSORED_DISPLAY';
  targetingType: 'MANUAL' | 'AUTOMATIC';
  dailyBudget: number;
  status: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  biddingStrategy: 'MANUAL' | 'DYNAMIC_DOWN' | 'DYNAMIC_UP_DOWN';
  startDate: string;
  endDate?: string;
  totalBudget?: number;
  totalImpressions: string;
  totalClicks: number;
  totalConversions: number;
  totalSpend: string;
  totalSales: string;
  createdAt: string;
  updatedAt: string;
}

export interface CampaignStats {
  totalImpressions: string;
  totalClicks: number;
  totalConversions: number;
  totalSpend: string;
  totalSales: string;
  ctr: string;
  cvr: string;
  acos: string;
  roas: string;
}

export interface CreateCampaignDto {
  name: string;
  campaignType?: 'SPONSORED_PRODUCTS' | 'SPONSORED_BRANDS' | 'SPONSORED_DISPLAY';
  targetingType?: 'MANUAL' | 'AUTOMATIC';
  dailyBudget: number;
  biddingStrategy?: 'MANUAL' | 'DYNAMIC_DOWN' | 'DYNAMIC_UP_DOWN';
  startDate?: string;
  endDate?: string;
  totalBudget?: number;
}

export interface UpdateCampaignDto {
  name?: string;
  dailyBudget?: number;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  biddingStrategy?: 'MANUAL' | 'DYNAMIC_DOWN' | 'DYNAMIC_UP_DOWN';
  endDate?: string;
  totalBudget?: number;
}
