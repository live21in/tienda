from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    #Enviamos como parametro category_slug
    path('category/<slug:category_slug>/', views.store, name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search')
] 