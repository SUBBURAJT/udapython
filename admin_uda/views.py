import json
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
from .models import Send_Sms,Send_Mail,Users,default_functions
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
default_obj = default_functions()

def link_callback(uri, rel):
    try:
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
                    surl = settings.STATIC_URL        # Typically /static/
                    sroot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    murl = settings.MEDIA_URL         # Typically /media/
                    mroot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(murl):
                            path = os.path.join(mroot, uri.replace(murl, ""))
                    elif uri.startswith(surl):
                            path = os.path.join(sroot, uri.replace(surl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise ValueError(
                            'media URI must start with %s or %s' % (surl, murl)
                    )
            return path
    except ValueError as err:
        return err
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
    obmem=membership()
    datas=obmem.list_membership()
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Membership Upload'
    greeting['data']=datas
    if request.is_ajax and request.method=='POST':
        mem=obmem.add_membership(request.FILES['file'])
        msg=''
        error=''
        if mem['err']:
            error=mem['err']
        if mem['invalid_ada']:
            error=' , '.join(mem['invalid_ada']) + ' Invalid ID'
        if mem['Added_id']:
            t_r=str(mem['Added_id'])
            msg+='Total New records : '+ t_r + ' added successfully'+'<br>'
        if mem['exists_id'] and len(mem['exists_id'])>0:
            msg+='Already exists values are updated'+'<br>'
        if mem['Added_id']==0 and len(mem['exists_id'])==0 and mem['err']=='':
            error='Please Upload a Correct row and columns'
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
        if mem['exists_id'] and len(mem['exists_id'])>0:
            msg+='Already exists values are updated'+'<br>'
        if mem['Added_id']==0 and len(mem['exists_id'])==0 and mem['err']=='':
            error='Please Upload a Correct row and columns'

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

def ger_err_msg(result):
    err=''
    msg=''
    if result['error']:
        err=result['error']
    if result['msg']:
        msg=result['msg']
    return {"msg":msg,"err":err}

@login_required()
def convention_workshop_form(request):
    con_obj = convention_workshops()
    module=request.POST.get('module')
    if module and module=='form_submit':
        res=con_obj.save_convention_workshop(request)
        err_msg=ger_err_msg(res)
        return JsonResponse({"valid":True,"err":err_msg['err'],"msg":err_msg['msg']}, status = 200)
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
    obmessage=message_centers()
    module=request.POST.get('module')
    if module=='list':
        result=obmessage.list_message_center(request)
        return JsonResponse(result, status = 200)
    elif module=='typeofmem':
        result=obmessage.type_of_members(request)
        return JsonResponse({"option":result}, status = 200)
    elif module=='memnames':
        result=obmessage.member_names(request)
        return JsonResponse({"option":result}, status = 200)
    if module and module=='add_message':
        result=obmessage.add_messages(request)
        err_msg=ger_err_msg(result)
        return JsonResponse({"valid":True,"err":err_msg['err'],"msg":err_msg['msg']}, status = 200)
    elif module and module=='delete':
        result=obmessage.delete_message(request)
        return JsonResponse(result, status = 200)
    elif module=='view_msg':
        result=obmessage.view_msgs(request)
        return JsonResponse(result, status = 200)
    else:
        result=[]
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
        uid= request.GET.get('id')
        users = Users.objects.filter(id=uid)
        user = serializers.serialize("json", users)        
        return JsonResponse({"valid":True,"data":user}, status = 200)

@login_required()
def delete_profile_img(request):
    uid=request.session['user_id']
    Users.objects.filter(id=uid).update(profile_img=None)
    return JsonResponse({"valid":True,"msg":"Profile Image deleted."}, status = 200)

@login_required()
def edit_profile(request):
    uid=request.session['user_id']
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Edit Profile'
   
    if(request.method == "POST"):
        objuser=user_managements()
        c = False
        file_action = False
        err_msg = ''
        succ_msg = ''
        name = request.POST.get('name')
        email = request.POST.get('email')
        old_password = request.POST.get('old_pass')
        new_password = request.POST.get('new_pass')

        data     = Users.objects.values().get(id=uid)
        password_check = check_password(old_password,data['password'])
        image = data['profile_img']
        if len(request.FILES) != 0:
            image = request.FILES['changepro']
            file_action = True

        if(email!=""):
            params={
                'email' : email,
                'oldPassword' : old_password,
                'newPassword' : new_password,
                'name' : name,
                'image' : image,
                'file_action' : file_action,
                'password_check' : password_check
            }
            validation_res = objuser.edit_pro_validation(params)
            err_msg = default_obj.check_key_val('errmsg',validation_res)
            succ_msg = default_obj.check_key_val('succmsg',validation_res)
            messages.error(request, err_msg)
            messages.success(request, succ_msg)
            c = validation_res['c']

        if(c):
            Users.objects.filter(id=uid).update(
                name=name,
                email=email,
                profile_img = image,
                password =make_password(new_password),
                reset_pass =make_password(new_password) ,
            )
            data     = Users.objects.get(id=uid)
            auth_user = User.objects.get(id=data.auth_user_id)
            auth_user.password   = make_password(new_password)
            auth_user.save()  
            if(file_action):
                messages.success(request, "File uploaded. And, details updated successfully")
            else:
                messages.success(request, "Your details updated successfully")

    datas = Users.objects.get(id=uid)
    greeting['datas'] = datas
    
    return render(request,'edit_profile.html',greeting)

@login_required()
def qr_search(request):
    if request.is_ajax and request.method=='POST':
        objqrsearch=qr_search_list()
        result=objqrsearch.list_registered_name(request)
        return JsonResponse(result, status = 200)
    greeting = {}
    greeting['pageview'] = "Settings"
    greeting['title'] = 'Scan QR Code'
    return render(request,'qr_search.html',greeting)

def qrcode_search(request,ids,types):
    if request.is_ajax and request.method=='GET':
        objqrsearchcode=qr_search_list()
        result=objqrsearchcode.list_registered_name_qr(request,ids,types)
        return JsonResponse(result, status = 200)

def reset_pass(request):
    module=request.POST.get('module')
    objuser=user_managements()
    if module and module=='send_mail':
        result=objuser.reset_pass_mail(request)
        return JsonResponse(result, status = 200)
    if module and module=='reset_password':
        result=objuser.reset_password_submit(request)
        if result['res']:
            messages.success(request, "Your password has been reset successfully!")
            return redirect('auth-login')
        else:
            messages.error(request, "Password reset failed!")
            return redirect('auth-login')