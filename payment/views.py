from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import mixins
from payment.models import IAPCharge
from payment.serializers import IAPChargeSerializer

class IAPChargeViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    查找充值的价格

    客户端根据price_code计算出product_id
    
    eg: "price_code": "Tier 2", 
        "product_id": "com.churchplatform.churchplatform.iap.c.tier2",
    """
    queryset = IAPCharge.objects.all()
    serializer_class = IAPChargeSerializer
    permission_classes = [IsAuthenticated]
    # # return JsonResponse({'errCode': '0', 'data': serializer_class.data}, safe=False)
    # 
    # pass

    def list(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)
        try:
            charges = IAPCharge.objects.all().order_by('price_code__price')
            slzCharges = self.get_serializer(charges, many=True)
            return JsonResponse({'errCode': '0', 'data': slzCharges.data}, safe=False)
        except Exception as e:
            # pprint.PrettyPrinter(4).pprint(e.__traceback__)
            import traceback
            import sys
            traceback.print_exc(file=sys.stdout)
            return JsonResponse({'errCode': '1001', 'data': {}, 'msg': '没有充值产品', 'sysErrMsg': e.__str__()},
                                safe=False)
        pass