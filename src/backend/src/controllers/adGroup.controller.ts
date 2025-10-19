import { Request, Response, NextFunction } from 'express';
import { adGroupService } from '../services/adGroup.service';
import { ValidationError } from '../utils/errors';

export class AdGroupController {
  /**
   * Create a new ad group
   * POST /api/campaigns/:campaignId/adgroups
   */
  async createAdGroup(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const adGroup = await adGroupService.createAdGroup({
        campaignId,
        name: req.body.name,
        defaultBid: parseFloat(req.body.defaultBid),
      });

      res.status(201).json({
        status: 'success',
        data: { adGroup },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get all ad groups for a campaign
   * GET /api/campaigns/:campaignId/adgroups
   */
  async getAdGroups(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const filters = {
        status: req.query.status as any,
      };

      const adGroups = await adGroupService.getCampaignAdGroups(campaignId, filters);

      res.json({
        status: 'success',
        data: { adGroups },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single ad group by ID
   * GET /api/campaigns/:campaignId/adgroups/:id
   */
  async getAdGroup(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or ad group ID');
      }

      const adGroup = await adGroupService.getAdGroupById(id, campaignId);

      res.json({
        status: 'success',
        data: { adGroup },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update an ad group
   * PUT /api/campaigns/:campaignId/adgroups/:id
   */
  async updateAdGroup(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or ad group ID');
      }

      const updateData = {
        name: req.body.name,
        defaultBid: req.body.defaultBid ? parseFloat(req.body.defaultBid) : undefined,
        status: req.body.status,
      };

      // Remove undefined values
      Object.keys(updateData).forEach(key =>
        updateData[key as keyof typeof updateData] === undefined && delete updateData[key as keyof typeof updateData]
      );

      const adGroup = await adGroupService.updateAdGroup(id, campaignId, updateData);

      res.json({
        status: 'success',
        data: { adGroup },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Delete an ad group
   * DELETE /api/campaigns/:campaignId/adgroups/:id
   */
  async deleteAdGroup(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or ad group ID');
      }

      await adGroupService.deleteAdGroup(id, campaignId);

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }
}

export const adGroupController = new AdGroupController();
