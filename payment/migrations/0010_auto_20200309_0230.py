# Generated by Django 3.0.4 on 2020-03-08 18:30

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20200309_0035'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('5257a761-6b99-4d3c-90a7-f916935238c0'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]
