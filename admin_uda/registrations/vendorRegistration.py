from admin_uda.models import *
import datetime as dt
from django.db.models import Q

class VendorRegistration():
    def check_email(request):  
        result = 0      
        req_email = request.POST.get('email')
        req_id = request.POST.get('id')
        if req_id:
            if Vendor_registration_form.objects.filter(~Q(id=req_id), email=req_email,status=1).exists():
                result = 1
        else:
            if Vendor_registration_form.objects.filter(email=req_email).exists():
                result = 1

        return result

    def get_vendor(request,id):
        if id:
            res = Vendor_registration_form.objects.values().filter(id=id,status=1)
        else:
            res = []
        return res

    def get_staff(request,id):
        if id:
            res = Vendor_employees.objects.values().filter(vendor_id=id)
        else:
            res = []
        return res

    def vendor_registrations_list(request):
        res={}
        where_cond = ''
        where_cond += ' WHERE a.status != 2 '

        singlenamesearch=request.POST.get('singlenamesearch')
        if singlenamesearch and singlenamesearch!='all':
            where_cond += " AND ( a.company_name LIKE '"+singlenamesearch+"%' OR a.first_name LIKE '"+singlenamesearch+"%' OR a.last_name LIKE '"+singlenamesearch+"%' OR a.email LIKE '"+singlenamesearch+"%' OR a.phone LIKE '"+singlenamesearch+"%' OR a.address LIKE '"+singlenamesearch+"%' )"

        
        flt_sdate=request.POST.get('fltr_start_date')
        flt_edate=request.POST.get('fltr_end_date')
        if flt_sdate and flt_edate:
            flt_strdate = dt.datetime.strptime(str(flt_sdate),'%m/%d/%Y').strftime('%Y-%m-%d')
            flt_endate = dt.datetime.strptime(str(flt_edate),'%m/%d/%Y').strftime('%Y-%m-%d')
            where_cond += " AND DATE(A.created_on) >= '"+str(flt_strdate)+"' AND DATE(A.created_on) <= '"+str(flt_endate)+"'"

        sql = "SELECT a.* FROM admin_uda_vendor_registration_form as a "+where_cond + " order by id desc"

        vendor_lists = Vendor_registration_form.objects.raw(sql,None)
        tot_count=len(list(vendor_lists))
        nd=[]
        for vendor in vendor_lists:
            nestedData=[]
            name_sec = '''<div class="d-flex align-items-center">
                                        <div class="activity-icon avatar-xs me-2">
                                            <span class="avatar-title bg-soft-warning text-warning br-5">'''+ vendor.first_name[0].capitalize()+vendor.last_name[0].capitalize() +'''</span>
                                        </div>
                                        ''' + vendor.first_name + ' ' + vendor.last_name +  '''
                                    </div>'''
            date_sec = dt.datetime.strptime(str(vendor.created_on.date()),'%Y-%m-%d').strftime('%m/%d/%Y')
            addr_sec = vendor.address+', '+vendor.city+', '+vendor.state
            act_sec = '''<div class="btn-group">
                                        <button type="button" class="btn fs-15 py-0" data-toggle="dropdown">
                                            <i class="fa fa-ellipsis-h "></i>
                                        </button>
                                        <ul class="dropdown-menu show action-dd" role="menu"
                                            data-popper-placement="bottom-end">
                                            <li><a href="/vendor_detail/'''+ str(vendor.id) +'''" class="text-dark"><span
                                                        class='avatar avatar-xs brround bg-violet-transparent'><i
                                                            class='fa fa-eye'></i></span> View</a></li>
                                            <li><a href="/vendor_edit/'''+ str(vendor.id) +'''" class="text-dark"><span
                                                        class='avatar avatar-xs brround bg-green-transparent'><i
                                                            class=' fas fa-pencil-alt'></i></span> Edit</a></li>
                                            <li><a class="text-dark"><span
                                                        class='avatar avatar-xs brround bg-brown-transparent'><i
                                                            class='fa fa-print'></i></span> Print QR Code</a></li>
                                            <li><a class="text-dark"><span
                                                        class='avatar avatar-xs brround bg-brown-transparent'><i
                                                            class='fa fa-envelope'></i></span> Send QR code via
                                                    email</a>
                                            </li>
                                            <li><a class="text-dark tabDelete"><span
                                                        class='avatar avatar-xs brround bg-red-transparent'><i
                                                            class='fa fa-trash'></i></span> Delete</a></li>
                                        </ul>
                                    </div>'''
            nestedData.append('<div class="form-check mb-0"><input class="form-check-input" type="checkbox" id="formCheck2"></div>')
            nestedData.append(name_sec)
            nestedData.append(date_sec)
            nestedData.append(vendor.company_name)
            nestedData.append(vendor.phone)
            nestedData.append(vendor.email)
            nestedData.append(addr_sec)
            nestedData.append(act_sec)
            nd.append(nestedData)

        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

    def save_form(request):
        id = request.POST.get('hdn_vendor_id')
        if int(id)>0:
            form_data = Vendor_registration_form.objects.get(id=id,status=1)
            form_data.company_name = request.POST.get('company_name')
            form_data.first_name = request.POST.get('first_name')
            form_data.last_name = request.POST.get('last_name')
            form_data.phone = request.POST.get('phone')
            form_data.email = request.POST.get('email')
            form_data.address = request.POST.get('address')
            form_data.city = request.POST.get('city')
            form_data.state = request.POST.get('state')
            form_data.zipcode = request.POST.get('zip')
            form_data.created_on=dt.datetime.now()
            form_data.save()
            LastInsertId = form_data.id
            if LastInsertId:
                result = 1
            else:
                result=0
        else:
            result=0
        return result