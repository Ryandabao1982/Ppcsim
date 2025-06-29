from django.core.management.base import BaseCommand, CommandError
from products.models import Product # Assuming models.py is in the same app 'products'
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with initial product data for the Ads Simulator'

    # Define the product data directly in the command
    # In a real application, this might come from a CSV, JSON, or another source
    PRODUCT_DATA = [
        {
            "product_name": "Ergonomic Office Chair", "asin": "B0BQZ0Y4R5", "category": "Office Furniture",
            "avg_selling_price": Decimal("249.99"), "cost_of_goods_sold": Decimal("95.00"),
            "initial_cvr_baseline": 0.015, "initial_bestseller_rank": 12000,
            "review_count": 85, "avg_star_rating": 4.3,
            "seasonality_profile": "evergreen", "competitive_intensity": "medium"
        },
        {
            "product_name": "Portable Bluetooth Speaker", "asin": "B0CR00N0M0", "category": "Electronics",
            "avg_selling_price": Decimal("49.99"), "cost_of_goods_sold": Decimal("15.00"),
            "initial_cvr_baseline": 0.025, "initial_bestseller_rank": 850,
            "review_count": 2100, "avg_star_rating": 4.7,
            "seasonality_profile": "evergreen", "competitive_intensity": "high"
        },
        {
            "product_name": "Organic Green Tea Bags (100-ct)", "asin": "B0CR1A1B1C", "category": "Grocery & Gourmet Food",
            "avg_selling_price": Decimal("19.99"), "cost_of_goods_sold": Decimal("5.00"),
            "initial_cvr_baseline": 0.030, "initial_bestseller_rank": 5000,
            "review_count": 750, "avg_star_rating": 4.5,
            "seasonality_profile": "evergreen", "competitive_intensity": "medium"
        },
        {
            "product_name": "Kids' STEM Robot Kit", "asin": "B0BR2C2D2E", "category": "Toys & Games",
            "avg_selling_price": Decimal("79.99"), "cost_of_goods_sold": Decimal("30.00"),
            "initial_cvr_baseline": 0.018, "initial_bestseller_rank": 25000,
            "review_count": 15, "avg_star_rating": 3.9,
            "seasonality_profile": "seasonal_toy", "competitive_intensity": "medium"
        },
        {
            "product_name": "Winter Wool Scarf", "asin": "B0CR3E3F3G", "category": "Clothing, Shoes & Jewelry",
            "avg_selling_price": Decimal("29.99"), "cost_of_goods_sold": Decimal("8.00"),
            "initial_cvr_baseline": 0.010, "initial_bestseller_rank": 80000,
            "review_count": 120, "avg_star_rating": 4.1,
            "seasonality_profile": "seasonal_clothing", "competitive_intensity": "high"
        },
        {
            "product_name": "Stainless Steel Water Bottle (32oz)", "asin": "B0CR4H4I4J", "category": "Sports & Outdoors",
            "avg_selling_price": Decimal("22.50"), "cost_of_goods_sold": Decimal("7.50"),
            "initial_cvr_baseline": 0.022, "initial_bestseller_rank": 1500,
            "review_count": 1800, "avg_star_rating": 4.6,
            "seasonality_profile": "evergreen", "competitive_intensity": "high"
        },
        {
            "product_name": "Pet Grooming Glove", "asin": "B0CR5K5L5M", "category": "Pet Supplies",
            "avg_selling_price": Decimal("14.99"), "cost_of_goods_sold": Decimal("4.00"),
            "initial_cvr_baseline": 0.035, "initial_bestseller_rank": 10000,
            "review_count": 400, "avg_star_rating": 4.4,
            "seasonality_profile": "evergreen", "competitive_intensity": "low"
        },
        {
            "product_name": "Advanced Drone with HD Camera", "asin": "B0CR6N6O6P", "category": "Electronics",
            "avg_selling_price": Decimal("499.00"), "cost_of_goods_sold": Decimal("200.00"),
            "initial_cvr_baseline": 0.008, "initial_bestseller_rank": 35000,
            "review_count": 60, "avg_star_rating": 4.0,
            "seasonality_profile": "evergreen", "competitive_intensity": "medium" # Note: design doc said "evergreen (with holiday spikes)" - using 'evergreen'
        },
        {
            "product_name": "Eco-Friendly Reusable Shopping Bags (5-pack)", "asin": "B0CR7Q7R7S", "category": "Home & Kitchen",
            "avg_selling_price": Decimal("16.99"), "cost_of_goods_sold": Decimal("5.00"),
            "initial_cvr_baseline": 0.028, "initial_bestseller_rank": 7000,
            "review_count": 600, "avg_star_rating": 4.5,
            "seasonality_profile": "evergreen", "competitive_intensity": "medium"
        },
        {
            "product_name": "Gourmet Coffee Beans (Dark Roast)", "asin": "B0CR8T8U8V", "category": "Grocery & Gourmet Food",
            "avg_selling_price": Decimal("24.00"), "cost_of_goods_sold": Decimal("8.00"),
            "initial_cvr_baseline": 0.020, "initial_bestseller_rank": 900,
            "review_count": 1500, "avg_star_rating": 4.6,
            "seasonality_profile": "evergreen", "competitive_intensity": "high"
        }
    ]

    def handle(self, *args, **options):
        self.stdout.write("Seeding initial product data...")

        # Option to clear existing products:
        # if options.get('clear'):
        #     Product.objects.all().delete()
        #     self.stdout.write(self.style.SUCCESS('Successfully cleared existing products.'))

        created_count = 0
        skipped_count = 0

        for data in self.PRODUCT_DATA:
            product, created = Product.objects.update_or_create(
                asin=data['asin'], # Use ASIN as the unique key for update_or_create
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created product: {product.product_name} (ASIN: {product.asin})"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Product with ASIN {product.asin} already exists. Updated: {product.product_name}"))
                skipped_count +=1 # Or updated_count if you want to track updates

        self.stdout.write(self.style.SUCCESS(f"Product seeding complete. {created_count} created, {skipped_count} already existed (updated)."))

    # Example of how to add arguments to the command:
    # def add_arguments(self, parser):
    #     parser.add_argument(
    #         '--clear',
    #         action='store_true',
    #         help='Clear existing products before seeding',
    #     )
