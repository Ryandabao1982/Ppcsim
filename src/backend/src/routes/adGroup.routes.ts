import { Router, Request, Response, NextFunction } from 'express';
import { adGroupController } from '../controllers/adGroup.controller';
import { authenticate } from '../middleware/auth';
import { adGroupValidation } from '../middleware/validation';
import { writeLimiter } from '../middleware/rateLimiter';

const router = Router({ mergeParams: true }); // mergeParams allows access to campaignId from parent route

// Apply authentication to all ad group routes
router.use(authenticate);

/**
 * @route   POST /api/campaigns/:campaignId/adgroups
 * @desc    Create a new ad group
 * @access  Private
 */
router.post('/', writeLimiter, adGroupValidation.create, (req: Request, res: Response, next: NextFunction) => 
  adGroupController.createAdGroup(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/adgroups
 * @desc    Get all ad groups for a campaign
 * @access  Private
 */
router.get('/', adGroupValidation.list, (req: Request, res: Response, next: NextFunction) => 
  adGroupController.getAdGroups(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/adgroups/:id
 * @desc    Get a single ad group by ID
 * @access  Private
 */
router.get('/:id', adGroupValidation.get, (req: Request, res: Response, next: NextFunction) => 
  adGroupController.getAdGroup(req, res, next)
);

/**
 * @route   PUT /api/campaigns/:campaignId/adgroups/:id
 * @desc    Update an ad group
 * @access  Private
 */
router.put('/:id', writeLimiter, adGroupValidation.update, (req: Request, res: Response, next: NextFunction) => 
  adGroupController.updateAdGroup(req, res, next)
);

/**
 * @route   DELETE /api/campaigns/:campaignId/adgroups/:id
 * @desc    Delete an ad group
 * @access  Private
 */
router.delete('/:id', writeLimiter, adGroupValidation.get, (req: Request, res: Response, next: NextFunction) => 
  adGroupController.deleteAdGroup(req, res, next)
);

export default router;
