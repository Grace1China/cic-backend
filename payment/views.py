from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import mixins
from payment.models import IAPCharge, Order, PayType
from payment.serializers import IAPChargeSerializer, IAPVerifiyRequestSerializer
from rest_framework.decorators import action

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from church.models import Course
import datetime
import pprint
import json
import httplib2
import uuid
from django.conf import settings

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

    def list(self, request):
        # if not request.user.is_authenticated:
        #     return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)
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


class OrderCreateAPIView(APIView):
    """
    创建订单
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # if not request.user.is_authenticated:
        #     return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)

        try:
            # serializer = self.get_serializer(data=data)
            # if serializer.is_valid():
            #     serializer.save(church=theChurch, is_active=True)
            data = self.request.data
            course_id = data.get('course_id', 0)
            if course_id == 0:
                return JsonResponse({'errCode': '0', 'data': {}, "msg": "参数错误"}, safe=False)

            course = Course.objects.get(pk=course_id)
            payType = PayType.objects.get(pk=1)
            isSandbox = settings.IAP_IS_SANDBOX
            
            order = Order(order_no=uuid.uuid4(), user=request.user, course=course, price=course.price,
                          iap_charge=course.iap_charge, pay_type=payType, iap_is_sandbox=isSandbox)
            order.save()
            return JsonResponse({'errCode': '0', 'data': {'order_no': order.order_no}}, safe=False)

        except Exception as e:
            return JsonResponse({'errCode': '1001', 'msg': str(e), 'data': {}}, safe=False)
        pass


# class OrderViewSet(mixins.ListModelMixin,
#                        viewsets.GenericViewSet):
#     queryset = Order.objects.all()
#     serializer_class = IAPChargeSerializer
#     permission_classes = [IsAuthenticated]
# 
#     """
#         查询订单
#     """
# 
#     # def list(self, request):
#     #     if not request.user.is_authenticated:
#     #         return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)
#     #     try:
#     #         charges = IAPCharge.objects.all().order_by('price_code__price')
#     #         slzCharges = self.get_serializer(charges, many=True)
#     #         return JsonResponse({'errCode': '0', 'data': slzCharges.data}, safe=False)
#     #     except Exception as e:
#     #         # pprint.PrettyPrinter(4).pprint(e.__traceback__)
#     #         import traceback
#     #         import sys
#     #         traceback.print_exc(file=sys.stdout)
#     #         return JsonResponse({'errCode': '1001', 'data': {}, 'msg': '没有充值产品', 'sysErrMsg': e.__str__()},
#     #                             safe=False)
#     #     pass


# 文档网址
# "https://developer.apple.com/library/archive/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html#//apple_ref/doc/uid/TP40010573-CH104-SW1"
class IapVerifyReceipt(APIView):
    """
    验证iapreceiptdata
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # if not request.user.is_authenticated:
        #     return JsonResponse({'errCode': '403', 'data': {}, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)

        try:
            receipt = request.data.get('receipt', '')
            order_no = request.data.get('order_no', '')

            pprint.PrettyPrinter(4).pprint('请求验证-order_no:' + order_no + 'receipt=xxx')

            if order_no == '' or receipt == '':
                return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)

            order = Order.objects.get(user=request.user, order_no=order_no)
            if order is None:
                return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "参数错误"}, safe=False)

            iapurl = "https://buy.itunes.apple.com/verifyReceipt"
            if settings.IAP_IS_SANDBOX:
                iapurl = "https://sandbox.itunes.apple.com/verifyReceipt"
                
            connect = httplib2.Http()
            resp, content = connect.request(iapurl,
                                            "POST",
                                            body=json.dumps({'receipt-data': receipt}),
                                            headers={"Content-type": "application/json"})

            if resp.status != 200:
                SaveWithFailed(order)
                return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "访问apple验证服务器错误"}, safe=False)

            connect.close()
            if content is None:
                SaveWithFailed(order)
                return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "验证失败,返回内容为空。"}, safe=False)

            decodedJson = json.loads(content)
            jsonString = json.dumps(decodedJson)
            
            order.iap_receipt = jsonString

            status = decodedJson.get('status')
            if status != 0:
                SaveWithFailed(order)
                return JsonResponse({'errCode': '0', 'data': {}, 'msg': "验证失败"}, safe=False)

            SaveWithSuccess(order)
            return JsonResponse({'errCode': '0', 'data': {}, 'msg': "验证成功"}, safe=False)

        except Exception as e:
            print("e:" + e.__str__())
            return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "访问apple验证服务器错误：" + e.__str__()}, safe=False)


def SaveWithFailed(order):
    order.fail_time = datetime.datetime.now()
    order.status = Order.STATUS_FAILED
    order.save()


def SaveWithSuccess(order):
    order.finish_time = datetime.datetime.now()
    order.status = Order.STATUS_SUCCESS
    order.save()
# 和上述方法一样。
# @api_view(['POST'])
# def IapVerification(request):
#     if request.method == 'POST':  # 当提交表单
# 
#     else:
#         return JsonResponse({'errCode': '1001', 'data': {}, 'msg': "请使用POST方法", 'sysErrMsg': ''}, safe=False)
