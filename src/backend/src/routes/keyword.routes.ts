import { Router } from 'express';
import { keywordController } from '../controllers/keyword.controller';

const router = Router({ mergeParams: true }); // mergeParams allows access to campaignId from parent route

/**
 * @route   POST /api/campaigns/:campaignId/keywords
 * @desc    Create a new keyword
 * @access  Private
 */
router.post('/', (req, res, next) => keywordController.createKeyword(req, res, next));

/**
 * @route   POST /api/campaigns/:campaignId/keywords/bulk
 * @desc    Bulk create keywords
 * @access  Private
 */
router.post('/bulk', (req, res, next) => keywordController.bulkCreateKeywords(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/keywords/negative
 * @desc    Get negative keywords
 * @access  Private
 */
router.get('/negative', (req, res, next) => keywordController.getNegativeKeywords(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/keywords
 * @desc    Get all keywords for a campaign
 * @access  Private
 */
router.get('/', (req, res, next) => keywordController.getKeywords(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/keywords/:id
 * @desc    Get a single keyword by ID
 * @access  Private
 */
router.get('/:id', (req, res, next) => keywordController.getKeyword(req, res, next));

/**
 * @route   PUT /api/campaigns/:campaignId/keywords/:id
 * @desc    Update a keyword
 * @access  Private
 */
router.put('/:id', (req, res, next) => keywordController.updateKeyword(req, res, next));

/**
 * @route   DELETE /api/campaigns/:campaignId/keywords/:id
 * @desc    Delete a keyword
 * @access  Private
 */
router.delete('/:id', (req, res, next) => keywordController.deleteKeyword(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/keywords/:id/stats
 * @desc    Get keyword statistics
 * @access  Private
 */
router.get('/:id/stats', (req, res, next) => keywordController.getKeywordStats(req, res, next));

export default router;
