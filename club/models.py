from django.db import models
from django.db.models import Q, F
from django.core.validators import MinValueValidator

class GameType(models.Model):
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    label = models.CharField(max_length=80, blank=True)
    image = models.CharField(max_length=120, blank=True)

    name = models.CharField("Название", max_length=100, unique=True)
    is_bowling = models.BooleanField("Боулинг", default=False)

    class Meta:
        verbose_name = "Типы игр"
        verbose_name_plural = "Типы игр"
        ordering = ["id"]

    def __str__(self):
        return f"GameType {self.name}"


class Zone(models.Model):
    vip = models.BooleanField(default=False)

    game_type = models.ForeignKey('GameType', verbose_name="Тип игры", on_delete=models.PROTECT, related_name="zones")
    number = models.PositiveIntegerField("Номер", validators=[MinValueValidator(1)])
    name = models.CharField("Название", max_length=120)
    capacity = models.PositiveIntegerField("Вместимость", validators=[MinValueValidator(1)])
    active = models.BooleanField("Доступна", default=True)
    photo = models.ImageField("Фото", upload_to="zones/", blank=True)

    class Meta:
        verbose_name = "Игровые зоны"
        verbose_name_plural = "Игровые зоны"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['game_type', 'number'], name="game_type_number_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(capacity__gte=1), name="%(class)s_capacity"),
            models.CheckConstraint(condition=Q(number__gte=1), name="%(class)s_number"),
        ]

    def __str__(self):
        return f"Zone {self.name}"


class Tariff(models.Model):
    game_type = models.ForeignKey('GameType', verbose_name="Тип игры", on_delete=models.PROTECT, related_name="tariffs")
    weekday = models.PositiveSmallIntegerField("День недели 0–6")
    start = models.TimeField("Начало")
    end = models.TimeField("Конец")
    rate = models.DecimalField("Рублей в час", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Тарифные интервалы"
        verbose_name_plural = "Тарифные интервалы"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['game_type', 'weekday', 'start'], name="game_type_weekday_start_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(weekday__lte=6), name="%(class)s_weekday"),
            models.CheckConstraint(condition=Q(end__gt=F("start")), name="%(class)s_period"),
            models.CheckConstraint(condition=Q(rate__gte=0), name="%(class)s_rate"),
        ]

    def __str__(self):
        return f"Tariff {self.pk}"


class ClubCard(models.Model):
    owner = models.ForeignKey('auth.User', verbose_name="Владелец", on_delete=models.PROTECT, related_name="club_cards")
    number = models.CharField("Номер карты", max_length=30, unique=True)
    discount = models.DecimalField("Скидка %", max_digits=5, decimal_places=2)
    valid_until = models.DateField("Действует до")
    active = models.BooleanField("Активна", default=True)

    class Meta:
        verbose_name = "Клубные карты"
        verbose_name_plural = "Клубные карты"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(discount__gte=0,discount__lte=100), name="%(class)s_discount"),
        ]

    def __str__(self):
        return f"ClubCard {self.number}"


class Booking(models.Model):
    number = models.CharField("Номер брони", max_length=32, unique=True)
    visitor = models.ForeignKey('auth.User', verbose_name="Посетитель", on_delete=models.PROTECT, related_name="bookings")
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Конец")
    guests = models.PositiveIntegerField("Гости", validators=[MinValueValidator(1)])
    card = models.ForeignKey('ClubCard', verbose_name="Карта", on_delete=models.PROTECT, related_name="bookings", null=True, blank=True)
    discount_snapshot = models.DecimalField("Применённая скидка %", max_digits=5, decimal_places=2, default=0)
    status = models.CharField("Статус", max_length=20, choices=[("confirmed","Подтверждена"),("completed","Завершена"),("cancelled","Отменена")], default="confirmed")
    cancel_reason = models.CharField("Причина отмены", max_length=250, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    zones = models.ManyToManyField("Zone", through="BookingZone", related_name="bookings", verbose_name="Зоны")

    class Meta:
        verbose_name = "Бронирования"
        verbose_name_plural = "Бронирования"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(ends_at__gt=F("starts_at")), name="%(class)s_period"),
            models.CheckConstraint(condition=Q(guests__gte=1), name="%(class)s_guests"),
            models.CheckConstraint(condition=Q(discount_snapshot__gte=0,discount_snapshot__lte=100), name="%(class)s_discount"),
            models.CheckConstraint(condition=Q(status__in=["confirmed","completed","cancelled"]), name="%(class)s_status"),
        ]

    def __str__(self):
        return f"Booking {self.number}"


class BookingZone(models.Model):
    booking = models.ForeignKey('Booking', verbose_name="Бронь", on_delete=models.PROTECT, related_name="zone_links")
    zone = models.ForeignKey('Zone', verbose_name="Зона", on_delete=models.PROTECT, related_name="booking_links")
    assigned_guests = models.PositiveIntegerField("Гости на зоне", validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Зоны в бронированиях"
        verbose_name_plural = "Зоны в бронированиях"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['booking', 'zone'], name="booking_zone_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(assigned_guests__gte=1), name="%(class)s_guests"),
        ]

    def __str__(self):
        return f"BookingZone {self.pk}"


class ChargeSegment(models.Model):
    booking_zone = models.ForeignKey('BookingZone', verbose_name="Зона брони", on_delete=models.PROTECT, related_name="segments")
    starts_at = models.DateTimeField("Начало отрезка")
    ends_at = models.DateTimeField("Конец отрезка")
    rate_snapshot = models.DecimalField("Историческая ставка в час", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Отрезки расчёта"
        verbose_name_plural = "Отрезки расчёта"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['booking_zone', 'starts_at'], name="booking_zone_starts_at_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(ends_at__gt=F("starts_at")), name="%(class)s_period"),
            models.CheckConstraint(condition=Q(rate_snapshot__gte=0), name="%(class)s_rate"),
        ]

    def __str__(self):
        return f"ChargeSegment {self.pk}"


class Category(models.Model):
    name = models.CharField("Название", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категории меню"
        verbose_name_plural = "Категории меню"
        ordering = ["id"]

    def __str__(self):
        return f"Category {self.name}"


class MenuItem(models.Model):
    description = models.TextField(blank=True)
    portion = models.CharField(max_length=80, blank=True)
    image = models.CharField(max_length=120, blank=True)

    category = models.ForeignKey('Category', verbose_name="Категория", on_delete=models.PROTECT, related_name="items")
    name = models.CharField("Название", max_length=120)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    active = models.BooleanField("Доступно", default=True)
    photo = models.ImageField("Фото", upload_to="menu/", blank=True)

    class Meta:
        verbose_name = "Блюда меню"
        verbose_name_plural = "Блюда меню"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'], name="category_name_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(price__gte=0), name="%(class)s_price"),
        ]

    def __str__(self):
        return f"MenuItem {self.name}"


class Preorder(models.Model):
    booking = models.OneToOneField('Booking', verbose_name="Бронь", on_delete=models.PROTECT, related_name="preorder")
    status = models.CharField("Статус", max_length=20, choices=[("new","Новый"),("accepted","Принят"),("cooking","Готовится"),("served","Выдан"),("cancelled","Отменён")], default="new")
    serve_at = models.DateTimeField("Время подачи")

    class Meta:
        verbose_name = "Предзаказы"
        verbose_name_plural = "Предзаказы"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(status__in=["new","accepted","cooking","served","cancelled"]), name="%(class)s_status"),
        ]

    def __str__(self):
        return f"Preorder {self.pk}"


class PreorderItem(models.Model):
    preorder = models.ForeignKey('Preorder', verbose_name="Предзаказ", on_delete=models.PROTECT, related_name="items")
    menu_item = models.ForeignKey('MenuItem', verbose_name="Блюдо", on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField("Количество", validators=[MinValueValidator(1)])
    price_snapshot = models.DecimalField("Цена при заказе", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Позиции предзаказов"
        verbose_name_plural = "Позиции предзаказов"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=['preorder', 'menu_item'], name="preorder_menu_item_%(class)s_uniq"),
            models.CheckConstraint(condition=Q(quantity__gte=1), name="%(class)s_quantity"),
            models.CheckConstraint(condition=Q(price_snapshot__gte=0), name="%(class)s_price"),
        ]

    def __str__(self):
        return f"PreorderItem {self.pk}"


class Payment(models.Model):
    booking = models.ForeignKey('Booking', verbose_name="Бронь", on_delete=models.PROTECT, related_name="payments")
    operator = models.ForeignKey('auth.User', verbose_name="Оператор", on_delete=models.PROTECT, related_name="recorded_payments")
    receipt = models.CharField("Номер чека", max_length=64, unique=True)
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_at = models.DateTimeField("Время оплаты")
    method = models.CharField("Способ", max_length=20, choices=[("cash","Наличные"),("terminal","Терминал клуба")])

    class Meta:
        verbose_name = "Оплаты"
        verbose_name_plural = "Оплаты"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="%(class)s_amount"),
            models.CheckConstraint(condition=Q(method__in=["cash","terminal"]), name="%(class)s_method"),
        ]

    def __str__(self):
        return f"Payment {self.receipt}"


class Event(models.Model):
    booking = models.ForeignKey('Booking', verbose_name="Бронь", on_delete=models.PROTECT, related_name="events")
    actor = models.ForeignKey('auth.User', verbose_name="Автор", on_delete=models.PROTECT, related_name="events")
    action = models.CharField("Действие", max_length=100)
    old_status = models.CharField("Прежний статус", max_length=20, blank=True)
    new_status = models.CharField("Новый статус", max_length=20)
    created_at = models.DateTimeField("Время", auto_now_add=True)

    class Meta:
        verbose_name = "Журнал событий"
        verbose_name_plural = "Журнал событий"
        ordering = ["id"]

    def __str__(self):
        return f"Event {self.pk}"


class ZoneBlock(models.Model):
    zone = models.ForeignKey('Zone', verbose_name="Зона", on_delete=models.PROTECT, related_name="blocks")
    starts_at = models.DateTimeField("Начало")
    ends_at = models.DateTimeField("Конец")
    reason = models.CharField("Причина", max_length=250)

    class Meta:
        verbose_name = "Недоступность зон"
        verbose_name_plural = "Недоступность зон"
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(condition=Q(ends_at__gt=F("starts_at")), name="%(class)s_period"),
        ]

    def __str__(self):
        return f"ZoneBlock {self.pk}"


class ClubSettings(models.Model):
    name = models.CharField("Название", max_length=120)
    address = models.CharField("Адрес", max_length=250)
    phone = models.CharField("Телефон", max_length=30)
    opens = models.TimeField("Открытие")
    closes = models.TimeField("Закрытие")
    rules = models.TextField("Правила")

    class Meta:
        verbose_name = "Настройки клуба"
        verbose_name_plural = "Настройки клуба"
        ordering = ["id"]

    def __str__(self):
        return f"ClubSettings {self.name}"



class Review(models.Model):
    name = models.CharField(max_length=100)
    text = models.TextField()
    date = models.DateField()
    rating = models.PositiveSmallIntegerField(default=5)


class Contact(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="club_contact")
    phone = models.CharField(max_length=16)
