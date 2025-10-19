import { keywordService } from '../services/keyword.service';
import { prisma } from '../database/client';

// Mock Prisma
jest.mock('../database/client', () => ({
  prisma: {
    keyword: {
      create: jest.fn(),
      findMany: jest.fn(),
      findFirst: jest.fn(),
      update: jest.fn(),
    },
    campaign: {
      findUnique: jest.fn(),
    },
    adGroup: {
      findUnique: jest.fn(),
    },
  },
}));

describe('KeywordService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createKeyword', () => {
    it('should create a keyword with valid data', async () => {
      const mockCampaign = { id: 1, userId: 1 };
      const mockKeyword = {
        id: 1,
        campaignId: 1,
        adGroupId: null,
        keywordText: 'test keyword',
        matchType: 'EXACT',
        bid: 1.5,
        status: 'ACTIVE',
        isNegative: false,
        impressions: BigInt(0),
        clicks: 0,
        conversions: 0,
        spend: 0.00,
        sales: 0.00,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      (prisma.campaign.findUnique as jest.Mock).mockResolvedValue(mockCampaign);
      (prisma.keyword.create as jest.Mock).mockResolvedValue(mockKeyword);

      const result = await keywordService.createKeyword({
        campaignId: 1,
        keywordText: 'test keyword',
        matchType: 'EXACT',
        bid: 1.5,
      });

      expect(result).toEqual(mockKeyword);
      expect(prisma.campaign.findUnique).toHaveBeenCalledWith({
        where: { id: 1 },
      });
    });

    it('should throw error for invalid bid', async () => {
      await expect(
        keywordService.createKeyword({
          campaignId: 1,
          keywordText: 'test',
          matchType: 'EXACT',
          bid: -1,
        })
      ).rejects.toThrow('Bid must be greater than 0');
    });

    it('should throw error for empty keyword text', async () => {
      await expect(
        keywordService.createKeyword({
          campaignId: 1,
          keywordText: '   ',
          matchType: 'EXACT',
          bid: 1.5,
        })
      ).rejects.toThrow('Keyword text cannot be empty');
    });
  });

  describe('getCampaignKeywords', () => {
    it('should return keywords for a campaign', async () => {
      const mockKeywords = [
        {
          id: 1,
          campaignId: 1,
          keywordText: 'keyword 1',
          matchType: 'EXACT',
          bid: 1.5,
        },
      ];

      (prisma.keyword.findMany as jest.Mock).mockResolvedValue(mockKeywords);

      const result = await keywordService.getCampaignKeywords(1);

      expect(result).toEqual(mockKeywords);
      expect(prisma.keyword.findMany).toHaveBeenCalledWith({
        where: { campaignId: 1 },
        orderBy: { createdAt: 'desc' },
      });
    });

    it('should filter keywords by match type', async () => {
      const mockKeywords = [
        {
          id: 1,
          campaignId: 1,
          keywordText: 'keyword 1',
          matchType: 'EXACT',
          bid: 1.5,
        },
      ];

      (prisma.keyword.findMany as jest.Mock).mockResolvedValue(mockKeywords);

      await keywordService.getCampaignKeywords(1, { matchType: 'EXACT' });

      expect(prisma.keyword.findMany).toHaveBeenCalledWith({
        where: { campaignId: 1, matchType: 'EXACT' },
        orderBy: { createdAt: 'desc' },
      });
    });
  });

  describe('getNegativeKeywords', () => {
    it('should return only negative keywords', async () => {
      const mockNegativeKeywords = [
        {
          id: 1,
          campaignId: 1,
          keywordText: 'negative keyword',
          matchType: 'EXACT',
          bid: 0,
          isNegative: true,
        },
      ];

      (prisma.keyword.findMany as jest.Mock).mockResolvedValue(mockNegativeKeywords);

      await keywordService.getNegativeKeywords(1);

      expect(prisma.keyword.findMany).toHaveBeenCalledWith({
        where: { campaignId: 1, isNegative: true },
        orderBy: { createdAt: 'desc' },
      });
    });
  });
});
