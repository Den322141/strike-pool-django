from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import get_random_string

from club.models import Booking, BookingZone, ClubCard, Zone, ZoneBlock


class Command(BaseCommand):
    help = "Подготовить пользователей и брони в отдельной базе занятия 13."

    @transaction.atomic
    def handle(self, *args, **options):
        if settings.DATABASES["default"]["NAME"] != settings.BASE_DIR / "lab13.sqlite3":
            raise CommandError("Используйте --settings=config.lab13")
        if User.objects.filter(username__startswith="lab13_").exists():
            raise CommandError("Набор уже существует.")
        password = get_random_string(18)
        users = {}
        for suffix, role in [("a", "Посетитель"), ("b", "Посетитель"), ("op", "Оператор"), ("bar", "Менеджер бара"), ("admin", "Администратор")]:
            user = User.objects.create_user("lab13_" + suffix, password=password,
                                            is_staff=suffix == "admin", is_superuser=suffix == "admin")
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            users[suffix] = user
        start = (timezone.localtime() + timedelta(days=7)).replace(hour=15, minute=0, second=0, microsecond=0)
        zones = list(Zone.objects.filter(game_type__is_bowling=True).order_by("number")[:3])
        for number, owner, status, offset in [("A","a","confirmed",0),("B","b","confirmed",1),("C","a","cancelled",2),("D","a","completed",-10)]:
            begin = start + timedelta(days=offset)
            booking = Booking.objects.create(number="QA-"+number, visitor=users[owner], starts_at=begin,
                                             ends_at=begin+timedelta(hours=1), guests=2,status=status)
            BookingZone.objects.create(booking=booking,zone=zones[0],assigned_guests=2)
        ZoneBlock.objects.create(zone=zones[2],starts_at=start,ends_at=start+timedelta(hours=1),reason="Учебное обслуживание")
        ClubCard.objects.create(number="QA10",owner=users["a"],discount=10,valid_until=start.date()+timedelta(days=30),active=True)
        self.stdout.write(f"Начало QA-A: {start}. Локальный пароль учебных ролей: {password}")

