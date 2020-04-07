# Generated by Django 2.2.7 on 2020-04-07 12:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0017_auto_20200407_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('badd4c47-7232-493a-a015-d1ff4659cd33'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]