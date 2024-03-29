# Generated by Django 3.0.3 on 2020-04-14 13:42

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0018_auto_20200407_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('5bb568de-0448-463d-adc6-6e453a828661'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]
