import re

from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Booking, Category, GameType, MenuItem, Review, Tariff, Zone


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
    items = MenuItem.objects.select_related("category").order_by("category_id", "name", "pk")
    category = request.GET.get("category", "")
    if category:
        items = items.filter(category__name=category)
    return render(request, "club/menu.html", {
        "page": Paginator(items, 20).get_page(request.GET.get("page")),
        "categories": Category.objects.all(), "category": category,
    })


def search(request):
    query = request.GET.get("q", "").strip()[:100]
    items = MenuItem.objects.select_related("category")
    if query:
        term = re.escape(query)
        items = items.filter(Q(name__iregex=term) | Q(description__iregex=term) | Q(category__name__iregex=term))
    else:
        items = items.none()
    return render(request, "club/search.html", {
        "page": Paginator(items.order_by("name", "pk"), 20).get_page(request.GET.get("page")), "q": query,
    })


def dish(request, pk):
    item = get_object_or_404(MenuItem.objects.select_related("category"), pk=pk)
    return render(request, "club/dish.html", {"item": item})


def booking_create(request):
    game = request.GET.get("game", "")
    try:
        guests = min(100, max(1, int(request.GET.get("guests", 1))))
    except ValueError:
        guests = 1
    zones = Zone.objects.filter(active=True, capacity__gte=guests).select_related("game_type")
    if game:
        zones = zones.filter(game_type__slug=game)
    return render(request, "club/booking_form.html", {
        "games": GameType.objects.all(), "game": game, "guests": guests, "zones": zones,
    })


def profile(request):
    cards = request.user.club_cards.all() if request.user.is_authenticated else []
    return render(request, "club/profile.html", {"cards": cards})


def booking_list(request):
    bookings = Booking.objects.filter(visitor=request.user).order_by("-starts_at", "-pk") if request.user.is_authenticated else Booking.objects.none()
    return render(request, "club/bookings.html", {"page": Paginator(bookings, 20).get_page(request.GET.get("page"))})


def dashboard(request):
    return render(request, "club/dashboard.html", {
        "games": GameType.objects.count(), "zones": Zone.objects.filter(active=True).count(),
        "dishes": MenuItem.objects.filter(active=True).count(),
    })
