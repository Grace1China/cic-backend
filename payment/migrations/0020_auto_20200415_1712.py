# Generated by Django 2.2.7 on 2020-04-15 09:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0019_auto_20200415_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_no',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, verbose_name='订单号'),
        ),
    ]
