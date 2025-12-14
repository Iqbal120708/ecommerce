from django.urls import path

from .views import CategoryList, ProductDetail, ProductList

urlpatterns = [
    path("category/", CategoryList.as_view(), name="category"),
    path("product/", ProductList.as_view(), name="product"),
    path("product/<int:pk>/", ProductDetail.as_view(), name="product_detail"),
]
