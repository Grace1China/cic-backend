from rest_framework import serializers
from payment.models import IAPCharge,IAPPrice

# class IAPPriceSerializer(serializers.ModelSerializer):
# 
#     class Meta:
#         model = IAPPrice
#         fields = '__all__'
        
class IAPChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IAPCharge
        fields = ['price_code', 'desc']
        # fields = ['product_id', 'price_code', 'desc']
        # fields = '__all__'