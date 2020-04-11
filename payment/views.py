from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import mixins
from payment.models import IAPCharge, Order, PayType,Users_Courses
from payment.serializers import IAPChargeSerializer, IAPVerifiyRequestSerializer
from rest_framework.decorators import action

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from church.models import Course
from django.utils import timezone
import datetime
import pprint
import json
import httplib2
import uuid
from django.conf import settings
from django.db import transaction
import logging

theLogger = logging.getLogger('church.all')

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
        try:
            charges = IAPCharge.objects.all().order_by('price_code__price')
            slzCharges = self.get_serializer(charges, many=True)
            return JsonResponse({'errCode': '0', 'data': slzCharges.data}, safe=False)
        except Exception as e:
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有充值产品', 'sysErrMsg': e.__str__()},
                                safe=False)
        pass


class OrderCreateAPIView(APIView):
    """
    创建订单
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            # serializer = self.get_serializer(data=data)
            # if serializer.is_valid():
            #     serializer.save(church=theChurch, is_active=True)
            data = self.request.data
            course_id = data.get('course_id', 0)
            if course_id == 0:
                return JsonResponse({'errCode': '0', 'data': None, "msg": "参数错误"}, safe=False)

            course = Course.objects.get(pk=course_id)
            payType = PayType.objects.get(pk=PayType.IAP)
            isSandbox = settings.IAP_IS_SANDBOX

            order = Order(order_no=uuid.uuid4(), user=request.user, course=course, price=course.price,
                          price_usd=course.price_usd,
                          iap_charge=course.iap_charge, pay_type=payType, is_sandbox=isSandbox)
            order.save()
            return JsonResponse({'errCode': '0', 'data': {'order_no': order.order_no}}, safe=False)

        except Exception as e:
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse({'errCode': '1001', 'msg': str(e), 'data': None}, safe=False)
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
#     #         return JsonResponse({'errCode': '403', 'data': None, 'msg': '您没有执行该操作的权限。', 'sysErrMsg': ''}, safe=False)
#     #     try:
#     #         charges = IAPCharge.objects.all().order_by('price_code__price')
#     #         slzCharges = self.get_serializer(charges, many=True)
#     #         return JsonResponse({'errCode': '0', 'data': slzCharges.data}, safe=False)
#     #     except Exception as e:
#     #         # pprint.PrettyPrinter(4).pprint(e.__traceback__)
#     #         import traceback
#     #         import sys
#     #         traceback.print_exc(file=sys.stdout)
#     #         return JsonResponse({'errCode': '1001', 'data': None, 'msg': '没有充值产品', 'sysErrMsg': e.__str__()},
#     #                             safe=False)
#     #     pass


# 文档网址
# "https://developer.apple.com/library/archive/releasenotes/General/ValidateAppStoreReceipt/Chapters/ValidateRemotely.html#//apple_ref/doc/uid/TP40010573-CH104-SW1"
# @transaction.atomic
class IapVerifyReceipt(APIView):
    """
    验证iapreceiptdata
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            receipt = request.data.get('receipt', '')
            order_no = request.data.get('order_no', '')

            pprint.PrettyPrinter(4).pprint('请求验证-order_no:' + order_no + 'receipt=xxx')

            if order_no == '' or receipt == '':
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)

            order = Order.objects.get(user=request.user, order_no=order_no)
            if order is None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误"}, safe=False)

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
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "访问apple验证服务器错误"}, safe=False)

            connect.close()
            if content is None:
                SaveWithFailed(order)
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "验证失败,返回内容为空。"}, safe=False)

            decodedJson = json.loads(content)
            jsonString = json.dumps(decodedJson)

            order.iap_receipt = jsonString

            status = decodedJson.get('status')
            if status != 0:
                SaveWithFailed(order)
                return JsonResponse({'errCode': '0', 'data': None, 'msg': "验证失败"}, safe=False)

            course = Course.objects.get(pk=order.course.id)
            usercourse = Users_Courses(user=request.user, course=course)
            with transaction.atomic():
                SaveWithSuccess(order)
                usercourse.save()
                course.sales_num += 1
                course.save()
            return JsonResponse({'errCode': '0', 'data': {"order_no":order.order_no,"course_id":order.course.id}, 'msg': "验证成功"}, safe=False)

        except Exception as e:
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            SaveWithFailed(order)
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "访问apple验证服务器错误：" + e.__str__()}, safe=False)


def SaveWithFailed(order):
    order.fail_time = datetime.datetime.utcnow()
    order.status = Order.STATUS_FAILED
    order.save()


def SaveWithSuccess(order):
    order.finish_time = datetime.datetime.utcnow()
    order.status = Order.STATUS_SUCCESS
    order.save()


# 和上述方法一样。
# @api_view(['POST'])
# def IapVerification(request):
#     if request.method == 'POST':  # 当提交表单
# 
#     else:
#         return JsonResponse({'errCode': '1001', 'data': None, 'msg': "请使用POST方法", 'sysErrMsg': ''}, safe=False)


# --------paypal---------
import braintree


class ClientToken(APIView):
    """
    paypal请求client token
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            course_id = request.data.get('course_id', 0)
            if course_id == 0:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)
            course = Course.objects.get(pk=course_id)
            if course is None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)

            payType = PayType.objects.get(pk=PayType.PAYPAL)
            isSandbox = settings.PAYPAL_IS_SANEBOX
            order = Order(order_no=uuid.uuid4(), user=request.user, course=course, price=course.price,
                          price_usd=course.price_usd, pay_type=payType, is_sandbox=isSandbox)
            order.save()

            gateway = pp_gateway()
            clientToken = gateway.client_token.generate()

            return JsonResponse(
                {'errCode': '0', 'data': {"client_token": clientToken, "order_no": order.order_no}, 'msg': "成功"},
                safe=False)
        except Exception as e:
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "请求client token失败：" + e.__str__()}, safe=False)


# @transaction.atomic
class PaymentMethodNonce(APIView):
    """
    paypal 支付
    """

    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        try:
            order_no = request.data.get('order_no', 0)
            nonce_from_the_client = request.data.get('payment_method_nonce', '')
            device_data_from_the_client = request.data.get('device_data_from_the_client', '')
            if order_no == '' or nonce_from_the_client == '' or device_data_from_the_client == '':
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误", 'sysErrMsg': ''}, safe=False)
            order = Order.objects.get(user=request.user, order_no=order_no)
            if order is None:
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "参数错误"}, safe=False)

            gateway = pp_gateway()
            result = gateway.transaction.sale({
                "amount": order.price_usd,
                "payment_method_nonce": nonce_from_the_client,
                "device_data": device_data_from_the_client,
                "options": {
                    "submit_for_settlement": True
                }
            })
            order.pp_transcation_id = result.transaction.id

            theLogger.info(result.transaction.status)
            if result.is_success:
                theLogger.info("success!: " + result.transaction.id)
                course = Course.objects.get(pk=order.course.id)
                usercourse = Users_Courses(user=request.user, course=course)
                
                with transaction.atomic():
                    SaveWithSuccess(order)
                    usercourse.save()
                    course.sales_num += 1
                    course.save()
                return JsonResponse({'errCode': '0', 'data': {"order_no":order.order_no,"course_id":order.course.id}, 'msg': "支付成功"}, safe=False)

            elif result.transaction:
                theLogger.info("Error processing transaction:")
                theLogger.info("  code: " + result.transaction.processor_response_code)
                theLogger.info("  text: " + result.transaction.processor_response_text)

                SaveWithFailed(order)
                return JsonResponse({'errCode': '1001', 'data': None,
                                     'msg': "支付失败:" + result.transaction.processor_response_code + "," + result.transaction.processor_response_text},
                                    safe=False)
            else:
                msg = ""
                for error in result.errors.deep_errors:
                    theLogger.info("attribute: " + error.attribute)
                    theLogger.info("  code: " + error.code)
                    theLogger.info("  message: " + error.message)
                    msg += "," + error.code + ":" + error.message
                SaveWithFailed(order)
                return JsonResponse({'errCode': '1001', 'data': None, 'msg': "支付失败" + msg}, safe=False)
        except Exception as e:
            theLogger.exception('There is and exceptin', exc_info=True, stack_info=True)
            SaveWithFailed(order)
            return JsonResponse({'errCode': '1001', 'data': None, 'msg': "支付失败：" + e.__str__()}, safe=False)


def pp_gateway():
    isSandbox = settings.PAYPAL_IS_SANEBOX
    if isSandbox:
        congfiguration = braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id="b9mnrfpx5f9b73tj",
            public_key="2ds4m93c5rfmbww5",
            private_key="39d099e6e9fa98ecc83a7537370717d2"
        )
    else: #TODO: 正式环境配置
        congfiguration = braintree.Configuration(
            braintree.Environment.Production,
            merchant_id="b9mnrfpx5f9b73tj",
            public_key="2ds4m93c5rfmbww5",
            private_key="39d099e6e9fa98ecc83a7537370717d2"
        )

    gateway = braintree.BraintreeGateway(congfiguration)
    return gateway
