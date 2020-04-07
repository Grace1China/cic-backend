# Generated by Django 2.2.7 on 2020-04-06 08:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0015_auto_20200406_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('ef34a9ad-44fd-49e4-8064-a8c1f0f19314'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]