from django.db import models
from church.models import Course
from churchs.models import CustomUser
import uuid
import json
import django.utils.timezone as timezone
from django_mysql.models import JSONField

# Create your models here.
class IAPPrice(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=32,unique=True, db_index=True,default='',verbose_name='内购价格码',help_text='iap内购价格码，来自apple')
    price = models.DecimalField(default=0,max_digits=9, decimal_places=2, db_index=True,verbose_name='人民币价格')
    proceeds = models.DecimalField(default=0,max_digits=9, decimal_places=2,verbose_name='人民币收入价格')
    price_usd = models.DecimalField(default=0,max_digits=9, decimal_places=2,verbose_name='美金价格')
    proceeds_usd = models.DecimalField(default=0,max_digits=9, decimal_places=2,verbose_name='美金收入价格')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['price']
    
class IAPCharge(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.CharField(max_length=255,unique=True, verbose_name='充值产品在apple上的真实id。不传给客户端，客户端根据product_code计算')
    
    #db_column本表列名，不写则为price_code_id。to_field是关联表外键列名，不写则默认id。
    price_code = models.ForeignKey(IAPPrice,on_delete=models.DO_NOTHING, db_column='price_code', to_field='code')
    price = models.DecimalField(default=0, max_digits=9, decimal_places=2, verbose_name='人民币价格') #初始化时候从iapprice表复制进来。因为关联查询太过麻烦。
    
    desc = models.CharField(max_length=255,verbose_name='充值产品文案描述')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')

    # class Meta:
    #     order_with_respect_to = 'price_code_price'
    #     # ordering = ['product_id']

#支付类型
class PayType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')
    
class Order(models.Model):
    STATUS_CREATED = 0
    STATUS_SUCCESS = 1
    STATUS_FAILED = 2
    STATUS_ORDER = (
        (STATUS_CREATED, '待支付'),
        (STATUS_SUCCESS, '支付成功'),
        (STATUS_FAILED, '支付失败')
    )
    
    def my_default(self):
        return {'foo': 'bar'}
    
    id = models.AutoField(primary_key=True)
    order_no = models.UUIDField(default=uuid.uuid4(), verbose_name='订单号', editable=False,db_index=True,unique=True,null=False,blank=False)
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, blank=False, null=False)

    price = models.DecimalField(default=0, max_digits=9, decimal_places=2,
                                verbose_name='人民币价格')
    
    pay_type = models.ForeignKey(PayType, on_delete=models.DO_NOTHING, blank=False, null=False)
    iap_charge = models.ForeignKey(IAPCharge, on_delete=models.DO_NOTHING, blank=True, null=True, verbose_name='内购价格')
    # iap_receipt = JSONField(default="")
    iap_receipt = models.TextField()
    iap_is_sandbox = models.BooleanField()
    
    status = models.IntegerField(choices=STATUS_ORDER, default=STATUS_CREATED,verbose_name='状态')
    desc = models.CharField(max_length=255, verbose_name='备注')
    fail_time = models.DateTimeField(null=True, blank=True, verbose_name='支付失败时间')
    finish_time = models.DateTimeField(null=True, blank=True, verbose_name='支付成功时间')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name='更新时间')


    
    # class JSONField(models.TextField):
    #     __metaclass__ = models.SubfieldBase
    #     description = "Json"
    # 
    #     def to_python(self, value):
    #         v = models.TextField.to_python(self, value)
    #         try:
    #             return json.loads(v)['v']
    #         except:
    #             pass
    #         return v
    # 
    #     def get_prep_value(self, value):
    #         return json.dumps({'v': value})