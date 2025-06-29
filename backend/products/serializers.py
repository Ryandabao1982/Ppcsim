from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'asin',
            'product_name',
            'category',
            'avg_selling_price',
            'cost_of_goods_sold',
            'initial_cvr_baseline',
            'initial_bestseller_rank',
            'review_count',
            'avg_star_rating',
            'seasonality_profile',
            'competitive_intensity',
            'created_at',
            'updated_at'
        ]
        # read_only_fields = ['id', 'created_at', 'updated_at'] # Good practice for GET responses
        # For a listing/GET endpoint, all fields are effectively read-only from client perspective
        # If this serializer were used for CUD operations, writeable fields would be different.
        # For now, this is for GET /api/products/

    # You can add custom representations if needed, e.g., for CVR:
    # initial_cvr_percentage = serializers.SerializerMethodField()
    # def get_initial_cvr_percentage(self, obj):
    #     return f"{(obj.initial_cvr_baseline * 100):.2f}%"
    # And then add 'initial_cvr_percentage' to fields list.
    # For now, keeping it direct to model fields.
