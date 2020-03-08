# Generated by Django 2.2.7 on 2020-03-08 15:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20200308_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.UUID('b668b8f9-d0f2-416f-9f14-f7fb58230481'), editable=False, unique=True, verbose_name='订单号'),
        ),
    ]
