from django.core.management.base import BaseCommand
from insights_challenges.models import Challenge
# from decimal import Decimal # Not strictly needed if targets are floats/ints in JSON

class Command(BaseCommand):
    help = 'Seeds the database with initial challenge data based on Ryan\'s Strategic Input.'

    CHALLENGE_DATA = [
        {
            "title": "The Launchpad: Achieving Initial Profitability",
            "description": "Launch Sponsored Product campaigns (Auto and 1-2 Manual) for a new product.",
            "scenario_details": "You're a new PPC manager assigned to launch a brand new product (e.g., Eco-Friendly Bamboo Toothbrush - ASIN B0EXAMPLE1 - assuming this ASIN exists or is created by product seeder). You have a starting daily budget of $25.",
            "objective_summary": "Achieve 50+ ad-attributed sales with an ACoS below 35% within 4 simulated weeks.",
            "level": "Beginner",
            "product_context_asins": ["B0EXAMPLE1"], # Example ASIN
            "scenario_constraints_json": {
                "starting_daily_budget_per_campaign": 25.00,
                # "product_to_launch_asin": "B0EXAMPLE1" # Redundant if in product_context_asins
            },
            "success_criteria": {
                "metrics": [
                    {"name": "TotalAdAttributedSalesCount", "target": 50, "condition": "ge"},
                    {"name": "FinalOverallACoS", "target": 35.0, "condition": "le"}
                ],
                "time_limit_weeks": 4,
                "optional_goals": [
                    {"description": "No negative ACoS keywords with >$10 spend"}
                ]
            },
            "is_active": True
        },
        {
            "title": "The ACoS Turnaround: Mastering Optimization",
            "description": "Optimize an inherited, struggling campaign to reduce ACoS and improve sales.",
            "scenario_details": "You've inherited a running Premium Wireless Earbuds campaign (ASIN B0EXAMPLE2 - high competition) that's currently struggling with a high ACoS (e.g., 60-70%) and significant spend. Assume this campaign and product data will be set up by a separate mechanism or this challenge requires specific pre-existing state.",
            "objective_summary": "Reduce the campaign's overall ACoS to below 30% while maintaining or increasing weekly sales volume by at least 10% within 3 simulated weeks.",
            "level": "Intermediate",
            "product_context_asins": ["B0EXAMPLE2"], # Example ASIN
            "scenario_constraints_json": {
                # "target_campaign_id_to_optimize": "NEEDS_DYNAMIC_SETUP_OR_STUDENT_FINDS_IT"
                # This implies the challenge might need to identify or allow student to select the campaign.
                # For V1 seeder, we define the challenge, setup is manual or future.
            },
            "success_criteria": {
                "metrics": [
                    {"name": "CampaignACoS", "target": 30.0, "condition": "le"},
                    {"name": "WeeklySalesVolumeIncreasePercent", "target": 10.0, "condition": "ge"}
                ],
                "time_limit_weeks": 3,
                "optional_goals": [
                    {"description": "At least 5 new negative keywords added"}
                ]
            },
            "is_active": True
        },
        {
            "title": "Scale to Dominate: Maximizing Profitable Growth",
            "description": "Aggressively grow a profitable campaign while maintaining efficiency.",
            "scenario_details": "You have a highly profitable Ergonomic Office Chair campaign (ASIN B0EXAMPLE3 - medium competition) already running at a healthy ACoS (e.g., 15-20%) and steady sales. The goal is aggressive, profitable growth.",
            "objective_summary": "Increase weekly ad-attributed sales by 50% while maintaining an ACoS below 25% within 6 simulated weeks.",
            "level": "Advanced",
            "product_context_asins": ["B0EXAMPLE3"], # Example ASIN
            "scenario_constraints_json": {},
            "success_criteria": {
                "metrics": [
                    {"name": "WeeklySalesVolumeIncreasePercent", "target": 50.0, "condition": "ge"},
                    {"name": "FinalOverallACoS", "target": 25.0, "condition": "le"}
                ],
                "time_limit_weeks": 6,
                "optional_goals": [
                    {"description": "Creation of at least 2 new exact match ad groups/campaigns from broad/phrase success"}
                ]
            },
            "is_active": True
        }
    ]

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding initial challenge data based on Ryan's Strategic Input..."))

        created_count = 0
        updated_count = 0

        for data in self.CHALLENGE_DATA:
            # Align field names with the Challenge model
            challenge_defaults = {
                'description': data['description'],
                'scenario_details': data['scenario_details'],
                'objective_summary': data['objective_summary'],
                'level': data['level'],
                'product_context_asins': data.get('product_context_asins', []),
                'scenario_constraints_json': data.get('scenario_constraints_json', {}),
                'success_criteria': data['success_criteria'],
                'is_active': data.get('is_active', True)
            }
            challenge, created = Challenge.objects.update_or_create(
                title=data['title'], # Use title as the unique key for update_or_create
                defaults=challenge_defaults
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created challenge: {challenge.title}"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Challenge '{challenge.title}' already exists. Updated."))
                updated_count +=1

        self.stdout.write(self.style.SUCCESS(f"Challenge seeding complete. {created_count} created, {updated_count} updated."))
