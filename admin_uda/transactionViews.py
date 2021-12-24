from django.shortcuts import redirect, render
from admin_uda.models import *
from admin_uda.transactions.spring_transaction import spring_transactions
from admin_uda.transactions.convention_transaction import convention_transactions
from admin_uda.transactions.fall_transaction import fall_transactions
from admin_uda.transactions.convention_detail import convention_details
from admin_uda.transactions.convention_id_card_print import convention_id_card_details
from admin_uda.transactions.convention_id_card_print_bulk import convention_id_card_bulk_details
import datetime as dt
import json
from django.template.defaulttags import register
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Value
from django.db.models.functions import Lower, Replace, Concat
from django.contrib.auth.decorators import login_required



@register.filter
def get_range(value):
    return range(value)
@register.filter
def get_str(value):
    return str(value)

@login_required()
def spring_transaction(request):
    module=request.POST.get('module')
    if module is not None and module=="export":
        return spring_transactions.export_transaction()

    greeting = {}
    con_types=Convention_types.objects.filter(status=1,form_status=2).order_by('id')
    con_arc=Convention_archive.objects.all().order_by('-id')
    greeting['pageview'] = "Dashboard new"
    greeting['title'] = 'Spring Transactions'
    greeting['con_types'] = con_types
    greeting['con_arc'] = con_arc
    return render(request,'spring_transaction.html',greeting)

def spring_transaction_operations(request):
    module=request.POST.get('module')
    if module and module=='list':
        result=spring_transactions.list_spring_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=spring_transactions.delete_spring_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=spring_transactions.archive_spring_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def convention_transaction(request):
    module=request.POST.get('module')
    if module is not None and module=="export":
        return convention_transactions.export_transaction()
        
    greeting = {}
    con_types=Convention_types.objects.filter(status=1,form_status=1).order_by('id')
    con_arc=Convention_archive.objects.all().order_by('-id')
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transactions'
    greeting['con_types'] = con_types
    greeting['con_arc'] = con_arc
    return render(request,'convention_transaction.html',greeting)

def convention_transaction_operations(request):
    module=request.POST.get('module')
    if module and module=='list':
        result=convention_transactions.list_convention_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=convention_transactions.delete_convention_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=convention_transactions.archive_convention_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def fall_transaction(request):
    module=request.POST.get('module')
    if module is not None and module=="export":
        return fall_transactions.export_transaction()
        
    greeting = {}
    con_types=Convention_types.objects.filter(status=1,form_status=3).order_by('id')
    con_arc=Convention_archive.objects.all().order_by('-id')
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Fall Transactions'
    greeting['con_types'] = con_types
    greeting['con_arc'] = con_arc
    return render(request,'fall_transaction.html',greeting)

def fall_transaction_operations(request):
    module=request.POST.get('module')
    if module and module=='list':
        result=fall_transactions.list_fall_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=fall_transactions.delete_fall_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=fall_transactions.archive_fall_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def convention_detail(request,ids,method):
    dat=convention_details.view_transaction_details(request,ids,method)
    greeting = {}
    greeting['pageview'] = "Dashboard"
    if dat['input']['form_status'] and dat['input']['form_status']==1:
        greeting['title'] = 'Convention Transaction Details'
    elif dat['input']['form_status'] and dat['input']['form_status']==2:
        greeting['title'] = 'Spring Transaction Details'
    elif dat['input']['form_status'] and dat['input']['form_status']==3:
        greeting['title'] = 'Fall Transaction Details'
    else:
        greeting['title'] = 'Convention Detail'
    greeting['datas'] = dat
    if dat['err']==1:
        return redirect('/convention_transaction')
    return render(request,'convention_detail.html',greeting)

@login_required()
def convention_detail_idcard(request,ids):
    dat=convention_id_card_details.id_card_details(request,ids)
    if dat['ext']==1:
        return redirect('/convention_transaction')
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transaction ID Cards'
    greeting['datas'] = dat
    return render(request,'convention_id_card_print.html',greeting)

def convention_id_card_print_bulk(request):
    dat=convention_id_card_bulk_details.id_card_details_bulk(request)
    if dat['ext']==1:
        return redirect('/convention_transaction')
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transaction ID Cards'
    greeting['datas'] = dat
    return render(request,'convention_id_card_print_bulk.html',greeting)
    


