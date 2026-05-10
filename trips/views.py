from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages

import requests

from django.conf import settings

from .models import (
    Trip,
    Stop,
    Activity,
    Expense,
    PackingItem,
    Note,
)

from .forms import (
    TripForm,
    StopForm,
    ActivityForm,
    ExpenseForm,
    PackingItemForm,
    NoteForm,
)


# =========================================================
# HELPER — resolve the Django User from the session
# =========================================================

def _get_current_user(request):
    """Return the Django User for the logged-in session, or None."""
    email = (request.session.get('user') or {}).get('email')
    if not email:
        return None
    user, _ = User.objects.get_or_create(
        username=email,
        defaults={'email': email}
    )
    return user


# =========================================================
# HOME  –  redirect authenticated users to dashboard
# =========================================================

def home(request):
    if 'user' in request.session:
        return redirect('dashboard')
    return render(request, 'trips/home.html')


# =========================================================
# DASHBOARD
# =========================================================

def dashboard(request):
    if 'user' not in request.session:
        return redirect('home')

    current_user = _get_current_user(request)
    today        = timezone.now().date()
    trips        = Trip.objects.filter(user=current_user)

    upcoming_trips = trips.filter(start_date__gte=today).count()
    total_spent    = sum(e.amount for e in Expense.objects.filter(trip__user=current_user))
    recent_trips   = trips[:5]
    all_cities     = Stop.objects.filter(trip__user=current_user).values_list('city', flat=True).distinct().count()

    context = {
        'trips':             trips,
        'total_trips':       trips.count(),
        'upcoming_trips':    upcoming_trips,
        'total_budget':      total_spent,
        'countries_visited': all_cities,
        'recent_trips':      recent_trips,
        'user_data':         request.session.get('user'),
    }

    return render(request, 'trips/dashboard.html', context)


# =========================================================
# TRIP LIST
# =========================================================

def trip_list(request):
    if 'user' not in request.session:
        return redirect('home')

    current_user = _get_current_user(request)
    trips = Trip.objects.filter(user=current_user)
    return render(request, 'trips/trip_list.html', {'trips': trips})


# =========================================================
# CREATE TRIP
# =========================================================

def create_trip(request):
    if 'user' not in request.session:
        return redirect('home')

    if request.method == 'POST':
        form = TripForm(request.POST)

        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = _get_current_user(request)
            trip.save()
            messages.success(request, f'Trip "{trip.title}" created!')
            return redirect('trip_list')
    else:
        form = TripForm()

    return render(request, 'trips/create_trip.html', {'form': form})


# =========================================================
# TRIP DETAIL
# =========================================================

def trip_detail(request, pk):
    if 'user' not in request.session:
        return redirect('home')

    current_user = _get_current_user(request)
    trip = get_object_or_404(Trip, pk=pk, user=current_user)

    if request.method == 'POST':
        action = request.POST.get('action') or request.POST.get('add_stop') or ''

        # Normalise legacy button-name style
        if 'add_stop' in request.POST:
            action = 'add_stop'
        elif 'add_activity' in request.POST:
            action = 'add_activity'
        elif 'add_expense' in request.POST:
            action = 'add_expense'
        elif 'add_packing_item' in request.POST:
            action = 'add_packing_item'
        elif 'add_note' in request.POST:
            action = 'add_note'

        if action == 'add_stop':
            stop_form = StopForm(request.POST)
            if stop_form.is_valid():
                arrival    = stop_form.cleaned_data['arrival_date']
                departure  = stop_form.cleaned_data['departure_date']
                # Cross-validate: stop must fall within the trip's date window
                errors = []
                if arrival < trip.start_date:
                    errors.append(f"Arrival date ({arrival}) is before the trip start ({trip.start_date}).")
                if departure > trip.end_date:
                    errors.append(f"Departure date ({departure}) is after the trip end ({trip.end_date}).")
                if errors:
                    for e in errors:
                        messages.error(request, e)
                else:
                    stop = stop_form.save(commit=False)
                    stop.trip = trip
                    stop.save()
                    messages.success(request, f'Stop "{stop.city}" added.')
            else:
                for field_errors in stop_form.errors.values():
                    for e in field_errors:
                        messages.error(request, e)

        elif action == 'add_activity':
            activity_form = ActivityForm(request.POST)
            if activity_form.is_valid():
                activity = activity_form.save(commit=False)
                stop_id  = request.POST.get('stop_id')
                if stop_id:
                    try:
                        activity.stop = Stop.objects.get(id=stop_id, trip=trip)
                        activity.save()
                        messages.success(request, f'Activity "{activity.name}" added.')
                    except Stop.DoesNotExist:
                        messages.error(request, "Invalid stop selected.")
                else:
                    messages.error(request, "No stop specified for activity.")

        elif action == 'add_expense':
            expense_form = ExpenseForm(request.POST)
            if expense_form.is_valid():
                expense      = expense_form.save(commit=False)
                expense.trip = trip
                expense.save()
                messages.success(request, 'Expense added.')
            else:
                for field_errors in expense_form.errors.values():
                    for e in field_errors:
                        messages.error(request, e)

        elif action == 'add_packing_item':
            packing_form = PackingItemForm(request.POST)
            if packing_form.is_valid():
                packing      = packing_form.save(commit=False)
                packing.trip = trip
                packing.save()
                messages.success(request, f'"{packing.item_name}" added to packing list.')
            else:
                for field_errors in packing_form.errors.values():
                    for e in field_errors:
                        messages.error(request, e)

        elif action == 'toggle_packed':
            item_id = request.POST.get('item_id')
            try:
                item        = PackingItem.objects.get(id=item_id, trip=trip)
                item.packed = not item.packed
                item.save()
            except PackingItem.DoesNotExist:
                messages.error(request, "Item not found.")

        elif action == 'add_note':
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                note      = note_form.save(commit=False)
                note.trip = trip
                note.save()
                messages.success(request, 'Note saved.')
            else:
                for field_errors in note_form.errors.values():
                    for e in field_errors:
                        messages.error(request, e)

        return redirect('trip_detail', pk=pk)

    # ── GET ──
    stops         = Stop.objects.filter(trip=trip)
    expenses      = Expense.objects.filter(trip=trip)
    packing_items = PackingItem.objects.filter(trip=trip)
    notes         = Note.objects.filter(trip=trip)

    total_expenses      = sum(exp.amount for exp in expenses)
    total_activity_cost = sum(
        activity.cost
        for stop in stops
        for activity in Activity.objects.filter(stop=stop)
    )
    grand_total  = total_expenses + total_activity_cost
    packed_count = packing_items.filter(packed=True).count()
    total_items  = packing_items.count()

    context = {
        'trip':                trip,
        'stops':               stops,
        'expenses':            expenses,
        'packing_items':       packing_items,
        'notes':               notes,
        'total_expenses':      total_expenses,
        'total_activity_cost': total_activity_cost,
        'grand_total':         grand_total,
        'packed_count':        packed_count,
        'total_items':         total_items,

        'stop_form':     StopForm(),
        'activity_form': ActivityForm(),
        'exp_form':      ExpenseForm(),
        'pack_form':     PackingItemForm(),
        'note_form':     NoteForm(),
    }

    return render(request, 'trips/trip_detail.html', context)


# =========================================================
# DELETE TRIP
# =========================================================

def delete_trip(request, pk):
    if 'user' not in request.session:
        return redirect('home')

    current_user = _get_current_user(request)
    trip = get_object_or_404(Trip, pk=pk, user=current_user)

    if request.method == 'POST':
        trip_title = trip.title
        trip.delete()
        messages.success(request, f'Trip "{trip_title}" deleted.')

    return redirect('trip_list')


# =========================================================
# BUDGET
# =========================================================

def budget(request):
    if 'user' not in request.session:
        return redirect('home')

    current_user = _get_current_user(request)
    expenses     = Expense.objects.filter(trip__user=current_user)
    total_budget = sum(expense.amount for expense in expenses)

    # Category breakdown for chart
    from collections import defaultdict
    breakdown = defaultdict(float)
    for exp in expenses:
        breakdown[exp.get_category_display()] += float(exp.amount)

    context = {
        'expenses':     expenses,
        'total_budget': total_budget,
        'breakdown':    dict(breakdown),
    }

    return render(request, 'trips/budget.html', context)


# =========================================================
# PROFILE
# =========================================================

def profile(request):
    if 'user' not in request.session:
        return redirect('home')

    return render(
        request,
        'trips/profile.html',
        {'user_data': request.session.get('user')}
    )


# =========================================================
# SHARED / PUBLIC ITINERARY VIEW
# =========================================================

def shared_trip(request, pk):
    """Public read-only view of a trip — no login required."""
    trip   = get_object_or_404(Trip, pk=pk)
    stops  = Stop.objects.filter(trip=trip)
    notes  = Note.objects.filter(trip=trip)

    total_activity_cost = sum(
        activity.cost
        for stop in stops
        for activity in Activity.objects.filter(stop=stop)
    )

    context = {
        'trip':                trip,
        'stops':               stops,
        'notes':               notes,
        'total_activity_cost': total_activity_cost,
    }

    return render(request, 'trips/shared_trip.html', context)


# =========================================================
# GOOGLE LOGIN
# =========================================================

def google_login(request):
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', '')

    # ── Dev bypass: if credentials are placeholder, use email/password mock ──
    if not client_id or client_id.strip() in ('', '.apps.googleusercontent.com'):
        return render(request, 'trips/dev_login.html')

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth"
        "?response_type=code"
        f"&client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=select_account"
    )

    return redirect(google_auth_url)


# =========================================================
# DEV LOGIN (used when Google credentials are not configured)
# =========================================================

def dev_login(request):
    """Simple name/email form that bypasses OAuth for local development."""
    if request.method == 'POST':
        name  = request.POST.get('name', 'Dev User').strip()
        email = request.POST.get('email', 'dev@traveloop.local').strip()

        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'trips/dev_login.html')

        request.session['user'] = {
            'name':    name or email.split('@')[0],
            'email':   email,
            'picture': None,
        }
        return redirect('dashboard')

    return render(request, 'trips/dev_login.html')


# =========================================================
# GOOGLE CALLBACK
# =========================================================

def google_callback(request):
    code = request.GET.get('code')

    if not code:
        messages.error(request, "No authorisation code returned from Google.")
        return redirect('home')

    token_url = "https://oauth2.googleapis.com/token"

    data = {
        'code':          code,
        'client_id':     settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri':  settings.GOOGLE_REDIRECT_URI,
        'grant_type':    'authorization_code',
    }

    try:
        response   = requests.post(token_url, data=data, timeout=10)
        token_json = response.json()
    except Exception as exc:
        messages.error(request, f"Failed to contact Google: {exc}")
        return redirect('home')

    if 'id_token' not in token_json:
        error_desc = token_json.get('error_description', token_json.get('error', 'Unknown error'))
        messages.error(request, f"Google auth failed: {error_desc}")
        return redirect('home')

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        idinfo = id_token.verify_oauth2_token(
            token_json['id_token'],
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception as exc:
        messages.error(request, f"Token verification failed: {exc}")
        return redirect('home')

    request.session['user'] = {
        'name':    idinfo.get('name'),
        'email':   idinfo.get('email'),
        'picture': idinfo.get('picture'),
    }

    return redirect('dashboard')


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):
    request.session.flush()
    logout(request)
    return redirect('home')