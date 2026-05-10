from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('',                    views.home,           name='home'),
    path('auth/google/',        views.google_login,   name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('auth/dev-login/',     views.dev_login,      name='dev_login'),
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
