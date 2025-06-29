from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer
# from rest_framework.pagination import PageNumberPagination # For custom pagination
# from django_filters.rest_framework import DjangoFilterBackend # For filtering
# from rest_framework import filters # For search and ordering

# Example Custom Pagination (if desired)
# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50

class ProductListView(generics.ListAPIView):
    """
    API view to retrieve a list of all products.
    Accessible by any authenticated user.
    """
    queryset = Product.objects.all().order_by('id') # Order by ID or name
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can see product list

    # Uncomment to enable DRF's built-in pagination and filtering
    # pagination_class = StandardResultsSetPagination
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['category', 'seasonality_profile', 'competitive_intensity'] # Fields for exact match filtering
    # search_fields = ['product_name', 'asin', 'category'] # Fields for ?search=...
    # ordering_fields = ['avg_selling_price', 'product_name', 'id'] # Fields for ?ordering=...


# If full CRUD API for products is needed later:
# class ProductCreateView(generics.CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer # Or a dedicated ProductCreateSerializer
#     permission_classes = [permissions.IsAdminUser] # Example: only admins can create

# class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer # Or different serializers for retrieve vs update
#     permission_classes = [permissions.IsAdminUser] # Example: only admins can modify/delete
#     # lookup_field = 'asin' # If you want to use ASIN in URL instead of ID
