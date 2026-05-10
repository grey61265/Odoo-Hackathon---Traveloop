from django.contrib import admin
from .models import Trip, Stop, Activity, Expense, PackingItem, Note


class StopInline(admin.TabularInline):
    model  = Stop
    extra  = 1
    fields = ['city', 'arrival_date', 'departure_date', 'order']


class ActivityInline(admin.TabularInline):
    model  = Activity
    extra  = 1
    fields = ['name', 'category', 'cost']


class ExpenseInline(admin.TabularInline):
    model  = Expense
    extra  = 1
    fields = ['category', 'amount']


class PackingItemInline(admin.TabularInline):
    model  = PackingItem
    extra  = 1
    fields = ['item_name', 'packed']


class NoteInline(admin.StackedInline):
    model  = Note
    extra  = 0
    fields = ['title', 'content']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display  = ['title', 'user', 'start_date', 'end_date', 'created_at']
    list_filter   = ['user', 'start_date']
    search_fields = ['title', 'description', 'user__username']
    inlines       = [StopInline, ExpenseInline, PackingItemInline, NoteInline]


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display  = ['city', 'trip', 'arrival_date', 'departure_date', 'order']
    list_filter   = ['trip']
    search_fields = ['city']
    inlines       = [ActivityInline]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display  = ['name', 'stop', 'category', 'cost']
    list_filter   = ['category']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display  = ['trip', 'category', 'amount']
    list_filter   = ['category', 'trip']


@admin.register(PackingItem)
class PackingItemAdmin(admin.ModelAdmin):
    list_display  = ['item_name', 'trip', 'packed']
    list_filter   = ['packed', 'trip']
    search_fields = ['item_name']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display  = ['title', 'trip', 'created_at']
    search_fields = ['title', 'content']
