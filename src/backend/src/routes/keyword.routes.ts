import { Router, Request, Response, NextFunction } from 'express';
import { keywordController } from '../controllers/keyword.controller';
import { authenticate } from '../middleware/auth';
import { keywordValidation } from '../middleware/validation';
import { writeLimiter, bulkLimiter } from '../middleware/rateLimiter';

const router = Router({ mergeParams: true }); // mergeParams allows access to campaignId from parent route

// Apply authentication to all keyword routes
router.use(authenticate);

/**
 * @route   POST /api/campaigns/:campaignId/keywords
 * @desc    Create a new keyword
 * @access  Private
 */
router.post('/', writeLimiter, keywordValidation.create, (req: Request, res: Response, next: NextFunction) => 
  keywordController.createKeyword(req, res, next)
);

/**
 * @route   POST /api/campaigns/:campaignId/keywords/bulk
 * @desc    Bulk create keywords
 * @access  Private
 */
router.post('/bulk', bulkLimiter, keywordValidation.bulk, (req: Request, res: Response, next: NextFunction) => 
  keywordController.bulkCreateKeywords(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/keywords/negative
 * @desc    Get negative keywords
 * @access  Private
 */
router.get('/negative', keywordValidation.list, (req: Request, res: Response, next: NextFunction) => 
  keywordController.getNegativeKeywords(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/keywords
 * @desc    Get all keywords for a campaign
 * @access  Private
 */
router.get('/', keywordValidation.list, (req: Request, res: Response, next: NextFunction) => 
  keywordController.getKeywords(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/keywords/:id
 * @desc    Get a single keyword by ID
 * @access  Private
 */
router.get('/:id', keywordValidation.get, (req: Request, res: Response, next: NextFunction) => 
  keywordController.getKeyword(req, res, next)
);

/**
 * @route   PUT /api/campaigns/:campaignId/keywords/:id
 * @desc    Update a keyword
 * @access  Private
 */
router.put('/:id', writeLimiter, keywordValidation.update, (req: Request, res: Response, next: NextFunction) => 
  keywordController.updateKeyword(req, res, next)
);

/**
 * @route   DELETE /api/campaigns/:campaignId/keywords/:id
 * @desc    Delete a keyword
 * @access  Private
 */
router.delete('/:id', writeLimiter, keywordValidation.get, (req: Request, res: Response, next: NextFunction) => 
  keywordController.deleteKeyword(req, res, next)
);

/**
 * @route   GET /api/campaigns/:campaignId/keywords/:id/stats
 * @desc    Get keyword statistics
 * @access  Private
 */
router.get('/:id/stats', keywordValidation.get, (req: Request, res: Response, next: NextFunction) => 
  keywordController.getKeywordStats(req, res, next)
);

export default router;
