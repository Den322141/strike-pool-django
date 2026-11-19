from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Booking, ChargeSegment, Zone, Contact


class ReservationTests(TestCase):
    fixtures = ["club_catalog"]

    def setUp(self):
        self.owner = User.objects.create_user("visitor")
        self.client.force_login(self.owner)
        start = (timezone.localtime() + timedelta(days=2)).replace(hour=17, minute=0)
        self.data = {"starts_at": start.strftime("%Y-%m-%dT%H:%M"), "hours": 2,
                     "guests": 7, "zones": list(Zone.objects.filter(game_type__is_bowling=True).values_list("id", flat=True)[:2])}

    def test_quote_create_edit_and_conflict(self):
        url = reverse("club:booking_create")
        quoted = self.client.get(reverse("club:quote"), self.data)
        self.assertEqual(quoted.status_code, 200)
        self.assertEqual(self.client.post(url, self.data).status_code, 302)
        booking = Booking.objects.get()
        self.assertEqual(ChargeSegment.objects.count(), 4)
        conflict = self.client.post(url, self.data)
        self.assertFormError(conflict.context["form"], "zones", "Одна из зон занята в это время.")
        edit_url = reverse("club:booking_edit", args=[booking.pk])
        self.assertEqual(self.client.post(edit_url, {**self.data, "hours": 1}).status_code, 302)
        self.assertEqual(ChargeSegment.objects.count(), 2)
        self.client.force_login(User.objects.create_user("other"))
        self.assertEqual(self.client.post(edit_url, self.data).status_code, 404)

    def test_capacity_and_guest_permissions(self):
        url = reverse("club:booking_create")
        response = self.client.post(url, {**self.data, "guests": 99})
        self.assertIn("guests", response.context["form"].errors)
        self.client.logout()
        self.assertEqual(self.client.post(url, self.data).status_code, 302)
        self.assertFalse(Booking.objects.exists())

    def test_registration(self):
        self.client.logout()
        url = reverse("club:register")
        fields = dict(username="newguest", first_name="Гость", email="guest@example.test",
                      phone="+79990001122", password1="Stone-Maple-589!", password2="Stone-Maple-589!")
        invalid = self.client.post(url, {**fields, "phone": "123"})
        self.assertIn("phone", invalid.context["form"].errors)
        self.assertEqual(invalid.context["form"]["email"].value(), fields["email"])
        self.assertRedirects(self.client.post(url, fields), reverse("club:profile"))
        self.assertEqual(Contact.objects.get().phone, fields["phone"])
