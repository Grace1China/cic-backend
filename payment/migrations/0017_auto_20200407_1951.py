# Generated by Django 2.2.7 on 2020-04-07 11:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0016_auto_20200406_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('51df8249-1baf-4fec-ac4e-f6dcf3665e47'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]