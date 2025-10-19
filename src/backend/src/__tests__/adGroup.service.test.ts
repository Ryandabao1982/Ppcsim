import { adGroupService } from '../services/adGroup.service';
import { prisma } from '../database/client';

// Mock Prisma
jest.mock('../database/client', () => ({
  prisma: {
    adGroup: {
      create: jest.fn(),
      findMany: jest.fn(),
      findFirst: jest.fn(),
      update: jest.fn(),
    },
    campaign: {
      findUnique: jest.fn(),
    },
  },
}));

describe('AdGroupService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createAdGroup', () => {
    it('should create an ad group with valid data', async () => {
      const mockCampaign = { id: 1, userId: 1 };
      const mockAdGroup = {
        id: 1,
        campaignId: 1,
        name: 'Test Ad Group',
        defaultBid: 2.0,
        status: 'ACTIVE',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      (prisma.campaign.findUnique as jest.Mock).mockResolvedValue(mockCampaign);
      (prisma.adGroup.create as jest.Mock).mockResolvedValue(mockAdGroup);

      const result = await adGroupService.createAdGroup({
        campaignId: 1,
        name: 'Test Ad Group',
        defaultBid: 2.0,
      });

      expect(result).toEqual(mockAdGroup);
      expect(prisma.campaign.findUnique).toHaveBeenCalledWith({
        where: { id: 1 },
      });
    });

    it('should throw error for invalid bid', async () => {
      await expect(
        adGroupService.createAdGroup({
          campaignId: 1,
          name: 'Test Ad Group',
          defaultBid: -1,
        })
      ).rejects.toThrow('Default bid must be greater than 0');
    });

    it('should throw error for empty name', async () => {
      await expect(
        adGroupService.createAdGroup({
          campaignId: 1,
          name: '   ',
          defaultBid: 2.0,
        })
      ).rejects.toThrow('Ad group name cannot be empty');
    });
  });

  describe('getCampaignAdGroups', () => {
    it('should return ad groups for a campaign', async () => {
      const mockAdGroups = [
        {
          id: 1,
          campaignId: 1,
          name: 'Ad Group 1',
          defaultBid: 2.0,
          status: 'ACTIVE',
          _count: { keywords: 5, products: 3 },
        },
      ];

      (prisma.adGroup.findMany as jest.Mock).mockResolvedValue(mockAdGroups);

      const result = await adGroupService.getCampaignAdGroups(1);

      expect(result).toEqual(mockAdGroups);
      expect(prisma.adGroup.findMany).toHaveBeenCalledWith({
        where: { campaignId: 1 },
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
    });

    it('should filter ad groups by status', async () => {
      const mockAdGroups = [
        {
          id: 1,
          campaignId: 1,
          name: 'Ad Group 1',
          status: 'ACTIVE',
        },
      ];

      (prisma.adGroup.findMany as jest.Mock).mockResolvedValue(mockAdGroups);

      await adGroupService.getCampaignAdGroups(1, { status: 'ACTIVE' });

      expect(prisma.adGroup.findMany).toHaveBeenCalledWith({
        where: { campaignId: 1, status: 'ACTIVE' },
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
    });
  });
});
