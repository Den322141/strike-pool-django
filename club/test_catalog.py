from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, Category, MenuItem


class CatalogTests(TestCase):
    fixtures = ["club_catalog"]

    def test_search_keeps_filters_on_second_page(self):
        category = Category.objects.first()
        MenuItem.objects.bulk_create([
            MenuItem(name=f"Тестовое блюдо {i}", category=category, price=i, active=True)
            for i in range(24)
        ])
        params = {"q": "ТЕСТОВОЕ", "order": "-price", "available": "1", "min_price": "2"}
        first = self.client.get(reverse("club:search"), params)
        self.assertEqual(len(first.context["page"]), 20)
        self.assertContains(first, "page=2")
        last = self.client.get(reverse("club:search"), {**params, "page": 2})
        self.assertEqual([item.price for item in last.context["page"]], [3, 2])

    def test_detail_reflects_price_change(self):
        item = MenuItem.objects.first()
        item.price = 321
        item.save(update_fields=["price"])
        self.assertContains(self.client.get(reverse("club:dish", args=[item.pk])), "321,00")


class BookingPrivacyTests(TestCase):
    def test_only_owner_can_read_ticket(self):
        owner = get_user_model().objects.create_user("owner")
        visitor = get_user_model().objects.create_user("visitor")
        start = timezone.now()
        record = Booking.objects.create(number="TEST", visitor=owner, starts_at=start,
                                        ends_at=start + timedelta(hours=1), guests=2)
        url = reverse("club:receipt", args=[record.pk])
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(visitor)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_login(owner)
        self.assertContains(self.client.get(url), "TEST")
