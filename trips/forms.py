from django import forms
from django.utils import timezone

from .models import (
    Trip,
    Stop,
    Activity,
    Expense,
    PackingItem,
    Note,
)


class TripForm(forms.ModelForm):

    class Meta:
        model = Trip

        fields = [
            'title',
            'description',
            'start_date',
            'end_date',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Goa Summer Trip',
                'class': 'form-control',
            }),

            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'What is this trip about?',
                'class': 'form-control',
            }),

            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),

            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date   = cleaned_data.get('end_date')
        today      = timezone.now().date()

        if start_date:
            if start_date < today:
                self.add_error(
                    'start_date',
                    "Start date cannot be in the past."
                )

        if start_date and end_date:
            if end_date < start_date:
                self.add_error(
                    'end_date',
                    "End date must be on or after the start date."
                )

        return cleaned_data


class StopForm(forms.ModelForm):
    """
    Validates that:
      • arrival  >= today
      • departure >= arrival
    Cross-trip validation (stop dates inside trip dates) is done in the view
    where the trip instance is available.
    """

    class Meta:
        model = Stop

        fields = [
            'city',
            'arrival_date',
            'departure_date',
            'order',
        ]

        widgets = {
            'city': forms.TextInput(attrs={
                'placeholder': 'e.g. Mumbai',
                'class': 'form-control',
            }),

            'arrival_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),

            'departure_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),

            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        arrival    = cleaned_data.get('arrival_date')
        departure  = cleaned_data.get('departure_date')
        today      = timezone.now().date()

        if arrival and arrival < today:
            self.add_error(
                'arrival_date',
                "Arrival date cannot be in the past."
            )

        if arrival and departure:
            if departure < arrival:
                self.add_error(
                    'departure_date',
                    "Departure date must be on or after the arrival date."
                )

        return cleaned_data


class ActivityForm(forms.ModelForm):

    class Meta:
        model = Activity

        fields = [
            'name',
            'category',
            'cost',
            'description',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Scuba Diving',
                'class': 'form-control',
            }),

            'category': forms.Select(attrs={
                'class': 'form-control',
            }),

            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
            }),

            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
            }),
        }

    def clean_cost(self):
        cost = self.cleaned_data['cost']
        if cost < 0:
            raise forms.ValidationError("Cost cannot be negative.")
        return cost


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            'category',
            'amount',
        ]

        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),

            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 0:
            raise forms.ValidationError("Amount cannot be negative.")
        return amount


class PackingItemForm(forms.ModelForm):

    class Meta:
        model = PackingItem

        fields = [
            'item_name',
            'packed',
        ]

        widgets = {
            'item_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Sunscreen',
                'class': 'form-control',
            }),
        }


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note

        fields = [
            'title',
            'content',
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Note title',
                'class': 'form-control',
            }),

            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
            }),
        }
