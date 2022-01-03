from django.shortcuts import redirect, render
from admin_uda.models import Convention_types,Convention_archive
from admin_uda.transactions.spring_transaction import spring_transactions
from admin_uda.transactions.convention_transaction import convention_transactions
from admin_uda.transactions.fall_transaction import fall_transactions
from admin_uda.transactions.convention_detail import convention_details
from admin_uda.transactions.convention_id_card_print import convention_id_card_details
from admin_uda.transactions.convention_id_card_print_bulk import convention_id_card_bulk_details
from admin_uda.transactions.convention_detail_pdf import convention_details_pdf
import datetime as dt
import json
from django.template.defaulttags import register
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers
from django.db.models import Value
from django.db.models.functions import Lower, Replace, Concat
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.conf import settings
from hashids import Hashids
import os
conobj=convention_transactions()
spobj=spring_transactions()
fallobj=fall_transactions()
con_trans_redirect = '/convention_transaction'

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
        return spobj.export_transaction()

    greeting = {}
    con_types=Convention_types.objects.filter(status=1,form_status=2).order_by('id')
    con_arc=Convention_archive.objects.all().order_by('-id')
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Spring Transactions'
    greeting['con_types'] = con_types
    greeting['con_arc'] = con_arc
    return render(request,'spring_transaction.html',greeting)

def spring_transaction_operations(request):
    module=request.POST.get('module')
    if module and module=='list':
        result=spobj.list_spring_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=spobj.delete_spring_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=spobj.archive_spring_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def convention_transaction(request):
    module=request.POST.get('module')
    if module is not None and module=="export":
        return conobj.export_transaction()
        
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
        result=conobj.list_convention_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=conobj.delete_convention_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=conobj.archive_convention_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def fall_transaction(request):
    module=request.POST.get('module')
    if module is not None and module=="export":
        return fallobj.export_transaction()
        
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
        result=fallobj.list_fall_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='delete':
        result=fallobj.delete_fall_transactions(request)
        return JsonResponse(result, status = 200)
    elif module and module=='archive':
        result=fallobj.archive_fall_transactions(request)
        return JsonResponse(result, status = 200)

@login_required()
def convention_detail(request,ids):
    con_det_obj = convention_details()
    dat=con_det_obj.view_transaction_details(request,ids)
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
        return redirect(con_trans_redirect)
    return render(request,'convention_detail.html',greeting)

@login_required()
def convention_detail_idcard(request,ids):
    objconid=convention_id_card_details()
    dat=objconid.id_card_details(request,ids)
    if dat['ext']==1:
        return redirect(con_trans_redirect)
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transaction ID Cards'
    greeting['datas'] = dat
    return render(request,'convention_id_card_print.html',greeting)

def convention_id_card_print_bulk(request):
    objbulk=convention_id_card_bulk_details()
    dat=objbulk.id_card_details_bulk(request)
    if dat['ext']==1:
        return redirect(con_trans_redirect)
    greeting = {}
    greeting['pageview'] = "Dashboard"
    greeting['title'] = 'Convention Transaction ID Cards'
    greeting['datas'] = dat
    return render(request,'convention_id_card_print_bulk.html',greeting)

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
                    raise Exception(
                            'media URI must start with %s or %s' % (surl, murl)
                    )
            return path
def get_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def transactions_pdf(request,ids):
    hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
    hashid = hashids.decode(ids) 
    tid=hashid[0]
    objconpdf=convention_details_pdf()
    dat=objconpdf.pdf_transaction_details(tid)
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
        return redirect(con_trans_redirect)
    else:
        return get_pdf('mail_attachment.html',greeting)


