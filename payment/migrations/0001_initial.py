# Generated by Django 3.0.3 on 2020-02-16 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IAPPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(db_index=True, default='', help_text='iap内购价格码，来自apple', max_length=32, unique=True, verbose_name='内购价格码')),
                ('price', models.DecimalField(db_index=True, decimal_places=2, default=0, max_digits=9, verbose_name='人民币价格')),
                ('proceeds', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='人民币收入价格')),
                ('price_usd', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='美金价格')),
                ('proceeds_usd', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='美金收入价格')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
            ],
            options={
                'ordering': ['price'],
            },
        ),
        migrations.CreateModel(
            name='IAPCharge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('product_id', models.CharField(max_length=255, unique=True, verbose_name='充值产品在apple上的真实id。不传给客户端，客户端根据product_code计算')),
                ('desc', models.CharField(max_length=255, verbose_name='充值产品文案描述')),
                ('create_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('price_code', models.ForeignKey(db_column='price_code', on_delete=django.db.models.deletion.DO_NOTHING, to='payment.IAPPrice', to_field='code')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='人民币价格价格')),
            ],
        ),
    ]
