from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import Booking, BookingZone, ChargeSegment, MenuItem, Zone


@override_settings(DEBUG=False)
class ExceptionTests(TestCase):
    def test_missing_page(self):
        response = self.client.get("/menu/999999/")
        self.assertContains(response, "Страница не найдена", status_code=404)

    def test_export_permission(self):
        self.client.force_login(User.objects.create_user("visitor"))
        response = self.client.get("/bookings/export/")
        self.assertContains(response, "Доступ ограничен", status_code=403)

    def test_registration_preserves_input(self):
        response = self.client.post("/register/", {"username": "guest", "first_name": "123", "email": "guest@example.test"})
        self.assertContains(response, "Введите имя буквами")
        self.assertContains(response, "guest@example.test")
        self.assertFalse(User.objects.filter(username="guest").exists())

    def test_atomic_save(self):
        self.client.force_login(User.objects.create_user("visitor"))
        start = (timezone.localtime() + timedelta(days=2)).replace(hour=15, minute=0)
        self.client.raise_request_exception = False
        with patch.object(ChargeSegment.objects, "bulk_create", side_effect=DatabaseError("Тест записи")):
            response = self.client.post("/bookings/create/", {"starts_at": start.strftime("%Y-%m-%dT%H:%M"),
                                        "zones": [Zone.objects.first().pk], "hours": 1, "guests": 2})
        self.assertContains(response, "Не удалось обработать запрос", status_code=500)
        self.assertFalse(Booking.objects.exists())
        self.assertFalse(BookingZone.objects.exists())

    def test_empty_dashboard(self):
        MenuItem.objects.all().delete()
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["dishes"], 0)
