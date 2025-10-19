import { Request, Response, NextFunction } from 'express';
import { campaignService } from '../services/campaign.service';
import { ValidationError } from '../utils/errors';

export class CampaignController {
  /**
   * Create a new campaign
   * POST /api/campaigns
   */
  async createCampaign(req: Request, res: Response, next: NextFunction) {
    try {
      // TODO: Get userId from authenticated user
      const userId = req.body.userId || 1; // Temporary until auth is implemented

      const campaign = await campaignService.createCampaign({
        userId,
        name: req.body.name,
        campaignType: req.body.campaignType,
        targetingType: req.body.targetingType,
        dailyBudget: parseFloat(req.body.dailyBudget),
        biddingStrategy: req.body.biddingStrategy,
        startDate: req.body.startDate ? new Date(req.body.startDate) : undefined,
        endDate: req.body.endDate ? new Date(req.body.endDate) : undefined,
        totalBudget: req.body.totalBudget ? parseFloat(req.body.totalBudget) : undefined,
      });

      res.status(201).json({
        status: 'success',
        data: { campaign },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get all campaigns for the authenticated user
   * GET /api/campaigns
   */
  async getCampaigns(req: Request, res: Response, next: NextFunction) {
    try {
      // TODO: Get userId from authenticated user
      const userId = parseInt(req.query.userId as string) || 1; // Temporary

      const filters = {
        status: req.query.status as any,
        campaignType: req.query.campaignType as any,
      };

      const campaigns = await campaignService.getUserCampaigns(userId, filters);

      res.json({
        status: 'success',
        data: { campaigns },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single campaign by ID
   * GET /api/campaigns/:id
   */
  async getCampaign(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      // TODO: Get userId from authenticated user
      const userId = parseInt(req.query.userId as string) || 1; // Temporary

      if (isNaN(id)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const campaign = await campaignService.getCampaignById(id, userId);

      res.json({
        status: 'success',
        data: { campaign },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update a campaign
   * PUT /api/campaigns/:id
   */
  async updateCampaign(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      // TODO: Get userId from authenticated user
      const userId = req.body.userId || 1; // Temporary

      if (isNaN(id)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const updateData = {
        name: req.body.name,
        dailyBudget: req.body.dailyBudget ? parseFloat(req.body.dailyBudget) : undefined,
        status: req.body.status,
        biddingStrategy: req.body.biddingStrategy,
        endDate: req.body.endDate ? new Date(req.body.endDate) : undefined,
        totalBudget: req.body.totalBudget ? parseFloat(req.body.totalBudget) : undefined,
      };

      // Remove undefined values
      Object.keys(updateData).forEach(key => 
        updateData[key as keyof typeof updateData] === undefined && delete updateData[key as keyof typeof updateData]
      );

      const campaign = await campaignService.updateCampaign(id, userId, updateData);

      res.json({
        status: 'success',
        data: { campaign },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Delete a campaign
   * DELETE /api/campaigns/:id
   */
  async deleteCampaign(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      // TODO: Get userId from authenticated user
      const userId = parseInt(req.query.userId as string) || 1; // Temporary

      if (isNaN(id)) {
        throw new ValidationError('Invalid campaign ID');
      }

      await campaignService.deleteCampaign(id, userId);

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get campaign statistics
   * GET /api/campaigns/:id/stats
   */
  async getCampaignStats(req: Request, res: Response, next: NextFunction) {
    try {
      const id = parseInt(req.params.id);
      // TODO: Get userId from authenticated user
      const userId = parseInt(req.query.userId as string) || 1; // Temporary

      if (isNaN(id)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const stats = await campaignService.getCampaignStats(id, userId);

      res.json({
        status: 'success',
        data: { stats },
      });
    } catch (error) {
      next(error);
    }
  }
}

export const campaignController = new CampaignController();
