from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as StaticRunserver
from django.core.management import call_command
from django.db import connection


class Command(StaticRunserver):
    def check_migrations(self):
        local_database = settings.BASE_DIR / "db.sqlite3"
        if (settings.DEBUG and connection.vendor == "sqlite"
                and connection.settings_dict["NAME"] == local_database
                and not connection.introspection.table_names()):
            self.stdout.write("Первый запуск. Создаём таблицы и загружаем каталог клуба.")
            call_command("migrate", interactive=False, stdout=self.stdout)
        super().check_migrations()
