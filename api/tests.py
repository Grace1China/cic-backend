from django.test import TestCase 
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.response import Response
import json

from rest_framework.test import force_authenticate
from .views import *
import logging

# Create your tests here.
from rest_framework.test import APIRequestFactory,APIClient
from .models import *


# Create your tests here.
class ApiTestCase(APITestCase):
    profile_list_url='/rapi/all-profiles'
    def setUp(self):
        # create a new user making a post request to djoser endpoint
        self.user=self.client.post('/auth/users/',data={'username':'mario','password':'i-keep-jumping'})
        # obtain a json web token for the newly created user
        response=self.client.post('/auth/jwt/create/',data={'username':'mario','password':'i-keep-jumping'})
        print(response.data)
        self.token=response.data['access']
        print('---------------------------token:access------------------------')
        print(self.token)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer '+self.token)

    def test_users(self):
        # response=self.client.post('/auth/users/',data={'username':'mario','password':'i-keep-jumping'})
        # jsonrt = json.loads(response.content)
        # print('----------mario----------')
        # print(jsonrt)

        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        print('----------profiles-------------')
        jsonrt = json.loads(response.content)
        print(jsonrt)



    # retrieve a list of all user profiles while the request user is authenticated
    def test_userprofile_list_authenticated(self):
        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        print(response.content)


    # retrieve a list of all user profiles while the request user is unauthenticated
    def test_userprofile_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    # check to retrieve the profile details of the authenticated user
    def test_userprofile_detail_retrieve(self):
        response=self.client.get('/rapi/accounts/profile/1')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        print(response.content)



    # populate the user profile that was automatically created using the signals
    def test_userprofile_profile(self):
        response=self.client.get(self.profile_list_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        jsonrt = json.loads(response.content)
        profile_data={'description':'I am a very famous game character','location':'nintendo world','Role':1}
        response=self.client.put('/rapi/accounts/profile/'+str(jsonrt[0]['id']),data=profile_data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        print(response.content)

    def test_sermon(self):
        pass


class ViewSetTest(TestCase):
    def test_view_set(self):
        # response = APIClient().get(reverse('cat-detail', args=(cat.pk,)))
        # self.assertEqual(response.status_code, 200)   


        request = APIRequestFactory().get("")
        # cat_detail = CatViewSet.as_view({'get': 'retrieve'})
        # cat = Cat.objects.create(name="bob")
        # response = cat_detail(request, pk=cat.pk)
        # self.assertEqual(response.status_code, 200)

        factory = APIRequestFactory()
        view = EweeklyViewSet.as_view({'get':'GetL3Eweekly'})
        # request = factory.get('http://test.l3.bicf.org/rapi/eweekly/l3'))
        # request = factory.get(reverse(view))
        response = view(request)
        pprint.PrettyPrinter(6).pprint(response.content)
        pprint.PrettyPrinter(6).pprint(eval(response.content))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(eval(response.content)['errCode'],'0')

        


    
