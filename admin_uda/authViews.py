
#auth views
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from admin_uda.forms import UserLoginForm,RecoverPasswordForm,LockScreenForm
from django.contrib import auth
from django.utils.http import urlsafe_base64_encode
from django.core.mail import BadHeaderError
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from .models import *


# Login
class LoginView(View):
    username = [];
    def get(self,request):
        if 'username' in request.session:
            return redirect('dashboard')
        else:
            greeting={}
            greeting['form'] = UserLoginForm
            return render(request,'pages/authentication/auth-login.html',greeting)

    def post(self,request):
        if(request.method == "POST"):
            username = request.POST.get('username')
            password = request.POST.get('password')
             
            if(username != '' and password != ''):
                if Users.objects.filter(status=1,email=username).exists():
                    data = Users.objects.values().get(status=1,email=username)
                    password_check=check_password(password,data['password'])
                    user = auth.authenticate(username=username, password=password,is_active=1)
                    #if(password_check==True):
                    if user is not None and (password_check==True):    
                        request.session['username'] = data['name']
                        request.session['user_email'] = username
                        request.session['user_id'] = data['id']
                        auth.login(request, user)
                        request.session.set_expiry(300)
                        LoginView.username.append(username)
                        data['success_message'] ='Successfully login'
                        return JsonResponse(data,safe=False)
                    else:
                        data={}
                        data['error_message'] ='Invalid Credentials'
                        return JsonResponse(data,safe=False)

                else:
                    data={}
                    data['error_message'] ='Invalid Credentials'
                    return JsonResponse(data,safe=False)
            else:
                data={}
                data['error_message'] ='Some field is empty'
                return JsonResponse(data,safe=False)  
        else:
            return redirect('auth-login')


# Logout
def logout(request):
    auth.logout(request)
    return render(request,'pages/authentication/auth-logout-done.html')


# Recover Password
class RecoverPasswordView(View):
    template_name = 'pages/authentication/auth-recoverpw.html'

    def get(self, request):
        if 'username' in request.session:
            return redirect('dashboard')
        else:
            return render(request, self.template_name, {'form': RecoverPasswordForm})

# Lock-Screen
class LockScreenView(LoginView,View):
    def get(self, request):
        if(self.username):
            greeting = {}
            username = self.username[0]
            greeting['heading'] = username
            greeting['form'] = LockScreenForm
            return render(request, 'pages/authentication/auth-lock-screen.html',greeting)
        else:
            return redirect("auth-login")
    def post (self, request):
        if request.method == "POST":
            password = request.POST['password']

            if(self.username):
                username = self.username[0]

                p_len =len(username)
                if(p_len<6):
                    user = auth.authenticate(username=username, password=password)
                    if user is not None:    
                        request.session['username'] = username
                        auth.login(request, user)
                        data={}
                        data['success_message'] ='Successfully unlock-screen'
                        return JsonResponse(data,safe=False)
                    else:
                        data={}
                        data['error_message'] = 'invalid creditional'
                        return JsonResponse(data,safe=False)
                else:
                    data={}
                    data['error_message'] = 'Password must be at least 6 characters'
                    return JsonResponse(data,safe=False)
            else:
                data={}
                data['session_timeout'] = 'Time-out Please Login'
                return JsonResponse(data,safe=False)        
        else:
            return redirect('auth-lock-screen')

              
               