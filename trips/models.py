from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Stop(models.Model):
    trip           = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='stops')
    city           = models.CharField(max_length=200)
    arrival_date   = models.DateField()
    departure_date = models.DateField()
    order          = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.city} (Stop #{self.order} of '{self.trip.title}')"

    class Meta:
        ordering = ['order']


class Activity(models.Model):
    CATEGORY_CHOICES = [
        ('sightseeing', 'Sightseeing'),
        ('food',        'Food & Dining'),
        ('adventure',   'Adventure'),
        ('culture',     'Culture'),
        ('shopping',    'Shopping'),
        ('transport',   'Transport'),
        ('other',       'Other'),
    ]

    stop        = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='activities')
    name        = models.CharField(max_length=200)
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    cost        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} @ {self.stop.city}"


class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('accommodation', 'Accommodation'),
        ('food',          'Food & Dining'),
        ('transport',     'Transport'),
        ('activities',    'Activities'),
        ('shopping',      'Shopping'),
        ('health',        'Health'),
        ('other',         'Other'),
    ]

    trip     = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    amount   = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category} — ₹{self.amount} ({self.trip.title})"


class PackingItem(models.Model):
    trip      = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='packing_items')
    item_name = models.CharField(max_length=200)
    packed    = models.BooleanField(default=False)

    def __str__(self):
        return f"{'✓' if self.packed else '○'} {self.item_name}"


class Note(models.Model):
    trip       = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='notes')
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.trip.title})"

    class Meta:
        ordering = ['-created_at']
