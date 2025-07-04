from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import datetime

from rest_framework.test import APIClient, APITestCase
# For DRF status codes
from rest_framework import status

from .models import Challenge, StudentChallengeProgress, CoachInsightsLog, InsightTypeChoices, ChallengeStatusChoices
from .services import start_challenge_for_user, check_single_challenge_progress, check_all_active_challenge_progress_for_user
from .rules import generate_insights_for_user # and individual rule functions when refactored for testing
from campaigns.models import Campaign, AdGroup, Keyword, MatchTypeChoices, CampaignStatusChoices, KeywordStatusChoices, AdTypeChoices, BiddingStrategyChoices, TargetingTypeChoices
from products.models import Product
from performance.models import AdPerformanceMetric

User = get_user_model()

# Placeholder for detailed test cases as outlined in the planning phase.
# These tests will require significant setup of prerequisite data (Users, Products, Campaigns, PerformanceMetrics).

class BaseTestCase(TestCase):
    """Base class for tests needing a common user and product."""
    def setUp(self):
        super().setUp() # Ensure APITestCase setup is called if inheriting from it later for API tests
        self.user = User.objects.create_user(email='testuser@example.com', password='password123', first_name='Test')
        self.product1 = Product.objects.create(
            asin="B0EXAMPLE1", product_name="Test Product 1", avg_selling_price=Decimal("25.00"),
            cost_of_goods_sold=Decimal("10.00"), initial_cvr_baseline=0.05,
            competitive_intensity='medium', seasonality_profile='evergreen'
        )
        self.product2 = Product.objects.create(
            asin="B0EXAMPLE2", product_name="Test Product 2", avg_selling_price=Decimal("50.00"),
            cost_of_goods_sold=Decimal("20.00"), initial_cvr_baseline=0.03,
            competitive_intensity='high', seasonality_profile='seasonal_toy'
        )
        # APIClient setup for API tests
        if hasattr(self, 'client'): # Check if self.client is expected (e.g. in APITestCase)
            self.client.force_authenticate(user=self.user)


class InsightRulesTests(BaseTestCase):
    def test_placeholder_insight_rule_example(self):
        """
        Conceptual test for an insight rule.
        Actual implementation would involve creating specific data scenarios.
        """
        # Example: Test for rule_budget_capping_scaling_opportunity
        # 1. Create campaign linked to self.product1
        campaign = Campaign.objects.create(
            user=self.user, name="Scaling Opp Campaign", ad_type=AdTypeChoices.SPONSORED_PRODUCTS,
            status=CampaignStatusChoices.ENABLED, daily_budget=Decimal("20.00"),
            bidding_strategy=BiddingStrategyChoices.DYNAMIC_DOWN_ONLY, targeting_type=TargetingTypeChoices.MANUAL
        )
        campaign.advertised_products.add(self.product1)

        # 2. Seed AdPerformanceMetric for current week (meeting capping, ACoS, WoW sales criteria)
        #    - Budget capping: spend close to 7 * daily_budget
        #    - ACoS <= product1.break_even_acos - 10%
        #    - Sales WoW >= 7%
        # This requires careful data seeding for two weeks.

        # 3. Call generate_insights_for_user for the current week's start date
        # current_week_start = timezone.now().date() - datetime.timedelta(days=timezone.now().weekday()) # Assuming Monday start
        # generate_insights_for_user(self.user.id, current_week_start)

        # 4. Assert CoachInsightsLog created with correct type and message
        # insights = CoachInsightsLog.objects.filter(user=self.user, insight_type=InsightTypeChoices.BUDGET_CAPPING_SCALING_OPPORTUNITY)
        # self.assertTrue(insights.exists())
        # self.assertIn(campaign.name, insights.first().generated_message)
        self.assertTrue(True) # Placeholder assertion

    # Add more tests for each of the 7 rules and their edge cases...


class ChallengeServicesTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Seed challenges (or ensure they are seeded by a fixture or management command call)
        self.challenge_launchpad = Challenge.objects.create(
            title="Test Launchpad", description="Desc1", objective_summary="Obj1", level="Beginner",
            success_criteria={"time_limit_weeks": 4, "metrics": [{"name": "TotalAdAttributedSalesCount", "target": 10, "condition": "ge"}]}
        )

    def test_start_challenge_service(self):
        progress = start_challenge_for_user(user_id=self.user.id, challenge_id=self.challenge_launchpad.id)
        self.assertIsNotNone(progress)
        self.assertEqual(progress.challenge, self.challenge_launchpad)
        self.assertEqual(progress.user, self.user)
        self.assertEqual(progress.status, ChallengeStatusChoices.ACTIVE)
        self.assertTrue((timezone.now() - progress.start_time).total_seconds() < 5) # Check start_time is recent

    def test_check_challenge_progress_success_service(self):
        progress = start_challenge_for_user(self.user.id, self.challenge_launchpad.id)
        # Simulate passing of time and performance data for "TotalAdAttributedSalesCount" >= 10
        # For simplicity, assume current_sim_week_start_date is such that challenge is ongoing.
        sim_week_start = progress.start_time.date()

        # Seed AdPerformanceMetric data for the user and relevant campaigns/products for the challenge
        # For this example, we'll assume the metric "TotalAdAttributedSalesCount" is met.
        # This would involve creating Campaign, AdGroup, then AdPerformanceMetric records.
        # For brevity, we'll mock the _get_challenge_metric_value or assume data exists.

        # This test needs more elaborate setup to truly test metric calculation.
        # For now, we focus on the status change if criteria were hypothetically met.
        # In a real test, you'd seed AdPerformanceMetric, then call:
        # check_single_challenge_progress(progress, sim_week_start)
        # And then check progress.status.

        # Mocking success for this placeholder:
        progress.status = ChallengeStatusChoices.COMPLETED_SUCCESS
        progress.save()

        reloaded_progress = StudentChallengeProgress.objects.get(id=progress.id)
        self.assertEqual(reloaded_progress.status, ChallengeStatusChoices.COMPLETED_SUCCESS)


class ChallengeAPITests(APITestCase, BaseTestCase): # Inherit from APITestCase for self.client, BaseTestCase for user/product
    def setUp(self):
        super().setUp() # Calls BaseTestCase.setUp which includes client.force_authenticate
        # Seed challenges for API tests
        self.challenge1 = Challenge.objects.create(title="API Test Challenge 1", level="Beginner", is_active=True, objective_summary="Test obj1", success_criteria={"time_limit_weeks":1})
        self.challenge2 = Challenge.objects.create(title="API Test Challenge 2", level="Intermediate", is_active=True, objective_summary="Test obj2", success_criteria={"time_limit_weeks":2})
        self.inactive_challenge = Challenge.objects.create(title="Inactive Challenge", level="Beginner", is_active=False, objective_summary="Test obj3")


    def test_list_challenges_api(self):
        url = reverse('challenge-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Should only list active challenges
        self.assertTrue(any(c['title'] == self.challenge1.title for c in response.data))

    def test_start_challenge_api_success(self):
        url = reverse('challenge-start', kwargs={'pk': self.challenge1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['challenge_title'], self.challenge1.title)
        self.assertEqual(response.data['status'], ChallengeStatusChoices.ACTIVE)
        self.assertTrue(StudentChallengeProgress.objects.filter(user=self.user, challenge=self.challenge1).exists())

    def test_start_challenge_api_not_found(self):
        url = reverse('challenge-start', kwargs={'pk': 9999}) # Non-existent
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_start_challenge_api_inactive(self):
        url = reverse('challenge-start', kwargs={'pk': self.inactive_challenge.id})
        response = self.client.post(url) # ChallengeViewSet queryset filters by is_active=True, so this should be 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_list_student_challenge_progress_api(self):
        # Start a challenge first
        start_challenge_for_user(user_id=self.user.id, challenge_id=self.challenge1.id)

        url = reverse('student-challenge-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['challenge_title'], self.challenge1.title)

class CoachInsightsAPITests(APITestCase, BaseTestCase):
    def setUp(self):
        super().setUp()
        self.insight_read = CoachInsightsLog.objects.create(
            user=self.user, insight_type=InsightTypeChoices.GENERAL_PERFORMANCE_TIP,
            generated_message="This is a read insight.", is_read=True,
            simulated_week_start_date=timezone.now().date()
        )
        self.insight_unread = CoachInsightsLog.objects.create(
            user=self.user, insight_type=InsightTypeChoices.HIGH_ACOS_GENERAL_INEFFICIENCY,
            generated_message="This is an unread insight.", is_read=False,
            simulated_week_start_date=timezone.now().date()
        )
        self.other_user = User.objects.create_user(email='other@example.com', password='password')
        self.other_user_insight = CoachInsightsLog.objects.create(
            user=self.other_user, insight_type=InsightTypeChoices.GENERAL_PERFORMANCE_TIP,
            generated_message="Other user's insight.", is_read=False,
            simulated_week_start_date=timezone.now().date()
        )

    def test_list_coach_insights_api_all(self):
        url = reverse('coach-insight-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) # Should only see self.user's insights

    def test_list_coach_insights_api_unread(self):
        url = reverse('coach-insight-list') + "?is_read=false"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.insight_unread.id)

    def test_list_coach_insights_api_read(self):
        url = reverse('coach-insight-list') + "?is_read=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.insight_read.id)

    def test_mark_insight_read_api(self):
        self.assertFalse(self.insight_unread.is_read)
        url = reverse('coach-insight-mark-read', kwargs={'pk': self.insight_unread.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.insight_unread.refresh_from_db()
        self.assertTrue(self.insight_unread.is_read)

    def test_mark_insight_read_api_forbidden(self):
        url = reverse('coach-insight-mark-read', kwargs={'pk': self.other_user_insight.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Because get_queryset filters first
        # If get_queryset didn't filter, it would be 403 from the explicit check in the action.
        # With default ReadOnlyModelViewSet.get_object(), it will be 404 if not in initial queryset.
        self.other_user_insight.refresh_from_db()
        self.assertFalse(self.other_user_insight.is_read)
