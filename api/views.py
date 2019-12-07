from rest_framework.generics import (ListCreateAPIView,RetrieveUpdateDestroyAPIView,)
from rest_framework.permissions import IsAuthenticated
from .models import userProfile
from .permissions import IsOwnerProfileOrReadOnly
from .serializers import userProfileSerializer
from churchs.models import Sermon
from churchs.serializers import SermonSerializer
import boto3
from botocore.exceptions import ClientError
import logging
from rest_framework import generics
from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse



# Create your views here.

class UserProfileListCreateView(ListCreateAPIView):
    queryset=userProfile.objects.all()
    serializer_class=userProfileSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        user=self.request.user
        serializer.save(user=user)


class userProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset=userProfile.objects.all()
    serializer_class=userProfileSerializer
    permission_classes=[IsOwnerProfileOrReadOnly,IsAuthenticated]


class SermonDetailView(APIView):
    '''
    retrieve and update sermon
    '''
    def get_object(self, pk):
        try:
            return Sermon.objects.get(pk=pk)
        except Sermon.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        sermon = None
        print('----------------->'+str(pk))
        if pk == None or int(pk) <= 0:
            #选一个最近的sermon
            sermonQry = Sermon.objects.all()
            sermon = sermonQry.reverse()[:1]
            if len(sermon) != 1:
                return JsonResponse({'errCode': '1001', msg:'database has no record.','data':None}, safe=False)
            else:
                sermon = sermon[0]

            print('---------pk <=0------------')
            print(sermon)
            serializer = SermonSerializer(sermon)
        else: 
            sermon = self.get_object(pk)
            print('---------pk >0------------')
            serializer = SermonSerializer(sermon)
            
        return JsonResponse({'errCode': '0', 'data': serializer.data}, safe=False)

    # def put(self, request, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = SnippetSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 1、首先要实现一个能查找主日信息的api可以返回主日的所有信息，现在只要实现当前主日信息 这个信息里面有id title cover pdf worship sermon giving等信息
# 2、在这个信息中，应该可以自定义presignedurl的过期时间。这些都已经是presignedurl了。
