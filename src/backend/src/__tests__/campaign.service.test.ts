import { campaignService } from '../services/campaign.service';
import { prisma } from '../database/client';

// Mock Prisma
jest.mock('../database/client', () => ({
  prisma: {
    campaign: {
      create: jest.fn(),
      findMany: jest.fn(),
      findFirst: jest.fn(),
      update: jest.fn(),
    },
  },
}));

describe('CampaignService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createCampaign', () => {
    it('should create a campaign with valid data', async () => {
      const mockCampaign = {
        id: 1,
        userId: 1,
        name: 'Test Campaign',
        campaignType: 'SPONSORED_PRODUCTS',
        targetingType: 'MANUAL',
        dailyBudget: 50.00,
        status: 'ACTIVE',
        biddingStrategy: 'MANUAL',
        startDate: new Date(),
        endDate: null,
        totalBudget: null,
        totalImpressions: BigInt(0),
        totalClicks: 0,
        totalConversions: 0,
        totalSpend: 0.00,
        totalSales: 0.00,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      (prisma.campaign.create as jest.Mock).mockResolvedValue(mockCampaign);

      const result = await campaignService.createCampaign({
        userId: 1,
        name: 'Test Campaign',
        dailyBudget: 50.00,
      });

      expect(result).toEqual(mockCampaign);
      expect(prisma.campaign.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          userId: 1,
          name: 'Test Campaign',
          dailyBudget: 50.00,
        }),
      });
    });

    it('should throw error for invalid budget', async () => {
      await expect(
        campaignService.createCampaign({
          userId: 1,
          name: 'Test Campaign',
          dailyBudget: -10,
        })
      ).rejects.toThrow('Daily budget must be greater than 0');
    });
  });

  describe('getUserCampaigns', () => {
    it('should return campaigns for a user', async () => {
      const mockCampaigns = [
        {
          id: 1,
          userId: 1,
          name: 'Campaign 1',
          campaignType: 'SPONSORED_PRODUCTS',
          targetingType: 'MANUAL',
          dailyBudget: 50.00,
          status: 'ACTIVE',
          biddingStrategy: 'MANUAL',
          startDate: new Date(),
          endDate: null,
          totalBudget: null,
          totalImpressions: BigInt(0),
          totalClicks: 0,
          totalConversions: 0,
          totalSpend: 0.00,
          totalSales: 0.00,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      (prisma.campaign.findMany as jest.Mock).mockResolvedValue(mockCampaigns);

      const result = await campaignService.getUserCampaigns(1);

      expect(result).toEqual(mockCampaigns);
      expect(prisma.campaign.findMany).toHaveBeenCalledWith({
        where: { userId: 1 },
        orderBy: { createdAt: 'desc' },
      });
    });
  });
});
