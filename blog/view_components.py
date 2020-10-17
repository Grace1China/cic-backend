
# from django.shortcuts import render

# from django.http import HttpResponse
# from django.template import loader
# from church.alioss_storage_backends_v3 import AliyunMediaStorage
# # Create your views here.
# import logging
# theLogger = logging.getLogger('church.all')
# from rest_framework import serializers
# from churchs.models.vpage import VPage
# from churchs.models.vpage import VComponents, VParts


# from api.serializers import MediaSerializer4ListAPI
# from church.models import Church

# from rest_framework_simplejwt.state import token_backend
# from users.models import CustomUser

# from django.conf import settings
# class VPartsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VParts
#         fields = '__all__'

# class VComponentsSerializer(serializers.ModelSerializer):
#     vparts = VPartsSerializer(many=True, read_only=True)
#     class Meta:
#         model = VComponents
#         fields = ('id','title','church','create_by','create_time','update_time','control','ContentColumn','Media','content','vparts',)


# class vpageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = VPage
#         fields = '__all__'

# def vcomp(request,pk=0):
#     try:
#         data = request.GET
#         id = data.get('componentid',0)
#         vcomp = VComponents.objects.get(id=id)
#         compsz = VComponentsSerializer(vcomp)
#         theLogger.info('-------------vcomp--------')
#         theLogger.info(compsz.data)
#         template = loader.get_template('blog/vcomponents.html')
#         context = {
#             'vcomp': compsz.data,
#         }
#         return HttpResponse(template.render(context, request))
#     except Exception as e:
#             theLogger.exception("there is an exception",exc_info=True,stack_info=True)
#             raise e