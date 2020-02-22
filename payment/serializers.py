from rest_framework import serializers
from payment.models import IAPCharge,IAPPrice

class IAPPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = IAPPrice
        fields = '__all__'
        
class IAPChargeSerializer(serializers.ModelSerializer):
    # iap_price = IAPPriceSerializer(read_only=True,many=False)
    # iap_price = serializers.StringRelatedField(many=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, coerce_to_string=None)
    class Meta:
        model = IAPCharge
        # fields = ['price_code', 'desc']
        fields = ['product_id', 'price_code', 'desc', 'price']
        # fields = '__all__'
        extra_kwargs = {
            'price': {'max_digits': 9, 'decimal_places': 2}
        }
        

class IAPVerifiyRequestSerializer(serializers.Serializer):
    receipt = serializers.CharField(required=True)

    # def create(self, validated_data):
    #     """
    #     Create and return a new `Snippet` instance, given the validated data.
    #     """
    #     return Snippet.objects.create(**validated_data)
    # 
    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `Snippet` instance, given the validated data.
    #     """
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.linenos = validated_data.get('linenos', instance.linenos)
    #     instance.language = validated_data.get('language', instance.language)
    #     instance.style = validated_data.get('style', instance.style)
    #     instance.save()
    #     return instance