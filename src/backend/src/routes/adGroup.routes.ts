import { Router } from 'express';
import { adGroupController } from '../controllers/adGroup.controller';

const router = Router({ mergeParams: true }); // mergeParams allows access to campaignId from parent route

/**
 * @route   POST /api/campaigns/:campaignId/adgroups
 * @desc    Create a new ad group
 * @access  Private
 */
router.post('/', (req, res, next) => adGroupController.createAdGroup(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/adgroups
 * @desc    Get all ad groups for a campaign
 * @access  Private
 */
router.get('/', (req, res, next) => adGroupController.getAdGroups(req, res, next));

/**
 * @route   GET /api/campaigns/:campaignId/adgroups/:id
 * @desc    Get a single ad group by ID
 * @access  Private
 */
router.get('/:id', (req, res, next) => adGroupController.getAdGroup(req, res, next));

/**
 * @route   PUT /api/campaigns/:campaignId/adgroups/:id
 * @desc    Update an ad group
 * @access  Private
 */
router.put('/:id', (req, res, next) => adGroupController.updateAdGroup(req, res, next));

/**
 * @route   DELETE /api/campaigns/:campaignId/adgroups/:id
 * @desc    Delete an ad group
 * @access  Private
 */
router.delete('/:id', (req, res, next) => adGroupController.deleteAdGroup(req, res, next));

export default router;
