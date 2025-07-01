from django.core.management.base import BaseCommand
from insights_challenges.models import Challenge # Assuming models.py is in the same app
from decimal import Decimal # For target_value in success_criteria if it's a Decimal

class Command(BaseCommand):
    help = 'Seeds the database with initial challenge data for the Ads Simulator'

    CHALLENGE_DATA = [
        {
            "name": "The Launchpad - Get Your First Profitable Sales",
            "description": "You're given a brand new product (Kids' STEM Robot Kit - ASIN B0BR2C2D2E), with very few reviews. Your task is to launch Sponsored Product campaigns and achieve your first sales profitably.",
            "objective_text": "Achieve 50+ ad-attributed sales with an ACoS below 50% for Product 'Kids' STEM Robot Kit' (ASIN B0BR2C2D2E) within 4 simulated weeks.",
            "difficulty_level": "Beginner",
            "simulated_weeks_duration": 4,
            "starting_conditions_json": {
                "focus_product_asin": "B0BR2C2D2E", # Kids' STEM Robot Kit
                "initial_budget_total_for_challenge_product_campaigns": 300.00
                # Note: Actual budget application to campaigns is part of a more advanced reset logic.
                # For now, this is informational for the student.
            },
            "success_criteria_json": [
                {"metric": "Orders", "scope": "product_asin", "scope_value": "B0BR2C2D2E", "condition": "greater_than_or_equal_to", "target_value": 50},
                {"metric": "ACoS", "scope": "product_asin", "scope_value": "B0BR2C2D2E", "condition": "less_than_or_equal_to", "target_value": 50.0}
                # The scope 'product_asin' implies metrics should be aggregated for campaigns advertising this ASIN.
            ],
            "is_active": True
        },
        {
            "name": "The ACoS Turnaround - Fixing a Leaky Bucket",
            "description": "You've inherited a Portable Bluetooth Speaker campaign (ASIN B0CR00N0M0) that's been running with high spend and very high ACoS. Your goal is to make it profitable.",
            "objective_text": "Reduce the overall ACoS for campaigns advertising 'Portable Bluetooth Speaker' (ASIN B0CR00N0M0) to below 30%, while maintaining or increasing weekly sales volume by 5% (compared to pre-challenge baseline), within 3 simulated weeks.",
            "difficulty_level": "Intermediate",
            "simulated_weeks_duration": 3,
            "starting_conditions_json": {
                "focus_product_asin": "B0CR00N0M0", # Portable Bluetooth Speaker
                "pre_challenge_setup": "Assume a campaign for this product exists with poor ACoS (e.g., 80-100%). Student needs to find and optimize it."
                # Note: Pre-challenge setup would need a mechanism to ensure such a campaign exists.
            },
            "success_criteria_json": [
                {"metric": "ACoS", "scope": "product_asin", "scope_value": "B0CR00N0M0", "condition": "less_than_or_equal_to", "target_value": 30.0},
                {"metric": "SalesGrowthWoW", "scope": "product_asin", "scope_value": "B0CR00N0M0", "condition": "greater_than_or_equal_to", "target_value": 5.0}
                # SalesGrowthWoW would need special handling in check_challenge_progress
            ],
            "is_active": True
        },
        {
            "name": "Scale to Dominate - Maximize Market Share Profitably",
            "description": "Your Stainless Steel Water Bottle campaign (ASIN B0CR4H4I4J) is already profitable. The client wants to aggressively grow market share without sacrificing profit.",
            "objective_text": "Increase weekly ad-attributed sales for 'Stainless Steel Water Bottle' (ASIN B0CR4H4I4J) by 50% (compared to pre-challenge baseline), while maintaining an ACoS below 25%, within 6 simulated weeks.",
            "difficulty_level": "Advanced",
            "simulated_weeks_duration": 6,
            "starting_conditions_json": {
                "focus_product_asin": "B0CR4H4I4J", # Stainless Steel Water Bottle
                "pre_challenge_setup": "Assume a campaign for this product exists with good ACoS (e.g., 20%)."
            },
            "success_criteria_json": [
                {"metric": "SalesIncreasePercentage", "scope": "product_asin", "scope_value": "B0CR4H4I4J", "condition": "greater_than_or_equal_to", "target_value": 50.0},
                {"metric": "ACoS", "scope": "product_asin", "scope_value": "B0CR4H4I4J", "condition": "less_than_or_equal_to", "target_value": 25.0}
            ],
            "is_active": True
        }
    ]

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial challenge data...")

        created_count = 0
        updated_count = 0

        for data in self.CHALLENGE_DATA:
            challenge, created = Challenge.objects.update_or_create(
                name=data['name'], # Use name as the unique key for update_or_create
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created challenge: {challenge.name}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Challenge '{challenge.name}' already exists. Updated."))
                updated_count +=1

        self.stdout.write(self.style.SUCCESS(f"Challenge seeding complete. {created_count} created, {updated_count} updated."))
