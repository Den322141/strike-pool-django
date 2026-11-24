import logging

from uuid import uuid4

from django.core.mail import send_mail
from smtplib import SMTPException
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .forms import BookingForm, RegistrationForm
from .models import Booking, BookingZone, ChargeSegment, Contact, Zone


@require_http_methods(["GET", "POST"])
def register(request):
    logger = logging.getLogger(__name__)
    logger.debug("Регистрация: %s", request.method)
    if request.user.is_authenticated:
        return redirect("club:profile")
    with transaction.atomic():
        form = RegistrationForm(request.POST if request.method == "POST" else None)
        if request.method == "POST" and form.is_valid():
            user = form.save()
            Contact.objects.create(user=user, phone=form.cleaned_data["phone"])
            logger.info("Создан профиль id=%s", user.pk)
            login(request, user)
            messages.success(request, "Профиль создан.")
            return redirect("club:profile")
    return render(request, "club/register.html", {"form": form})


def notify_booking(record, action):
    if record.visitor.email:
        try:
            send_mail("Бронирование в Страйк и Пул", f"Бронь {record.number}: {action}.", None, [record.visitor.email])
        except (OSError, SMTPException):
            logging.getLogger(__name__).exception("Не удалось отправить уведомление о брони id=%s", record.pk)


def save_booking(form, user, record):
    data = form.cleaned_data
    if record is None:
        record = Booking(visitor=user, number="BK-" + uuid4().hex[:16].upper())
    record.starts_at = data["starts_at"]
    record.ends_at = data["ends_at"]
    record.guests = data["guests"]
    record.save()
    ChargeSegment.objects.filter(booking_zone__booking=record).delete()
    record.zone_links.all().delete()
    zones = list(data["zones"])
    remaining = record.guests - len(zones)
    for zone in zones:
        extra = min(remaining, zone.capacity - 1)
        link = BookingZone.objects.create(booking=record, zone=zone, assigned_guests=extra + 1)
        remaining -= extra
        ChargeSegment.objects.bulk_create([
            ChargeSegment(booking_zone=link, starts_at=a, ends_at=b, rate_snapshot=rate)
            for pk, a, b, rate in form.segments if pk == zone.pk
        ])
    return record


@require_http_methods(["GET", "POST"])
def reserve(request, pk=None):
    if request.method == "POST" and not request.user.is_authenticated:
        return redirect("club:login")
    with transaction.atomic():
        record = get_object_or_404(Booking, pk=pk, visitor=request.user) if pk else None
        initial = {"zones": Zone.objects.filter(game_type__slug=request.GET.get("game", ""), active=True)[:1]}
        zone_id = request.GET.get("zone", "")
        if zone_id.isascii() and zone_id.isdigit() and len(zone_id) <= 18:
            initial["zones"] = Zone.objects.filter(pk=int(zone_id), active=True)
        if record:
            if record.status != "confirmed" or record.starts_at <= timezone.now() or record.payments.exists():
                messages.info(request, "Изменить можно только предстоящую неоплаченную бронь.")
                return redirect("club:booking_detail", pk=pk)
            initial = {"starts_at": timezone.localtime(record.starts_at), "guests": record.guests,
                       "hours": (record.ends_at-record.starts_at).total_seconds()/3600, "zones": record.zones.all()}
        form = BookingForm(request.POST if request.method == "POST" else None, initial=initial, booking=record)
        if request.method == "POST" and form.is_valid():
            try:
                record = save_booking(form, request.user, record)
            except DatabaseError:
                logging.getLogger(__name__).exception("Ошибка записи брони")
                raise
            logging.getLogger(__name__).info("Сохранена бронь id=%s", record.pk)
            if pk is None:
                transaction.on_commit(lambda: notify_booking(record, "создана"))
            messages.success(request, f"Бронь сохранена. Стоимость: {form.total:.2f} ₽.")
            return redirect("club:booking_detail", pk=record.pk)
    return render(request, "club/booking_form.html", {"form": form, "booking": record})


@login_required(login_url="club:login")
def edit(request, pk):
    return reserve(request, pk)


@require_GET
def quote(request):
    pk = request.GET.get("booking")
    record = None
    if pk:
        if not request.user.is_authenticated or not pk.isascii() or not pk.isdigit() or len(pk)>18:
            return JsonResponse({"error": "Бронь недоступна."}, status=400)
        record = get_object_or_404(Booking, pk=int(pk), visitor=request.user)
    form = BookingForm(request.GET, booking=record)
    if form.is_valid():
        return JsonResponse({"total": format(form.total, ".2f")})
    return JsonResponse({"errors": form.errors.get_json_data()})
