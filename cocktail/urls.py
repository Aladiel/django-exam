from django.urls import path
from .views import generate_cocktail_view, cocktail_list_view, redirect_home

urlpatterns = [
    path('', redirect_home, name='home'),
    path('generate/', generate_cocktail_view, name='generate_cocktail'),
    path('cocktails/', cocktail_list_view, name='cocktail_list'),
]