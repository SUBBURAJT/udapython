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

reg_succ_msg = "Registered Successfully"
update_succ_msg = "Updated Successfully"
reg_err_msg = "Someting went to wrong! Please Try Again"

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
    
    # get convention type
    today = dt.date.today() 
    greeting['convention'] = FallRegistration.get_convention(today)    
    greeting['convention_cnt'] = len(greeting['convention'])

    if request.is_ajax and request.method=='POST':
        save_form = FallRegistration.save_form(request)
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
    greeting['convention'] = SpringRegistration.get_convention(today)
    if request.is_ajax and request.method=='POST':
        spr_form=SpringRegistration.saveRegistration(request)
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
    con_obj = ConventionRegistration()

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
        email_check = VendorRegistration.check_email(request)
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
        vendor_res = VendorRegistration.get_vendor(request,vendor_id)
        greeting['vendor'] = vendor_res[0]
        
    if request.is_ajax and request.method=='POST':
        save_form = VendorRegistration.save_form(request)
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
        vendor_res = VendorRegistration.get_vendor(request,vendor_id)
        greeting['vendor'] = vendor_res[0]
        staff_res = VendorRegistration.get_staff(request,vendor_id)
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
        result=VendorRegistration.vendor_registrations_list(request)
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
        handon_details = ConventionRegistration.get_form(hand_id)
        greeting['handon_details'] = handon_details
        if len(handon_details)==0:
            return redirect('convention_transaction')

    today = dt.date.today() 
    greeting['convention'] = ConventionRegistration.get_convention(today)
    greeting['workshops'] = ConventionRegistration.get_worshop()
    greeting['workshops_cnt'] = len(ConventionRegistration.get_worshop())  

    if request.is_ajax and request.method=='POST':
        save_form = ConventionRegistration.update_form(request,hand_id)
        if save_form == 1:
            error = 0
            msg=update_succ_msg
        else:
            error = 1
            msg=reg_err_msg
        return JsonResponse({"valid":True,"err":error,"msg":msg}, status = 200)

    return render(request,'convention_edit.html',greeting)
    
    
