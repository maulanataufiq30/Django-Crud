from django.urls import path
from .views import ProdukListView, ProdukCreateView, ProdukUpdateView, ProdukDeleteView

urlpatterns = [
    path('', ProdukListView.as_view(), name='produk_list'),
    path('tambah/', ProdukCreateView.as_view(), name='produk_create'),
    path('<int:pk>/edit/', ProdukUpdateView.as_view(), name='produk_update'),
    path('<int:pk>/hapus/', ProdukDeleteView.as_view(), name='produk_delete'),
]