from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.shortcuts import render
from .models import Users
from hashids import Hashids
import random

authkey="123456"

# Login
def login_values_check(username,password):
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
def login_check(request):
    global authkey
    res={}
    if request.is_ajax and request.method=='POST':
        res['status'] ='error'
        res['msg'] ='API verification failed'
        if request.POST.get('authenticationkey') == authkey:
            username = request.POST.get('username')
            password = request.POST.get('password')
            res['status'] ='error'
            res['msg'] ='Some field is empty'
            if(username != '' and password != ''):
                res=login_values_check(username,password)
        return JsonResponse(res,safe=False)
    else:
        res['status'] ='error'
        res['msg'] ='Invalid type'
        return JsonResponse(res,safe=False)

               