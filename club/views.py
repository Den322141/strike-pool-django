import csv
import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .forms import PeriodForm
import re
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Booking, Category, GameType, MenuItem, Review, Tariff, Zone


logger = logging.getLogger(__name__)


def home(request):
    zones = Zone.objects.select_related("game_type").order_by("game_type_id", "number")
    today = timezone.localdate()
    rates = Tariff.objects.filter(weekday=today.weekday()).select_related("game_type").order_by("game_type_id", "start")
    return render(request, "club/home.html", {
        "games": GameType.objects.annotate(players=Max("zones__capacity")),
        "lanes": zones.filter(game_type__is_bowling=True),
        "tables": zones.filter(game_type__is_bowling=False),
        "tariffs": rates,
        "today": today,
        "reviews": Review.objects.order_by("-date", "-pk")[:6],
    })


def menu(request):
    items = MenuItem.objects.select_related("category").order_by("category__name", "name", "pk")
    return render(request, "club/menu.html", {
        "page": Paginator(items, 20).get_page(request.GET.get("page")),
        "categories": Category.objects.all(), "total": items.count(),
    })


def search(request):
    logger.debug("Начат поиск по меню")
    query = request.GET.get("q", "").strip()[:100]
    items = MenuItem.objects.select_related("category")
    category = request.GET.get("category", "")
    if category:
        items = items.filter(category__name=category)
    if query:
        term = re.escape(query)
        items = items.filter(Q(name__iregex=term) | Q(description__iregex=term) | Q(category__name__iregex=term))
    if request.GET.get("available") == "1":
        items = items.filter(active=True)
    for key, lookup in [("min_price", "price__gte"), ("max_price", "price__lte")]:
        raw = request.GET.get(key, "")
        if raw:
            try:
                amount = Decimal(raw)
                if not amount.is_finite() or not 0 <= amount <= 99999999:
                    raise ValueError
                items = items.filter(**{lookup: amount})
            except (InvalidOperation, ValueError):
                logger.warning("Отклонена граница цены: %s", key)
                items = items.none()
    order = request.GET.get("order")
    if order not in ("price", "-price"):
        order = "category__name"
    items = items.order_by(order, "name", "pk")
    return render(request, "club/search.html", {
        "page": Paginator(items, 20).get_page(request.GET.get("page")),
        "q": query, "submitted": bool(request.GET),
    })


def dish(request, pk):
    logger.debug("Открытие блюда id=%s", pk)
    item = get_object_or_404(MenuItem.objects.select_related("category"), pk=pk)
    return render(request, "club/dish.html", {"item": item})


def profile(request):
    cards = request.user.club_cards.all() if request.user.is_authenticated else []
    return render(request, "club/profile.html", {"cards": cards})


def booking_list(request):
    bookings = Booking.objects.filter(visitor=request.user).order_by("-starts_at", "-pk") if request.user.is_authenticated else Booking.objects.none()
    return render(request, "club/bookings.html", {"page": Paginator(bookings, 20).get_page(request.GET.get("page")), "can_export": request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name="Оператор").exists())})


def dashboard(request):
    return render(request, "club/dashboard.html", {
        "games": GameType.objects.count(), "zones": Zone.objects.filter(active=True).count(),
        "dishes": MenuItem.objects.filter(active=True).count(),
    })

@login_required(login_url="club:login")
def booking_record(request, pk, template_name):
    records = Booking.objects.filter(visitor=request.user).prefetch_related("zones__game_type")
    booking = get_object_or_404(records, pk=pk)
    return render(request, template_name, {"booking": booking})

@login_required(login_url="club:login")
def export_bookings(request):
    if not (request.user.is_superuser or request.user.groups.filter(name="Оператор").exists()):
        raise PermissionDenied
    form = PeriodForm(request.GET)
    if not form.is_valid():
        return render(request, "club/export.html", {"form": form})
    records = Booking.objects.filter(starts_at__date__range=(form.cleaned_data["start"], form.cleaned_data["end"]))
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(["Номер", "Начало", "Гости", "Статус"])
    for record in records:
        number = record.number
        if number.lstrip().startswith(("=", "+", "-", "@")):
            number = "'" + number
        writer.writerow([number, timezone.localtime(record.starts_at).isoformat(), record.guests, record.status])
    return response
