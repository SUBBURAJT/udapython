from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from .models import Users
from hashids import Hashids
import random


from rest_framework import serializers
from rest_framework.validators import UniqueValidator 
from rest_framework import serializers, viewsets, routers
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken

authkey="123456"


class login_api(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        global authkey
        try:
            res={}
            res['status'] ='error'
            res['msg'] ='API verification failed'
            if request.POST.get('authenticationkey') == authkey:
                    username = request.POST.get('username')
                    password = request.POST.get('password')
                    res['status'] ='error'
                    res['msg'] ='Some field is empty'
                    if(username != '' and password != ''):
                        res=self.login_values_check(username,password)
            return JsonResponse(res,safe=False)
        except Exception as e:
            return Response({'success':False,'code': 401,'locale': 'en',e: 'User is not Registered.','data':None})
    def login_values_check(self,username,password):
        res={}
        res['status'] ='error'
        res['msg'] ='Invalid Credentials'
        if Users.objects.filter(status=1,email=username).exists():
            data = Users.objects.values().get(status=1,email=username)
            password_check=check_password(password,data['password'])
            user = auth.authenticate(username=username, password=password,is_active=1)
            if user is not None and (password_check==True):
                hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=20)
                rand=random.randint(12345678909999999999,99999999991234567890)
                hashid = hashids.encode(rand)
                gen_rand=Users.objects.get(status=1,email=username)
                gen_rand.api_random_key=hashid
                gen_rand.save()
                data_values = Users.objects.values('id','api_random_key','email','name').get(status=1,email=username)
                res['status'] ='success'
                res['msg'] ='Successfully login'
                res['data'] =data_values
        return res

               