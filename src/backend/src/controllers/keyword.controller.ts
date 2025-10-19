import { Request, Response, NextFunction } from 'express';
import { keywordService } from '../services/keyword.service';
import { ValidationError } from '../utils/errors';

export class KeywordController {
  /**
   * Create a new keyword
   * POST /api/campaigns/:campaignId/keywords
   */
  async createKeyword(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const keyword = await keywordService.createKeyword({
        campaignId,
        adGroupId: req.body.adGroupId ? parseInt(req.body.adGroupId) : undefined,
        keywordText: req.body.keywordText,
        matchType: req.body.matchType,
        bid: parseFloat(req.body.bid),
        isNegative: req.body.isNegative,
      });

      res.status(201).json({
        status: 'success',
        data: { keyword },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get all keywords for a campaign
   * GET /api/campaigns/:campaignId/keywords
   */
  async getKeywords(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const filters = {
        adGroupId: req.query.adGroupId ? parseInt(req.query.adGroupId as string) : undefined,
        matchType: req.query.matchType as any,
        status: req.query.status as any,
        isNegative: req.query.isNegative === 'true' ? true : req.query.isNegative === 'false' ? false : undefined,
      };

      const keywords = await keywordService.getCampaignKeywords(campaignId, filters);

      res.json({
        status: 'success',
        data: { keywords },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get negative keywords for a campaign
   * GET /api/campaigns/:campaignId/keywords/negative
   */
  async getNegativeKeywords(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      const keywords = await keywordService.getNegativeKeywords(campaignId);

      res.json({
        status: 'success',
        data: { keywords },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get a single keyword by ID
   * GET /api/campaigns/:campaignId/keywords/:id
   */
  async getKeyword(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or keyword ID');
      }

      const keyword = await keywordService.getKeywordById(id, campaignId);

      res.json({
        status: 'success',
        data: { keyword },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Update a keyword
   * PUT /api/campaigns/:campaignId/keywords/:id
   */
  async updateKeyword(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or keyword ID');
      }

      const updateData = {
        keywordText: req.body.keywordText,
        matchType: req.body.matchType,
        bid: req.body.bid ? parseFloat(req.body.bid) : undefined,
        status: req.body.status,
        isNegative: req.body.isNegative,
      };

      // Remove undefined values
      Object.keys(updateData).forEach(key =>
        updateData[key as keyof typeof updateData] === undefined && delete updateData[key as keyof typeof updateData]
      );

      const keyword = await keywordService.updateKeyword(id, campaignId, updateData);

      res.json({
        status: 'success',
        data: { keyword },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Delete a keyword
   * DELETE /api/campaigns/:campaignId/keywords/:id
   */
  async deleteKeyword(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or keyword ID');
      }

      await keywordService.deleteKeyword(id, campaignId);

      res.status(204).send();
    } catch (error) {
      next(error);
    }
  }

  /**
   * Bulk create keywords
   * POST /api/campaigns/:campaignId/keywords/bulk
   */
  async bulkCreateKeywords(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);

      if (isNaN(campaignId)) {
        throw new ValidationError('Invalid campaign ID');
      }

      if (!Array.isArray(req.body.keywords)) {
        throw new ValidationError('Keywords must be an array');
      }

      // Add campaignId to each keyword
      const keywords = req.body.keywords.map((kw: any) => ({
        ...kw,
        campaignId,
        adGroupId: kw.adGroupId ? parseInt(kw.adGroupId) : undefined,
        bid: parseFloat(kw.bid),
      }));

      const createdKeywords = await keywordService.bulkCreateKeywords({ keywords });

      res.status(201).json({
        status: 'success',
        data: { keywords: createdKeywords },
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * Get keyword statistics
   * GET /api/campaigns/:campaignId/keywords/:id/stats
   */
  async getKeywordStats(req: Request, res: Response, next: NextFunction) {
    try {
      const campaignId = parseInt(req.params.campaignId);
      const id = parseInt(req.params.id);

      if (isNaN(campaignId) || isNaN(id)) {
        throw new ValidationError('Invalid campaign ID or keyword ID');
      }

      const stats = await keywordService.getKeywordStats(id, campaignId);

      res.json({
        status: 'success',
        data: { stats },
      });
    } catch (error) {
      next(error);
    }
  }
}

export const keywordController = new KeywordController();
