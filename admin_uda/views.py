import json
#from typing import ParamSpec
from django.shortcuts import render, redirect
from django.http import JsonResponse
from admin_uda.setting.membership_upload import membership
from admin_uda.setting.hygienist_upload import hygienist
from admin_uda.setting.convention_workshop import convention_workshops
from admin_uda.setting.message_center import message_centers
from admin_uda.setting.user_management import user_managements
from admin_uda.setting.qr_search import qr_search_list
from django.core.mail import send_mail
from django.conf import settings
from django.core import serializers

from uda.settings import DEFAULT_FROM_EMAIL
from .models import *
from django.contrib import messages
import datetime
import csv
from django.http import HttpResponse, response
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import Q
import random
import os
from django.conf import settings
from django.http import HttpResponse, Http404
import array as arr
from django.contrib.auth.models import User

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from os import path
from django.utils.html import strip_tags
from django.contrib.staticfiles import finders

succ_message = "Registered Successfully"

def link_callback(uri, rel):
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    sUrl = settings.STATIC_URL        # Typically /static/
                    sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    mUrl = settings.MEDIA_URL         # Typically /media/
                    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(mUrl):
                            path = os.path.join(mRoot, uri.replace(mUrl, ""))
                    elif uri.startswith(sUrl):
                            path = os.path.join(sRoot, uri.replace(sUrl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise Exception(
                            'media URI must start with %s or %s' % (sUrl, mUrl)
                    )
            return path
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
def myview(request):
    #Retrieve data or whatever you need
    # # return render_to_pdf(
    #         'mail_attachment.html',
    #         {
    #             'pagesize':'A4',
    #             'mylist': '123',
    #         }
    #     )  
    return HttpResponse(succ_message)  

def send_sms(request):
    txt_res=Send_Sms.Send(msg_txt='Test Message for text',to_number='9962220345')
    return HttpResponse(txt_res, 200)
def send_mail(request):
    body = """
    <html><head><style></style></head><body><table><thead><th><td>Name</td><td>Age</td></th></thead><tbody><tr><td>Raja Kumari</td><td>25</td></tr><tr><td>Siva</td><td>25</td></tr></tbody></table></body></html>
    """
    plain_message = strip_tags(body)
    txt_res=Send_Mail.Send(subject='User add',body=plain_message,to_mail='rajiveorchids@gmail.com',html_message=body)
    return HttpResponse(txt_res, 200)

# Create your views here.
@login_required()
def dashboard(request):
    greeting = {}
    greeting['title'] = "Dashboard"
    greeting['pageview'] = "UDA"  
    if 'username' in request.session:
        return render(request, 'menu/index.html',greeting)
    else:
        return redirect('auth-login')
    

def membership_upload_ui(request):
    return render(request,'membership_upload_ui.html',{})

def hygienist_upload_ui(request):
    return render(request,'membership_upload_ui.html',{})

def user_management_ui(request):
    return render(request,'user_management_ui.html',{})

def convention_workshop_ui(request):
    return render(request,'convention_workshop_ui.html',{})

def spring_transaction_ui(request):
    return render(request,'spring_transaction_ui.html',{})

def message_center_ui(request):
    return render(request,'message_center_ui.html',{})

@login_required()
def membership_upload(request):
    greeting = {}
    datas=membership.list_membership()
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Membership Upload'
    greeting['data']=datas
    if request.is_ajax and request.method=='POST':
        mem=membership.add_membership(request.FILES['file'])
        msg=''
        error=''
        if mem['err']:
            error=mem['err']

        if mem['Added_id']:
            t_r=str(mem['Added_id'])
            msg+='Total New records : '+ t_r + ' added successfully'+'<br>'

        if mem['exists_id']:
            if(len(mem['exists_id'])>0):
                msg+='Already exists values are updated'+'<br>'

        return JsonResponse({"valid":True,"err":error,"msg":msg,"al":mem['exists_id']}, status = 200)
    
    return render(request,'membership_upload.html',greeting)

@login_required()
def hygienist_upload(request):
    hyg_obj = hygienist()
    greeting = {}
    datas=hyg_obj.list_hygienist()
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Hygienist Upload'
    greeting['data']=datas
    if request.is_ajax and request.method=='POST':
        mem=hyg_obj.add_hygienist(request.FILES['file'])
        msg=''
        error=''
        if mem['err']:
            error=mem['err']

        if mem['invalid_ada']:
            error=' , '.join(mem['invalid_ada']) + ' Invalid ID'

        if mem['Added_id']:
            t_r=str(mem['Added_id'])
            msg+='Total New records : '+ t_r + ' added successfully'+'<br>'

        if mem['exists_id']:
            if(len(mem['exists_id'])>0):
                msg+='Already exists values are updated'+'<br>'

        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)
    
    return render(request,'hygienist_upload.html',greeting)

@login_required()
def message_center(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Message Center'
    return render(request,'message_center.html',greeting)

@login_required()    
def convention_workshop(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Workshop'    
    return render(request,'convention_workshop.html',greeting)

@login_required()
def convention_workshop_form(request):
    con_obj = convention_workshops()
    module=request.POST.get('module')
    if module and module=='form_submit':
        err=''
        msg=''
        res=con_obj.save_convention_workshop(request)
        if res['error']:
            err=res['error']

        if res['msg']:
            msg=res['msg']

        return JsonResponse({"valid":True,"err":err,"msg":msg}, status = 200)
    elif module and module=='list':
        result=con_obj.list_convention_workshop(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=con_obj.delete_convention_workshop(request)
        return JsonResponse(result, status = 200)
    elif module and module=='getdatas':
        result=con_obj.get_convention_workshop(request)
        datas = serializers.serialize("json", result)        
        return JsonResponse({"data":datas}, status = 200)
    elif module and module=='block':
        result=con_obj.block_convention_workshop(request)
        return JsonResponse(result, status = 200)

@login_required()
def message_center_operations(request):
    module=request.POST.get('module')
    if module and module=='list':
        result=message_centers.list_message_center(request)
        return JsonResponse(result, status = 200)
    if module and module=='typeofmem':
        result=message_centers.type_of_members(request)
        return JsonResponse({"option":result}, status = 200)
    if module and module=='memnames':
        result=message_centers.member_names(request)
        return JsonResponse({"option":result}, status = 200)
    if module and module=='add_message':
        err=''
        msg=''
        result=message_centers.add_messages(request)
        if result['error']:
            err=result['error']
        if result['msg']:
            msg=result['msg']
        return JsonResponse({"valid":True,"err":err,"msg":msg}, status = 200)
    elif module and module=='delete':
        result=message_centers.delete_message(request)
        return JsonResponse(result, status = 200)
    if module and module=='view_msg':
        result=message_centers.view_msgs(request)
        return JsonResponse(result, status = 200)

    
def convention_transaction_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transactions'
    return render(request,'convention_transaction_ui.html',greeting)

def fall_registration_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Fall Registration'
    return render(request,'fall_registration_ui.html',greeting)
    
def spring_registration_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Spring Registration'
    return render(request,'spring_registration_ui.html',greeting)
        
def fall_transaction_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Fall Transactions'
    return render(request,'fall_transaction_ui.html',greeting)

def edit_profile_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Edit Profile'
    return render(request,'edit_profile_ui.html',greeting)
    
def exhibitor_registration_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Registration'
    return render(request,'exhibitor_registration_ui.html',greeting)

def vendor_detail_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Details'
    return render(request,'vendor_detail_ui.html',greeting)
                
def vendor_edit_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Edit'
    return render(request,'vendor_edit_ui.html',greeting)
        
def convention_registration_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Registration'
    return render(request,'convention_registration_ui.html',greeting)
            
def forgot_password_template_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Forgot Password'
    return render(request,'forgot_password_template_ui.html',greeting)
                
def convention_edit_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Edit'
    return render(request,'convention_edit_ui.html',greeting)
                    
def convention_detail_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Detail'
    return render(request,'convention_detail_ui.html',greeting)
                        
def vendor_detail_print_ui(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Registration Details'
    return render(request,'vendor_detail_print_ui.html',greeting)
                            
def convention_id_card_print_bulk_ui(request):
    greeting = {}
    greeting['pageview'] = ""
    greeting['title'] = ''
    return render(request,'convention_id_card_print_bulk_ui.html',greeting)

def convention_id_card_print_ui(request):
    greeting = {}
    greeting['pageview'] = ""
    greeting['title'] = ''
    return render(request,'convention_id_card_print_ui.html',greeting)
    
def mail_attachment_ui(request):
    greeting = {}
    greeting['pageview'] = ""
    greeting['title'] = ''
    return render(request,'mail_attachment_ui.html',greeting)
        
def qr_search_ui(request):
    greeting = {}
    greeting['pageview'] = "Settings"
    greeting['title'] = 'Scan QR Code'
    return render(request,'qr_search_ui.html',greeting)

def user_email_check(request):
    if request.is_ajax and request.method=='POST':
        req_email = request.POST.get('email')
        req_id = request.POST.get('id')
        if req_id!='' and Users.objects.filter(~Q(id=req_id), email=req_email,status=1).exists():
            return JsonResponse({"valid":True,"err":1,"msg":"Email Already Exists"}, status = 200)
        elif req_id=='' and Users.objects.filter( email=req_email,status=1).exists():
            return JsonResponse({"valid":True,"err":1,"msg":"Email Already Exists"}, status = 200)
        else:
            return JsonResponse({"valid":True,"err":0,"msg":""}, status = 200)
        
@login_required()
def user_management_operations(request):
    user_obj = user_managements()
    module=request.POST.get('module')
    if module and module=='list_user_management':
        result=user_obj.list_user_management(request)
        return JsonResponse(result, status = 200)
    if module and module=='add_user_management':
        err=''
        msg=''
        result=user_obj.add_user_management(request)
        if result['error']:
            err=result['error']
        if result['msg']:
            msg=result['msg']
        return JsonResponse({"valid":True,"err":err,"msg":msg}, status = 200)
    

@login_required()
def user_management(request):
    greeting = {}
    greeting['title'] = 'User Management'
    greeting['pageview'] = "Dashboard"

    return render(request,'user_management.html',greeting )

@login_required()
def delete_user_management(request,id):
     id_session=request.session['user_id']
     print(id_session)
     if request.is_ajax and request.method=='POST':
        error=''
        user = Users.objects.get(id=id)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        user.status = 0
        user.deleted_by = id_session
        user.deleted_at = datetime.datetime.now()
        user.deleted_ip = ip
        user.save()
        #Udate auth_user table
        auth_id=user.auth_user_id
        auth_user = User.objects.get(id=auth_id)
        auth_user.is_active=0
        msg = "User Deleted Successfully"
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

def get_users(request):
    if request.is_ajax and request.method=='GET':
        id= request.GET.get('id')
        users = Users.objects.filter(id=id)
        user = serializers.serialize("json", users)        
        return JsonResponse({"valid":True,"data":user}, status = 200)

@login_required()
def delete_profile_img(request):
    id=request.session['user_id']
    Users.objects.filter(id=id).update(profile_img=None)
    return JsonResponse({"valid":True,"msg":"Profile Image deleted."}, status = 200)

@login_required()
def edit_profile(request):
    id=request.session['user_id']
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Edit Profile'
   
    # print(data.auth_user_id)

    if(request.method == "POST"):
        c = False
        file_action = False
        name = request.POST.get('name')
        email = request.POST.get('email')
        oldPassword = request.POST.get('old_pass')
        newPassword = request.POST.get('new_pass')

        data     = Users.objects.values().get(id=id)
        password_check = check_password(oldPassword,data['password'])
        
        if len(request.FILES) != 0:
            image = request.FILES['changepro']
            file_action = True
        else:
           image = data['profile_img']

        if(email!=""):
            if Users.objects.filter(~Q(id=id),email=email).exists():
                messages.error(request, 'Email already exist')
            elif(oldPassword=='' and newPassword != ""):
                messages.error(request, 'Old password required to update your new password')
            elif(oldPassword!="" and newPassword==''):
                messages.error(request, 'New password required to update')
            elif(oldPassword != "" and newPassword != "" ):
                if(password_check==True):
                    c = True 
                else:
                    messages.error(request, "Invalid Old password ") 
            else:
                Users.objects.filter(id=id).update(
                    name=name,
                    email=email,
                    profile_img = image,
                  
                )
                if(file_action):
                    messages.success(request, "File & General details updated successfully")
                else:
                    messages.success(request, "General details updated successfully")


        if(c):
            Users.objects.filter(id=id).update(
                name=name,
                email=email,
                profile_img = image,
                password =make_password(newPassword),
                reset_pass =make_password(newPassword) ,
            )
            data     = Users.objects.get(id=id)
            auth_user = User.objects.get(id=data.auth_user_id)
            # print(auth_user)
            auth_user.password   = make_password(newPassword)
            auth_user.save()  
            if(file_action):
                messages.success(request, "File uploaded. And, details updated successfully")
            else:
                messages.success(request, "Your details updated successfully")

    datas = Users.objects.get(id=id)
    greeting['datas'] = datas
    
    return render(request,'edit_profile.html',greeting)

@login_required()
def qr_search(request):
    if request.is_ajax and request.method=='POST':
        result=qr_search_list.list_registered_name(request)
        return JsonResponse(result, status = 200)
    greeting = {}
    greeting['pageview'] = "Settings"
    greeting['title'] = 'Scan QR Code'
    return render(request,'qr_search.html',greeting)

def qrcode_search(request,ids,types):
    if request.is_ajax and request.method=='GET':
        result=qr_search_list.list_registered_name_qr(request,ids,types)
        return JsonResponse(result, status = 200)