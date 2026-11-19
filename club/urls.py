from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView

from . import reservations, views

app_name = "club"
urlpatterns = [
    path("", views.home, name="home"),
    path("bookings/create/", reservations.reserve, name="booking_create"),
    path("api/quote/", reservations.quote, name="quote"),
    path("menu/", views.menu, name="menu_catalog"),
    path("menu/<int:pk>/", views.dish, name="dish"),
    path("search/", views.search, name="search"),
    path("about/", TemplateView.as_view(template_name="club/about.html"), name="about"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", LoginView.as_view(template_name="club/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="club:home"), name="logout"),
    path("register/", reservations.register, name="register"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/", views.booking_record, {"template_name": "club/booking_detail.html"}, name="booking_detail"),
    path("bookings/<int:pk>/edit/", reservations.edit, name="booking_edit"),
    path("bookings/<int:pk>/receipt/", views.booking_record, {"template_name": "club/receipt.html"}, name="receipt"),
]
