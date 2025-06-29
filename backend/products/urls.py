from django.urls import path
from .views import ProductListView #, ProductDetailView, ProductCreateView # If more views were added

app_name = 'products'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    # If detail/create/update/delete views were added:
    # path('create/', ProductCreateView.as_view(), name='product-create'),
    # path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    # path('<str:asin>/', ProductDetailView.as_view(), name='product-detail-asin'), # Example with ASIN
]
