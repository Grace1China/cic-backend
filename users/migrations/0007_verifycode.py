# Generated by Django 3.0.3 on 2020-04-14 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20191217_2118'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerifyCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='电子邮件')),
                ('verify_code', models.CharField(max_length=6, verbose_name='验证码')),
            ],
        ),
    ]
