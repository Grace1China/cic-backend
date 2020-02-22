from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import mixins
from payment.models import IAPCharge
from payment.serializers import IAPChargeSerializer, IAPVerifiyRequestSerializer
from rest_framework.decorators import action

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

import json
import httplib2


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


class IapVerifyReceipt(APIView):
    """
    验证iapreceiptdata
    """
    def post(self, request, format=None):
        # if not request.user.is_authenticated:
        #     return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)

        receiptParam = request.data.get('receipt', '')

        pay_receipt = json.dumps({'receipt-data': receiptParam})

        headers = {"Content-type": "application/json"}
        # 测试地址
        connect = httplib2.Http()
        # 正式地址
        # connect = httplib2.HTTPSConnection("buy.itunes.apple.com")

        try:
            resp, content = connect.request("https://sandbox.itunes.apple.com/verifyReceipt", "POST", body=pay_receipt, headers=headers)
            
            if resp.status != 200:
                return JsonResponse (
                    {'errCode': '1001', 'data': {}, 'msg': "访问apple验证服务器错误：" + content, 'sysErrMsg': ''},
                    safe=False)

            connect.close()
            if content:
                decodedJson = json.loads(content)

                status = decodedJson.get('status')
                receipt = decodedJson.get('receipt', {})

                transaction_id = receipt.get('transaction_id', '')
                purchase_date = receipt.get('original_purchase_date', '')
                product_id = receipt.get('product_id', '')

                if status == 0:
                    return JsonResponse({'errCode': '0', 'data': decodedJson}, safe=False)

            return JsonResponse({'errCode': '1001', 'data': {}, 'msg': decodedJson, 'sysErrMsg': ''}, safe=False)
        except Exception as e:
            print("e:" + e.__str__())
            return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "访问apple验证服务器错误：" + e.__str__(), 'sysErrMsg': ''}, safe=False)





# 和上述方法一样。
# @api_view(['POST'])
# def IapVerification(request):
#     if request.method == 'POST':  # 当提交表单
# 
#     else:
#         return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "请使用POST方法", 'sysErrMsg': ''}, safe=False)