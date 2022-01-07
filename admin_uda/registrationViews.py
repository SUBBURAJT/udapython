import os
from django.shortcuts import render,redirect
from admin_uda.models import Handon_form,Ada_membership
from admin_uda.registrations.fallRegistration import FallRegistration
from admin_uda.registrations.springRegistration import SpringRegistration
from admin_uda.registrations.conventionRegistration import ConventionRegistration
from admin_uda.registrations.vendorRegistration import VendorRegistration
import datetime as dt
import json
from django.template.defaulttags import register
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Value
from django.db.models.functions import Lower, Replace, Concat
from admin_uda.registrations.registration import Registration
from hashids import Hashids
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from os import path
from django.contrib.staticfiles import finders
from django.conf import settings

reg_succ_msg = "Registered Successfully"
update_succ_msg = "Updated Successfully"
reg_err_msg = "Someting went to wrong! Please Try Again"
vendor_obj = VendorRegistration()
con_obj = ConventionRegistration()
sp_obj = SpringRegistration()

@register.filter
def get_range(value):
    return range(value)
@register.filter
def get_int(value):
    return int(value)

@login_required()
def fall_registration(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Fall Registration' 
    fall_obj = FallRegistration()
    # get convention type
    today = dt.date.today() 
    greeting['convention'] = fall_obj.get_convention(today)    
    greeting['convention_cnt'] = len(greeting['convention'])

    if request.is_ajax and request.method=='POST':
        save_form = fall_obj.save_form(request)
        if save_form == 1:
            error = 0
            msg=reg_succ_msg
        elif save_form == 2:
            error = 1
            msg="Mail send error";
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'fall_registration.html',greeting)

def get_ada_membership_info(request):
    if request.is_ajax and request.method=='POST':
        ada_number = (request.POST.get('ada_number')).strip()
        member_res = Ada_membership.objects.filter(ADA_Number=ada_number)
        if member_res:
            member = serializers.serialize("json", member_res)
        else:
            member = 0        
        return JsonResponse({"valid":True,"data":member}, status = 200)


def get_ada_membership_address(request):
    if request.is_ajax and request.method=='POST':
        fname = ((request.POST.get('fname')).strip()).lower()
        lname = ((request.POST.get('lname')).strip()).lower()
        member_res = Ada_membership.objects.annotate(
            lowered_nospace_fname=Lower(Replace('First_Name', Value(' '), Value(''))),
            lowered_nospace_lname=Lower(Replace('Last_Name', Value(' '), Value('')))
        ).filter(
            lowered_nospace_fname=fname,
            lowered_nospace_lname=lname
        )
        if member_res:
            member = serializers.serialize("json", member_res)
        else:
            member = 0        
        return JsonResponse({"valid":True,"data":member}, status = 200)

@login_required()
def spring_registration(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Spring Registration' 

    today=dt.date.today()
    greeting['convention'] = sp_obj.get_convention(today)
    if request.is_ajax and request.method=='POST':
        spr_form=sp_obj.save_registration(request)
        if spr_form == 1:
            error = 0
            msg=reg_succ_msg
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'spring_registration.html',greeting)

@login_required()
def convention_registration(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Registration'
    

    # get convention type
    today = dt.date.today() 
    greeting['convention'] = con_obj.get_convention(today)
    greeting['workshops'] = con_obj.get_worshop()
    greeting['workshops_cnt'] = len(greeting['workshops'])  

    if request.is_ajax and request.method=='POST':
        save_form = con_obj.save_form(request)
        if save_form == 1:
            error = 0
            msg=reg_succ_msg
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'convention_registration.html',greeting)

def vendor_email_check(request):
    error = 0
    msg = ""
    if request.is_ajax and request.method=='POST':
        email_check = vendor_obj.check_email(request)
        if email_check==1:
            error = 1
            msg = "Email Already Exists"
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)
    else:
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

@login_required()
def vendor_edit(request,id):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor'
    hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
    decoded_id = hashids.decode(id) 
    if decoded_id:
        vendor_id = decoded_id[0]


    if request.method=='GET':        
        vendor_res = vendor_obj.get_vendor(request,vendor_id)
        greeting['vendor'] = vendor_res[0]
        
    if request.is_ajax and request.method=='POST':
        save_form = vendor_obj.save_form(request)
        if save_form == 1:
            error = 0
            msg=update_succ_msg
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'vendor_edit.html',greeting)

@login_required()
def vendor_detail(request,id):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Details'
    hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
    decoded_id = hashids.decode(id) 
    if decoded_id:
        vendor_id = decoded_id[0]

    if request.method=='GET':        
        vendor_res = vendor_obj.get_vendor(request,vendor_id)
        greeting['vendor'] = vendor_res[0]
        staff_res = vendor_obj.get_staff(request,vendor_id)
        greeting['staff'] = staff_res
        greeting['staff_cnt'] = len(staff_res)

    return render(request,'vendor_detail.html',greeting)

@login_required()   
def exhibitor_registration(request):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Registration'

    module=request.POST.get('module')
    if module and module=='list':
        result=vendor_obj.vendor_registrations_list(request)
        return JsonResponse(result, status = 200)


    return render(request,'exhibitor_registration.html',greeting)

def convention_edit(request,param1):
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Edit'
    hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
    decoded_id = hashids.decode(param1) 
    if decoded_id:
        hand_id = decoded_id[0]
        handon_details = con_obj.get_form(hand_id)
        greeting['handon_details'] = handon_details
        if len(handon_details)==0:
            return redirect('convention_transaction')

    today = dt.date.today() 
    greeting['convention'] = con_obj.get_convention(today)
    greeting['workshops'] = con_obj.get_worshop()
    greeting['workshops_cnt'] = len(con_obj.get_worshop())  

    if request.is_ajax and request.method=='POST':
        save_form = con_obj.update_form(request,hand_id)
        if save_form == 1:
            error = 0
            msg=update_succ_msg
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'convention_edit.html',greeting)

@login_required() 
def vendor_detail_print(request):
    if request.method=='POST':
        result=vendor_obj.vendor_details_print(request)
    else:
        result=''
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Exhibitor Registration Print'
    greeting['datas'] = result
    return render(request,'vendor_detail_print.html',greeting)

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
                    raise FileNotFoundError(
                            'media URI must start with %s or %s' % (surl, murl)
                    )
            return path
    except Exception as e:
        return e

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
    
def vendor_pdf(request):
    greeting={}
    greeting['title'] = 'Exhibitor Registration Detail'
    result=vendor_obj.vendor_details_print(request)
    greeting['datas'] = result
    return render_to_pdf('vendor_detail_pdf.html',greeting)
    
