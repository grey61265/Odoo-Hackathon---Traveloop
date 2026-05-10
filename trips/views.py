from django.shortcuts import render


def dashboard(request):
    return render(request, 'trips/dashboard.html')


def trip_list(request):
    return render(request, 'trips/trip_list.html')


def budget(request):
    return render(request, 'trips/budget.html')


def profile(request):
    return render(request, 'trips/profile.html')