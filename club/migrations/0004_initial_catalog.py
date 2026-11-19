import json
from pathlib import Path

from django.db import migrations


def load_initial_catalog(apps, schema_editor):
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "club_catalog.json"
    rows = json.loads(fixture.read_text(encoding="utf-8"))
    database = schema_editor.connection.alias
    models = {label: apps.get_model(label) for label in {row["model"] for row in rows}}
    if any(model.objects.using(database).exists() for model in models.values()):
        return

    for row in rows:
        model = models[row["model"]]
        fields = {model._meta.get_field(name).attname: value for name, value in row["fields"].items()}
        model.objects.using(database).create(pk=row["pk"], **fields)


class Migration(migrations.Migration):
    dependencies = [("club", "0003_contact")]
    operations = [migrations.RunPython(load_initial_catalog, migrations.RunPython.noop)]
