import { Keyword, Prisma } from '@prisma/client';
import { prisma } from '../database/client';
import { NotFoundError, ValidationError } from '../utils/errors';

export interface CreateKeywordDto {
  campaignId: number;
  adGroupId?: number;
  keywordText: string;
  matchType: 'BROAD' | 'PHRASE' | 'EXACT';
  bid: number;
  isNegative?: boolean;
}

export interface UpdateKeywordDto {
  keywordText?: string;
  matchType?: 'BROAD' | 'PHRASE' | 'EXACT';
  bid?: number;
  status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
  isNegative?: boolean;
}

export interface BulkKeywordDto {
  keywords: CreateKeywordDto[];
}

export class KeywordService {
  /**
   * Create a new keyword
   */
  async createKeyword(data: CreateKeywordDto): Promise<Keyword> {
    // Validate bid
    if (data.bid <= 0) {
      throw new ValidationError('Bid must be greater than 0');
    }

    // Validate keyword text
    if (!data.keywordText.trim()) {
      throw new ValidationError('Keyword text cannot be empty');
    }

    // Check if campaign exists
    const campaign = await prisma.campaign.findUnique({
      where: { id: data.campaignId },
    });

    if (!campaign) {
      throw new NotFoundError('Campaign not found');
    }

    // Check if ad group exists (if provided)
    if (data.adGroupId) {
      const adGroup = await prisma.adGroup.findUnique({
        where: { id: data.adGroupId },
      });

      if (!adGroup) {
        throw new NotFoundError('Ad group not found');
      }

      // Verify ad group belongs to campaign
      if (adGroup.campaignId !== data.campaignId) {
        throw new ValidationError('Ad group does not belong to the specified campaign');
      }
    }

    // Create keyword
    const keyword = await prisma.keyword.create({
      data: {
        campaignId: data.campaignId,
        adGroupId: data.adGroupId,
        keywordText: data.keywordText.trim(),
        matchType: data.matchType,
        bid: data.bid,
        isNegative: data.isNegative || false,
      },
    });

    return keyword;
  }

  /**
   * Get all keywords for a campaign
   */
  async getCampaignKeywords(campaignId: number, filters?: {
    adGroupId?: number;
    matchType?: 'BROAD' | 'PHRASE' | 'EXACT';
    status?: 'ACTIVE' | 'PAUSED' | 'ARCHIVED';
    isNegative?: boolean;
  }): Promise<Keyword[]> {
    const where: Prisma.KeywordWhereInput = {
      campaignId,
      ...(filters?.adGroupId && { adGroupId: filters.adGroupId }),
      ...(filters?.matchType && { matchType: filters.matchType }),
      ...(filters?.status && { status: filters.status }),
      ...(filters?.isNegative !== undefined && { isNegative: filters.isNegative }),
    };

    const keywords = await prisma.keyword.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });

    return keywords;
  }

  /**
   * Get a single keyword by ID
   */
  async getKeywordById(id: number, campaignId: number): Promise<Keyword> {
    const keyword = await prisma.keyword.findFirst({
      where: { id, campaignId },
    });

    if (!keyword) {
      throw new NotFoundError('Keyword not found');
    }

    return keyword;
  }

  /**
   * Update a keyword
   */
  async updateKeyword(id: number, campaignId: number, data: UpdateKeywordDto): Promise<Keyword> {
    // Check if keyword exists and belongs to campaign
    await this.getKeywordById(id, campaignId);

    // Validate bid if provided
    if (data.bid !== undefined && data.bid <= 0) {
      throw new ValidationError('Bid must be greater than 0');
    }

    // Validate keyword text if provided
    if (data.keywordText !== undefined && !data.keywordText.trim()) {
      throw new ValidationError('Keyword text cannot be empty');
    }

    // Update keyword
    const keyword = await prisma.keyword.update({
      where: { id },
      data: {
        ...(data.keywordText && { keywordText: data.keywordText.trim() }),
        ...(data.matchType && { matchType: data.matchType }),
        ...(data.bid !== undefined && { bid: data.bid }),
        ...(data.status && { status: data.status }),
        ...(data.isNegative !== undefined && { isNegative: data.isNegative }),
      },
    });

    return keyword;
  }

  /**
   * Delete a keyword (soft delete by archiving)
   */
  async deleteKeyword(id: number, campaignId: number): Promise<void> {
    // Check if keyword exists and belongs to campaign
    await this.getKeywordById(id, campaignId);

    // Soft delete by archiving
    await prisma.keyword.update({
      where: { id },
      data: { status: 'ARCHIVED' },
    });
  }

  /**
   * Bulk create keywords
   */
  async bulkCreateKeywords(data: BulkKeywordDto): Promise<Keyword[]> {
    const keywords: Keyword[] = [];

    const keywords = await Promise.all(
      data.keywords.map((keywordData) => this.createKeyword(keywordData))
    );

    return keywords;
  }

  /**
   * Get keyword statistics
   */
  async getKeywordStats(id: number, campaignId: number) {
    const keyword = await this.getKeywordById(id, campaignId);

    return {
      impressions: keyword.impressions.toString(),
      clicks: keyword.clicks,
      conversions: keyword.conversions,
      spend: keyword.spend.toString(),
      sales: keyword.sales.toString(),
      ctr: keyword.impressions > 0 
        ? (Number(keyword.clicks) / Number(keyword.impressions) * 100).toFixed(2)
        : '0.00',
      cvr: keyword.clicks > 0 
        ? (keyword.conversions / keyword.clicks * 100).toFixed(2)
        : '0.00',
      cpc: keyword.clicks > 0 
        ? (Number(keyword.spend) / keyword.clicks).toFixed(2)
        : '0.00',
      acos: Number(keyword.sales) > 0 
        ? (Number(keyword.spend) / Number(keyword.sales) * 100).toFixed(2)
        : '0.00',
    };
  }

  /**
   * Get negative keywords for a campaign
   */
  async getNegativeKeywords(campaignId: number): Promise<Keyword[]> {
    return this.getCampaignKeywords(campaignId, { isNegative: true });
  }
}

export const keywordService = new KeywordService();
