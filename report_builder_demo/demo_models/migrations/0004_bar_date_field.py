from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demo_models', '0003_auto_20150419_2110'),
    ]

    operations = [
        migrations.AddField(
            model_name='bar',
            name='date_field',
            field=models.DateField(null=True, blank=True),
        ),
    ]
