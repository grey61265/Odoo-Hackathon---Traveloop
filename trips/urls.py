from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('',                    views.home,           name='home'),
    path('login/',              views.login_view,     name='login'),
    path('register/',           views.register_view,  name='register'),
    path('logout/',             views.logout_view,    name='logout'),

    # ── Core pages ────────────────────────────────────────
    path('dashboard/',          views.dashboard,      name='dashboard'),
    path('profile/',            views.profile,        name='profile'),
    path('budget/',             views.budget,         name='budget'),

    # ── Trips ─────────────────────────────────────────────
    path('trips/',              views.trip_list,      name='trip_list'),
    path('trips/create/',       views.create_trip,    name='create_trip'),
    path('trips/<int:pk>/',     views.trip_detail,    name='trip_detail'),
    path('trips/<int:pk>/delete/', views.delete_trip, name='delete_trip'),

    # ── Public / shared ───────────────────────────────────
    path('share/<int:pk>/',     views.shared_trip,    name='shared_trip'),
]
