import { body, param, query, validationResult } from 'express-validator';
import { Request, Response, NextFunction } from 'express';
import { ValidationError } from '../utils/errors';

// Middleware to check validation results
export const validate = (req: Request, res: Response, next: NextFunction) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map(err => err.msg).join(', ');
    throw new ValidationError(errorMessages);
  }
  next();
};

// Campaign validation rules
export const campaignValidation = {
  create: [
    body('name').trim().notEmpty().withMessage('Campaign name is required')
      .isLength({ max: 255 }).withMessage('Campaign name must be less than 255 characters'),
    body('dailyBudget').isFloat({ min: 0.01 }).withMessage('Daily budget must be greater than 0'),
    body('totalBudget').optional().isFloat({ min: 0.01 }).withMessage('Total budget must be greater than 0'),
    body('campaignType').optional().isIn(['SPONSORED_PRODUCTS', 'SPONSORED_BRANDS', 'SPONSORED_DISPLAY'])
      .withMessage('Invalid campaign type'),
    body('targetingType').optional().isIn(['MANUAL', 'AUTOMATIC']).withMessage('Invalid targeting type'),
    body('biddingStrategy').optional().isIn(['MANUAL', 'DYNAMIC_DOWN', 'DYNAMIC_UP_DOWN'])
      .withMessage('Invalid bidding strategy'),
    validate,
  ],
  update: [
    param('id').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    body('name').optional().trim().notEmpty().withMessage('Campaign name cannot be empty')
      .isLength({ max: 255 }).withMessage('Campaign name must be less than 255 characters'),
    body('dailyBudget').optional().isFloat({ min: 0.01 }).withMessage('Daily budget must be greater than 0'),
    body('totalBudget').optional().isFloat({ min: 0.01 }).withMessage('Total budget must be greater than 0'),
    body('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    validate,
  ],
  get: [
    param('id').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    validate,
  ],
  list: [
    query('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    query('campaignType').optional().isIn(['SPONSORED_PRODUCTS', 'SPONSORED_BRANDS', 'SPONSORED_DISPLAY'])
      .withMessage('Invalid campaign type'),
    validate,
  ],
};

// Keyword validation rules
export const keywordValidation = {
  create: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    body('keywordText').trim().notEmpty().withMessage('Keyword text is required')
      .isLength({ max: 255 }).withMessage('Keyword text must be less than 255 characters'),
    body('matchType').isIn(['BROAD', 'PHRASE', 'EXACT']).withMessage('Invalid match type'),
    body('bid').isFloat({ min: 0.01 }).withMessage('Bid must be greater than 0'),
    body('adGroupId').optional().isInt({ min: 1 }).withMessage('Invalid ad group ID'),
    body('isNegative').optional().isBoolean().withMessage('isNegative must be a boolean'),
    validate,
  ],
  update: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    param('id').isInt({ min: 1 }).withMessage('Invalid keyword ID'),
    body('keywordText').optional().trim().notEmpty().withMessage('Keyword text cannot be empty')
      .isLength({ max: 255 }).withMessage('Keyword text must be less than 255 characters'),
    body('matchType').optional().isIn(['BROAD', 'PHRASE', 'EXACT']).withMessage('Invalid match type'),
    body('bid').optional().isFloat({ min: 0.01 }).withMessage('Bid must be greater than 0'),
    body('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    validate,
  ],
  get: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    param('id').isInt({ min: 1 }).withMessage('Invalid keyword ID'),
    validate,
  ],
  list: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    query('matchType').optional().isIn(['BROAD', 'PHRASE', 'EXACT']).withMessage('Invalid match type'),
    query('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    query('isNegative').optional().isBoolean().withMessage('isNegative must be a boolean'),
    validate,
  ],
  bulk: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    body('keywords').isArray({ min: 1 }).withMessage('Keywords must be a non-empty array'),
    body('keywords.*.keywordText').trim().notEmpty().withMessage('Keyword text is required'),
    body('keywords.*.matchType').isIn(['BROAD', 'PHRASE', 'EXACT']).withMessage('Invalid match type'),
    body('keywords.*.bid').isFloat({ min: 0.01 }).withMessage('Bid must be greater than 0'),
    validate,
  ],
};

// Ad Group validation rules
export const adGroupValidation = {
  create: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    body('name').trim().notEmpty().withMessage('Ad group name is required')
      .isLength({ max: 255 }).withMessage('Ad group name must be less than 255 characters'),
    body('defaultBid').isFloat({ min: 0.01 }).withMessage('Default bid must be greater than 0'),
    validate,
  ],
  update: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    param('id').isInt({ min: 1 }).withMessage('Invalid ad group ID'),
    body('name').optional().trim().notEmpty().withMessage('Ad group name cannot be empty')
      .isLength({ max: 255 }).withMessage('Ad group name must be less than 255 characters'),
    body('defaultBid').optional().isFloat({ min: 0.01 }).withMessage('Default bid must be greater than 0'),
    body('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    validate,
  ],
  get: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    param('id').isInt({ min: 1 }).withMessage('Invalid ad group ID'),
    validate,
  ],
  list: [
    param('campaignId').isInt({ min: 1 }).withMessage('Invalid campaign ID'),
    query('status').optional().isIn(['ACTIVE', 'PAUSED', 'ARCHIVED']).withMessage('Invalid status'),
    validate,
  ],
};
