from django.urls import path

from . import views

app_name = "club"

urlpatterns = [
    path("", views.home, name="home"),
    path("bookings/create/", views.section, {"title": "Бронирование"}, name="booking_create"),
    path("menu/", views.section, {"title": "Бар и кухня"}, name="menu_catalog"),
    path("dashboard/", views.section, {"title": "Показатели"}, name="dashboard"),
    path("login/", views.section, {"title": "Вход в личный кабинет"}, name="login"),
    path("register/", views.section, {"title": "Регистрация"}, name="register"),
    path("bookings/", views.section, {"title": "Мои бронирования"}, name="booking_list"),
]
