import { Router, Request, Response, NextFunction } from 'express';
import { campaignController } from '../controllers/campaign.controller';
import { authenticate } from '../middleware/auth';
import { campaignValidation } from '../middleware/validation';
import { writeLimiter } from '../middleware/rateLimiter';

const router = Router();

// Apply authentication to all campaign routes
router.use(authenticate);

/**
 * @route   POST /api/campaigns
 * @desc    Create a new campaign
 * @access  Private
 */
router.post('/', writeLimiter, campaignValidation.create, (req: Request, res: Response, next: NextFunction) => 
  campaignController.createCampaign(req, res, next)
);

/**
 * @route   GET /api/campaigns
 * @desc    Get all campaigns for the authenticated user
 * @access  Private
 */
router.get('/', campaignValidation.list, (req: Request, res: Response, next: NextFunction) => 
  campaignController.getCampaigns(req, res, next)
);

/**
 * @route   GET /api/campaigns/:id
 * @desc    Get a single campaign by ID
 * @access  Private
 */
router.get('/:id', campaignValidation.get, (req: Request, res: Response, next: NextFunction) => 
  campaignController.getCampaign(req, res, next)
);

/**
 * @route   PUT /api/campaigns/:id
 * @desc    Update a campaign
 * @access  Private
 */
router.put('/:id', writeLimiter, campaignValidation.update, (req: Request, res: Response, next: NextFunction) => 
  campaignController.updateCampaign(req, res, next)
);

/**
 * @route   DELETE /api/campaigns/:id
 * @desc    Delete a campaign (archive)
 * @access  Private
 */
router.delete('/:id', writeLimiter, campaignValidation.get, (req: Request, res: Response, next: NextFunction) => 
  campaignController.deleteCampaign(req, res, next)
);

/**
 * @route   GET /api/campaigns/:id/stats
 * @desc    Get campaign statistics
 * @access  Private
 */
router.get('/:id/stats', campaignValidation.get, (req: Request, res: Response, next: NextFunction) => 
  campaignController.getCampaignStats(req, res, next)
);

export default router;
