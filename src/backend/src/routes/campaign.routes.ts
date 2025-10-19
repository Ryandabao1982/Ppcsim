import { Router } from 'express';
import { campaignController } from '../controllers/campaign.controller';

const router = Router();

/**
 * @route   POST /api/campaigns
 * @desc    Create a new campaign
 * @access  Private
 */
router.post('/', (req, res, next) => campaignController.createCampaign(req, res, next));

/**
 * @route   GET /api/campaigns
 * @desc    Get all campaigns for the authenticated user
 * @access  Private
 */
router.get('/', (req, res, next) => campaignController.getCampaigns(req, res, next));

/**
 * @route   GET /api/campaigns/:id
 * @desc    Get a single campaign by ID
 * @access  Private
 */
router.get('/:id', (req, res, next) => campaignController.getCampaign(req, res, next));

/**
 * @route   PUT /api/campaigns/:id
 * @desc    Update a campaign
 * @access  Private
 */
router.put('/:id', (req, res, next) => campaignController.updateCampaign(req, res, next));

/**
 * @route   DELETE /api/campaigns/:id
 * @desc    Delete a campaign (archive)
 * @access  Private
 */
router.delete('/:id', (req, res, next) => campaignController.deleteCampaign(req, res, next));

/**
 * @route   GET /api/campaigns/:id/stats
 * @desc    Get campaign statistics
 * @access  Private
 */
router.get('/:id/stats', (req, res, next) => campaignController.getCampaignStats(req, res, next));

export default router;
