from django.shortcuts import render

from .demo_content import GAMES, LANES, REVIEWS, TABLES, TARIFFS


def home(request):
    return render(request, "club/home.html", {
        "games": GAMES,
        "lanes": LANES,
        "tables": TABLES,
        "tariffs": TARIFFS,
        "reviews": REVIEWS,
    })


def section(request, title):
    return render(request, "club/section.html", {"title": title})
