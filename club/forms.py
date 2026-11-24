from datetime import timedelta
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Booking, Tariff, Zone, ZoneBlock


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Ваше имя", min_length=2, max_length=80)
    email = forms.EmailField(label="Электронная почта", max_length=254)
    phone = forms.RegexField(label="Телефон", regex=r"^\+?[0-9]{10,15}\Z", max_length=16,
                            widget=forms.TextInput(attrs={"type": "tel", "pattern": r"\+?[0-9]{10,15}", "placeholder": "+79991234567"}),
                            error_messages={"invalid": "Введите от 10 до 15 цифр, можно начать с плюса."})

    def clean_first_name(self):
        name = self.cleaned_data["first_name"]
        if not any(letter.isalpha() for letter in name):
            raise ValidationError("Введите имя буквами, например Анна.")
        return name

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "email", "phone", "password1", "password2")


class BookingForm(forms.Form):
    starts_at = forms.DateTimeField(label="Начало игры", input_formats=["%Y-%m-%dT%H:%M"],
                                   widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}))
    hours = forms.IntegerField(label="Продолжительность, ч", min_value=1, max_value=8, initial=1)
    guests = forms.IntegerField(label="Количество гостей", min_value=1, max_value=100, initial=1)
    zones = forms.ModelMultipleChoiceField(label="Дорожки и столы", queryset=Zone.objects.none(),
                                          widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, booking=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking = booking
        self.fields["zones"].queryset = Zone.objects.filter(active=True).order_by("game_type", "number")
        self.fields["zones"].label_from_instance = lambda z: f"{z.name} · до {z.capacity} гостей"
        self.segments = []
        self.total = Decimal(0)

    def clean(self):
        data = super().clean()
        if self.errors:
            return data
        start = data["starts_at"]
        if start.year >= 9999:
            self.add_error("starts_at", "Проверьте год бронирования.")
            return data
        end = start + timedelta(hours=data["hours"])
        zones = list(data["zones"])
        if start <= timezone.now():
            self.add_error("starts_at", "Выберите время в будущем.")
        if not len(zones) <= data["guests"] <= sum(zone.capacity for zone in zones):
            message = "Число гостей должно соответствовать вместимости выбранных зон. На каждую зону нужен хотя бы один гость."
            if data["guests"] == 7 and len(zones) == 1 and zones[0].game_type.is_bowling:
                message = "Для семи гостей выберите две дорожки."
            self.add_error("guests", message)
        busy = Booking.objects.filter(zones__in=zones, starts_at__lt=end, ends_at__gt=start, status="confirmed")
        if self.booking:
            busy = busy.exclude(pk=self.booking.pk)
        if busy.exists() or ZoneBlock.objects.filter(zone__in=zones, starts_at__lt=end, ends_at__gt=start).exists():
            self.add_error("zones", "Одна из зон занята в это время.")
        if self.errors:
            return data
        rates = list(Tariff.objects.filter(game_type_id__in={z.game_type_id for z in zones}))
        discount = self.booking.discount_snapshot if self.booking else 0
        for zone in zones:
            cursor = timezone.localtime(start)
            while cursor < end:
                rate = next((r for r in rates if r.game_type_id == zone.game_type_id and r.weekday == cursor.weekday()
                             and r.start <= cursor.time() < r.end), None)
                if rate is None:
                    self.add_error("starts_at", "Часть выбранного времени вне часов работы клуба.")
                    return data
                boundary = cursor.replace(hour=rate.end.hour, minute=rate.end.minute, second=rate.end.second, microsecond=rate.end.microsecond)
                if rate.end.isoformat() == "23:59:59":
                    boundary += timedelta(seconds=1)
                until = min(end, boundary)
                seconds = int((until - cursor).total_seconds())
                self.total += rate.rate * seconds / 3600
                self.segments.append((zone.pk, cursor, until, rate.rate))
                cursor = until
        self.total = (self.total * (100 - discount) / 100).quantize(Decimal("0.01"))
        data["ends_at"] = end
        return data

class PeriodForm(forms.Form):
    start = forms.DateField(label="С даты", widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(label="По дату", widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end") and data["end"] < data["start"]:
            self.add_error("end", "Укажите дату окончания после начала периода.")
        return data
