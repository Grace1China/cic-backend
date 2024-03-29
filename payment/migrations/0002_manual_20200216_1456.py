# Generated by Django 3.0.3 on 2020-02-16 06:56

# Generated by Django 3.0.3 on 2020-02-15 16:59


from django.db import migrations
from payment.models import IAPPrice
import csv

#测试数据
# productids = ["com.silverlinings.ios.NobelPrize.c.1",
#             "com.silverlinings.ios.NobelPrize.c.3",
#             "com.silverlinings.ios.NobelPrize.c.6",
#             "com.silverlinings.ios.NobelPrize.c.12"]
# codes = ["Alternate Tier A", "Alternate Tier B", "Tier 1", "Tier 2"]
# descs = ["12元课程","98元课程","998元课程","2998元课程"]

# 正式数据
productids = ["com.churchplatform.churchplatform.iap.c.tier2",
            "com.churchplatform.churchplatform.iap.c.tier15",
            "com.churchplatform.churchplatform.iap.c.tier66",
            "com.churchplatform.churchplatform.iap.c.tier81"]
codes = ["Tier 2","Tier 15","Tier 66","Tier 81"]
descs = ["12元课程","98元课程","998元课程","2998元课程"]


#添加事务？
def forwards_func(apps, schema_editor):
    # init iap_price
    with open('payment/iap_price.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            p = IAPPrice(code=row['Code'],
                         price=row['Price_CNY'],
                         proceeds=row['Proceeds_CNY'],
                         price_usd=row['Price_USD'],
                         proceeds_usd=row['Proceeds_USD'])
            p.save()

    # init iap_charge   
    IAPPricem = apps.get_model("payment", "IAPPrice")
    p1 = IAPPricem.objects.get(code=codes[0])
    p2 = IAPPricem.objects.get(code=codes[1])
    p3 = IAPPricem.objects.get(code=codes[2])
    p4 = IAPPricem.objects.get(code=codes[3])

    IAPCharge = apps.get_model("payment", "IAPCharge")
    db_alias = schema_editor.connection.alias
    IAPCharge.objects.using(db_alias).bulk_create([

        IAPCharge(price_code=p1, product_id=productids[0], desc=descs[0], price=p1.price),
        # 客户端根据price_code计算在apple上的product_id
        IAPCharge(price_code=p2, product_id=productids[1], desc=descs[1], price=p2.price),
        IAPCharge(price_code=p3, product_id=productids[2], desc=descs[2], price=p3.price),
        IAPCharge(price_code=p4, product_id=productids[3], desc=descs[3], price=p4.price),
    ])


#如何执行reverse？
def reverse_func(apps, schema_editor):
    IAPCharge = apps.get_model("payment", "IAPCharge")
    db_alias = schema_editor.connection.alias
    IAPCharge.objects.using(db_alias).filter(product_id=productids[0]).delete()
    IAPCharge.objects.using(db_alias).filter(product_id=productids[1]).delete()
    IAPCharge.objects.using(db_alias).filter(product_id=productids[2]).delete()
    IAPCharge.objects.using(db_alias).filter(product_id=productids[3]).delete()

    print("----------")

    IAPPricem = apps.get_model("payment", "IAPPrice")
    db_alias = schema_editor.connection.alias
    IAPPricem.objects.using(db_alias).bulk_delete() #语法是否错误？？？


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
