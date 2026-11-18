import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Категории меню',
                'verbose_name_plural': 'Категории меню',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ClubSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('address', models.CharField(max_length=250, verbose_name='Адрес')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('opens', models.TimeField(verbose_name='Открытие')),
                ('closes', models.TimeField(verbose_name='Закрытие')),
                ('rules', models.TextField(verbose_name='Правила')),
            ],
            options={
                'verbose_name': 'Настройки клуба',
                'verbose_name_plural': 'Настройки клуба',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('is_bowling', models.BooleanField(default=False, verbose_name='Боулинг')),
            ],
            options={
                'verbose_name': 'Типы игр',
                'verbose_name_plural': 'Типы игр',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ClubCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=30, unique=True, verbose_name='Номер карты')),
                ('discount', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Скидка %')),
                ('valid_until', models.DateField(verbose_name='Действует до')),
                ('active', models.BooleanField(default=True, verbose_name='Активна')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='club_cards', to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Клубные карты',
                'verbose_name_plural': 'Клубные карты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=32, unique=True, verbose_name='Номер брони')),
                ('starts_at', models.DateTimeField(verbose_name='Начало')),
                ('ends_at', models.DateTimeField(verbose_name='Конец')),
                ('guests', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Гости')),
                ('discount_snapshot', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Применённая скидка %')),
                ('status', models.CharField(choices=[('confirmed', 'Подтверждена'), ('completed', 'Завершена'), ('cancelled', 'Отменена')], default='confirmed', max_length=20, verbose_name='Статус')),
                ('cancel_reason', models.CharField(blank=True, max_length=250, verbose_name='Причина отмены')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to=settings.AUTH_USER_MODEL, verbose_name='Посетитель')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='club.clubcard', verbose_name='Карта')),
            ],
            options={
                'verbose_name': 'Бронирования',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100, verbose_name='Действие')),
                ('old_status', models.CharField(blank=True, max_length=20, verbose_name='Прежний статус')),
                ('new_status', models.CharField(max_length=20, verbose_name='Новый статус')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='events', to='club.booking', verbose_name='Бронь')),
            ],
            options={
                'verbose_name': 'Журнал событий',
                'verbose_name_plural': 'Журнал событий',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена')),
                ('active', models.BooleanField(default=True, verbose_name='Доступно')),
                ('photo', models.ImageField(blank=True, upload_to='menu/', verbose_name='Фото')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='club.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Блюда меню',
                'verbose_name_plural': 'Блюда меню',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.CharField(max_length=64, unique=True, verbose_name='Номер чека')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Сумма')),
                ('paid_at', models.DateTimeField(verbose_name='Время оплаты')),
                ('method', models.CharField(choices=[('cash', 'Наличные'), ('terminal', 'Терминал клуба')], max_length=20, verbose_name='Способ')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='club.booking', verbose_name='Бронь')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recorded_payments', to=settings.AUTH_USER_MODEL, verbose_name='Оператор')),
            ],
            options={
                'verbose_name': 'Оплаты',
                'verbose_name_plural': 'Оплаты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Preorder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('accepted', 'Принят'), ('cooking', 'Готовится'), ('served', 'Выдан'), ('cancelled', 'Отменён')], default='new', max_length=20, verbose_name='Статус')),
                ('serve_at', models.DateTimeField(verbose_name='Время подачи')),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='preorder', to='club.booking', verbose_name='Бронь')),
            ],
            options={
                'verbose_name': 'Предзаказы',
                'verbose_name_plural': 'Предзаказы',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PreorderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('price_snapshot', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена при заказе')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_items', to='club.menuitem', verbose_name='Блюдо')),
                ('preorder', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='club.preorder', verbose_name='Предзаказ')),
            ],
            options={
                'verbose_name': 'Позиции предзаказов',
                'verbose_name_plural': 'Позиции предзаказов',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.PositiveSmallIntegerField(verbose_name='День недели 0–6')),
                ('start', models.TimeField(verbose_name='Начало')),
                ('end', models.TimeField(verbose_name='Конец')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Рублей в час')),
                ('game_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tariffs', to='club.gametype', verbose_name='Тип игры')),
            ],
            options={
                'verbose_name': 'Тарифные интервалы',
                'verbose_name_plural': 'Тарифные интервалы',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Номер')),
                ('name', models.CharField(max_length=120, verbose_name='Название')),
                ('capacity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Вместимость')),
                ('active', models.BooleanField(default=True, verbose_name='Доступна')),
                ('photo', models.ImageField(blank=True, upload_to='zones/', verbose_name='Фото')),
                ('game_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='zones', to='club.gametype', verbose_name='Тип игры')),
            ],
            options={
                'verbose_name': 'Игровые зоны',
                'verbose_name_plural': 'Игровые зоны',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='BookingZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_guests', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Гости на зоне')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='zone_links', to='club.booking', verbose_name='Бронь')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='booking_links', to='club.zone', verbose_name='Зона')),
            ],
            options={
                'verbose_name': 'Зоны в бронированиях',
                'verbose_name_plural': 'Зоны в бронированиях',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='zones',
            field=models.ManyToManyField(related_name='bookings', through='club.BookingZone', to='club.zone', verbose_name='Зоны'),
        ),
        migrations.CreateModel(
            name='ZoneBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField(verbose_name='Начало')),
                ('ends_at', models.DateTimeField(verbose_name='Конец')),
                ('reason', models.CharField(max_length=250, verbose_name='Причина')),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='blocks', to='club.zone', verbose_name='Зона')),
            ],
            options={
                'verbose_name': 'Недоступность зон',
                'verbose_name_plural': 'Недоступность зон',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ChargeSegment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField(verbose_name='Начало отрезка')),
                ('ends_at', models.DateTimeField(verbose_name='Конец отрезка')),
                ('rate_snapshot', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Историческая ставка в час')),
                ('booking_zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='segments', to='club.bookingzone', verbose_name='Зона брони')),
            ],
            options={
                'verbose_name': 'Отрезки расчёта',
                'verbose_name_plural': 'Отрезки расчёта',
                'ordering': ['id'],
                'constraints': [models.UniqueConstraint(fields=('booking_zone', 'starts_at'), name='booking_zone_starts_at_chargesegment_uniq'), models.CheckConstraint(condition=models.Q(('ends_at__gt', models.F('starts_at'))), name='chargesegment_period'), models.CheckConstraint(condition=models.Q(('rate_snapshot__gte', 0)), name='chargesegment_rate')],
            },
        ),
        migrations.AddConstraint(
            model_name='clubcard',
            constraint=models.CheckConstraint(condition=models.Q(('discount__gte', 0), ('discount__lte', 100)), name='clubcard_discount'),
        ),
        migrations.AddConstraint(
            model_name='menuitem',
            constraint=models.UniqueConstraint(fields=('category', 'name'), name='category_name_menuitem_uniq'),
        ),
        migrations.AddConstraint(
            model_name='menuitem',
            constraint=models.CheckConstraint(condition=models.Q(('price__gte', 0)), name='menuitem_price'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.CheckConstraint(condition=models.Q(('amount__gt', 0)), name='payment_amount'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.CheckConstraint(condition=models.Q(('method__in', ['cash', 'terminal'])), name='payment_method'),
        ),
        migrations.AddConstraint(
            model_name='preorder',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['new', 'accepted', 'cooking', 'served', 'cancelled'])), name='preorder_status'),
        ),
        migrations.AddConstraint(
            model_name='preorderitem',
            constraint=models.UniqueConstraint(fields=('preorder', 'menu_item'), name='preorder_menu_item_preorderitem_uniq'),
        ),
        migrations.AddConstraint(
            model_name='preorderitem',
            constraint=models.CheckConstraint(condition=models.Q(('quantity__gte', 1)), name='preorderitem_quantity'),
        ),
        migrations.AddConstraint(
            model_name='preorderitem',
            constraint=models.CheckConstraint(condition=models.Q(('price_snapshot__gte', 0)), name='preorderitem_price'),
        ),
        migrations.AddConstraint(
            model_name='tariff',
            constraint=models.UniqueConstraint(fields=('game_type', 'weekday', 'start'), name='game_type_weekday_start_tariff_uniq'),
        ),
        migrations.AddConstraint(
            model_name='tariff',
            constraint=models.CheckConstraint(condition=models.Q(('weekday__lte', 6)), name='tariff_weekday'),
        ),
        migrations.AddConstraint(
            model_name='tariff',
            constraint=models.CheckConstraint(condition=models.Q(('end__gt', models.F('start'))), name='tariff_period'),
        ),
        migrations.AddConstraint(
            model_name='tariff',
            constraint=models.CheckConstraint(condition=models.Q(('rate__gte', 0)), name='tariff_rate'),
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.UniqueConstraint(fields=('game_type', 'number'), name='game_type_number_zone_uniq'),
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.CheckConstraint(condition=models.Q(('capacity__gte', 1)), name='zone_capacity'),
        ),
        migrations.AddConstraint(
            model_name='zone',
            constraint=models.CheckConstraint(condition=models.Q(('number__gte', 1)), name='zone_number'),
        ),
        migrations.AddConstraint(
            model_name='bookingzone',
            constraint=models.UniqueConstraint(fields=('booking', 'zone'), name='booking_zone_bookingzone_uniq'),
        ),
        migrations.AddConstraint(
            model_name='bookingzone',
            constraint=models.CheckConstraint(condition=models.Q(('assigned_guests__gte', 1)), name='bookingzone_guests'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('ends_at__gt', models.F('starts_at'))), name='booking_period'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('guests__gte', 1)), name='booking_guests'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('discount_snapshot__gte', 0), ('discount_snapshot__lte', 100)), name='booking_discount'),
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['confirmed', 'completed', 'cancelled'])), name='booking_status'),
        ),
        migrations.AddConstraint(
            model_name='zoneblock',
            constraint=models.CheckConstraint(condition=models.Q(('ends_at__gt', models.F('starts_at'))), name='zoneblock_period'),
        ),
    ]
