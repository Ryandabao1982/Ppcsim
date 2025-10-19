import { AdGroup, Prisma } from '@prisma/client';
import { prisma } from '../database/client';
import { NotFoundError, ValidationError } from '../utils/errors';

export interface CreateAdGroupDto {
  campaignId: number;
  name: string;
  defaultBid: number;
}

export interface UpdateAdGroupDto {
  name?: string;
  defaultBid?: number;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
}

export class AdGroupService {
  /**
   * Create a new ad group
   */
  async createAdGroup(data: CreateAdGroupDto): Promise<AdGroup> {
    // Validate bid
    if (data.defaultBid <= 0) {
      throw new ValidationError('Default bid must be greater than 0');
    }

    // Validate name
    if (!data.name.trim()) {
      throw new ValidationError('Ad group name cannot be empty');
    }

    // Check if campaign exists
    const campaign = await prisma.campaign.findUnique({
      where: { id: data.campaignId },
    });

    if (!campaign) {
      throw new NotFoundError('Campaign not found');
    }

    // Create ad group
    const adGroup = await prisma.adGroup.create({
      data: {
        campaignId: data.campaignId,
        name: data.name.trim(),
        defaultBid: data.defaultBid,
      },
    });

    return adGroup;
  }

  /**
   * Get all ad groups for a campaign
   */
  async getCampaignAdGroups(campaignId: number, filters?: {
    status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  }): Promise<AdGroup[]> {
    const where: Prisma.AdGroupWhereInput = {
      campaignId,
      ...(filters?.status && { status: filters.status }),
    };

    const adGroups = await prisma.adGroup.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        _count: {
          select: {
            keywords: true,
            products: true,
          },
        },
      },
    });

    return adGroups;
  }

  /**
   * Get a single ad group by ID
   */
  async getAdGroupById(id: number, campaignId: number): Promise<AdGroup> {
    const adGroup = await prisma.adGroup.findFirst({
      where: { id, campaignId },
      include: {
        _count: {
          select: {
            keywords: true,
            products: true,
          },
        },
      },
    });

    if (!adGroup) {
      throw new NotFoundError('Ad group not found');
    }

    return adGroup;
  }

  /**
   * Update an ad group
   */
  async updateAdGroup(id: number, campaignId: number, data: UpdateAdGroupDto): Promise<AdGroup> {
    // Check if ad group exists and belongs to campaign
    await this.getAdGroupById(id, campaignId);

    // Validate bid if provided
    if (data.defaultBid !== undefined && data.defaultBid <= 0) {
      throw new ValidationError('Default bid must be greater than 0');
    }

    // Validate name if provided
    if (data.name !== undefined && !data.name.trim()) {
      throw new ValidationError('Ad group name cannot be empty');
    }

    // Update ad group
    const adGroup = await prisma.adGroup.update({
      where: { id },
      data: {
        ...(data.name && { name: data.name.trim() }),
        ...(data.defaultBid !== undefined && { defaultBid: data.defaultBid }),
        ...(data.status && { status: data.status }),
      },
    });

    return adGroup;
  }

  /**
   * Delete an ad group (soft delete by archiving)
   */
  async deleteAdGroup(id: number, campaignId: number): Promise<void> {
    // Check if ad group exists and belongs to campaign
    await this.getAdGroupById(id, campaignId);

    // Soft delete by archiving
    await prisma.adGroup.update({
      where: { id },
      data: { status: 'ARCHIVED' },
    });
  }
}

export const adGroupService = new AdGroupService();
