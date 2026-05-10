from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('trips/',     views.trip_list, name='trip_list'),
    path('budget/',    views.budget,    name='budget'),
    path('profile/',   views.profile,   name='profile'),
]
