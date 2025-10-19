import { Campaign, Prisma } from '@prisma/client';
import { prisma } from '../database/client';
import { NotFoundError, ValidationError } from '../utils/errors';

export interface CreateCampaignDto {
  userId: number;
  name: string;
  campaignType?: 'SPONSORED_PRODUCTS' | 'SPONSORED_BRANDS' | 'SPONSORED_DISPLAY';
  targetingType?: 'MANUAL' | 'AUTOMATIC';
  dailyBudget: number;
  biddingStrategy?: 'MANUAL' | 'DYNAMIC_DOWN' | 'DYNAMIC_UP_DOWN';
  startDate?: Date;
  endDate?: Date;
  totalBudget?: number;
}

export interface UpdateCampaignDto {
  name?: string;
  dailyBudget?: number;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  biddingStrategy?: 'MANUAL' | 'DYNAMIC_DOWN' | 'DYNAMIC_UP_DOWN';
  endDate?: Date;
  totalBudget?: number;
}

export class CampaignService {
  /**
   * Create a new campaign
   */
  async createCampaign(data: CreateCampaignDto): Promise<Campaign> {
    // Validate budget
    if (data.dailyBudget <= 0) {
      throw new ValidationError('Daily budget must be greater than 0');
    }

    if (data.totalBudget && data.totalBudget <= 0) {
      throw new ValidationError('Total budget must be greater than 0');
    }

    // Create campaign
    const campaign = await prisma.campaign.create({
      data: {
        userId: data.userId,
        name: data.name,
        campaignType: data.campaignType || 'SPONSORED_PRODUCTS',
        targetingType: data.targetingType || 'MANUAL',
        dailyBudget: data.dailyBudget,
        biddingStrategy: data.biddingStrategy || 'MANUAL',
        startDate: data.startDate || new Date(),
        endDate: data.endDate,
        totalBudget: data.totalBudget,
      },
    });

    return campaign;
  }

  /**
   * Get all campaigns for a user
   */
  async getUserCampaigns(userId: number, filters?: {
    status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
    campaignType?: 'SPONSORED_PRODUCTS' | 'SPONSORED_BRANDS' | 'SPONSORED_DISPLAY';
  }): Promise<Campaign[]> {
    const where: Prisma.CampaignWhereInput = {
      userId,
      ...(filters?.status && { status: filters.status }),
      ...(filters?.campaignType && { campaignType: filters.campaignType }),
    };

    const campaigns = await prisma.campaign.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });

    return campaigns;
  }

  /**
   * Get a single campaign by ID
   */
  async getCampaignById(id: number, userId: number): Promise<Campaign> {
    const campaign = await prisma.campaign.findFirst({
      where: { id, userId },
    });

    if (!campaign) {
      throw new NotFoundError('Campaign not found');
    }

    return campaign;
  }

  /**
   * Update a campaign
   */
  async updateCampaign(id: number, userId: number, data: UpdateCampaignDto): Promise<Campaign> {
    // Check if campaign exists and belongs to user
    await this.getCampaignById(id, userId);

    // Validate budget if provided
    if (data.dailyBudget !== undefined && data.dailyBudget <= 0) {
      throw new ValidationError('Daily budget must be greater than 0');
    }

    if (data.totalBudget !== undefined && data.totalBudget <= 0) {
      throw new ValidationError('Total budget must be greater than 0');
    }

    // Update campaign
    const campaign = await prisma.campaign.update({
      where: { id },
      data,
    });

    return campaign;
  }

  /**
   * Delete a campaign (soft delete by archiving)
   */
  async deleteCampaign(id: number, userId: number): Promise<void> {
    // Check if campaign exists and belongs to user
    await this.getCampaignById(id, userId);

    // Soft delete by archiving
    await prisma.campaign.update({
      where: { id },
      data: { status: 'ARCHIVED' },
    });
  }

  /**
   * Get campaign statistics
   */
  async getCampaignStats(id: number, userId: number) {
    const campaign = await this.getCampaignById(id, userId);

    return {
      totalImpressions: campaign.totalImpressions.toString(),
      totalClicks: campaign.totalClicks,
      totalConversions: campaign.totalConversions,
      totalSpend: campaign.totalSpend.toString(),
      totalSales: campaign.totalSales.toString(),
      ctr: campaign.totalImpressions > 0 
        ? (Number(campaign.totalClicks) / Number(campaign.totalImpressions) * 100).toFixed(2)
        : '0.00',
      cvr: campaign.totalClicks > 0 
        ? (campaign.totalConversions / campaign.totalClicks * 100).toFixed(2)
        : '0.00',
      acos: Number(campaign.totalSales) > 0 
        ? (Number(campaign.totalSpend) / Number(campaign.totalSales) * 100).toFixed(2)
        : '0.00',
      roas: Number(campaign.totalSpend) > 0 
        ? (Number(campaign.totalSales) / Number(campaign.totalSpend)).toFixed(2)
        : '0.00',
    };
  }
}

export const campaignService = new CampaignService();
