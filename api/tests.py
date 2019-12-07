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
class userProfileTestCase(APITestCase):
    profile_list_url='/rapi/accounts/all-profiles'
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
