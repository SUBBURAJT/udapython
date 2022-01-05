from django.db.models.aggregates import Count
from django.http import HttpResponse
from django.db.models import Q , FilteredRelation
from admin_uda.models import Handon_form
import datetime as dt
import csv 
from hashids import Hashids
class convention_transactions():
    date_format = '%m-%d-%Y'
    date_format_input = '%m/%d/%Y'
    date_format_db = '%Y-%m-%d'

    def condition_query_fn(self,request,condt):
        result = {}
        
        #filters
        flt_sdate=request.POST.get('fltr_start_date')
        flt_edate=request.POST.get('fltr_end_date')
            
        if flt_sdate and flt_edate:
            flt1_strdate = dt.datetime.strptime(str(flt_sdate),self.date_format_input).strftime(self.date_format_db)
            flt1_endate = dt.datetime.strptime(str(flt_edate),self.date_format_input).strftime(self.date_format_db)
            condt+=" AND DATE(A.created_on) >= '"+str(flt1_strdate)+"' AND DATE(A.created_on) <= '"+str(flt1_endate)+"'"

        group_where_hw1=''
        group_where_hw_q1=''
        group_where_ct1=''
        group_where_ct_q1=''
        select_hw1=''
        select_ct1=''
        keywordsearch=request.POST.get('keyword')
        if keywordsearch:
            condt+=" AND ( A.name LIKE '"+keywordsearch+"%' OR A.last_name LIKE '"+keywordsearch+"%' OR A.practice_name LIKE '"+keywordsearch+"%' OR A.email LIKE '"+keywordsearch+"%' OR A.phone LIKE '"+keywordsearch+"%' OR A.transaction_ref LIKE '"+keywordsearch+"%' "
            if keywordsearch=='Success' or keywordsearch=='Failure' or keywordsearch=='Pending':
                if keywordsearch=='Pending':
                    condt+=" OR (A.transaction_status IS NULL)"
                else:
                    condt+=" OR A.transaction_status LIKE '"+keywordsearch+"%' "
            condt+=")"
            group_where_hw1+=" name LIKE '"+keywordsearch+"%'"
            group_where_ct1+=" name LIKE '"+keywordsearch+"%'"
            if group_where_hw1!='':
                group_where_hw_q1+=" AND "+group_where_hw1
                select_hw1+=",(SELECT GROUP_CONCAT(name) FROM admin_uda_handon_form_workshop WHERE hand_id_id=A.id "+group_where_hw_q1+") AS hw_names,(SELECT COUNT(work_id_id) FROM admin_uda_handon_form_workshop WHERE hand_id_id=A.id "+group_where_hw_q1+") AS hw_ids1"
            if group_where_ct1!='':
                group_where_ct_q1+=" AND "+group_where_ct1
                select_ct1+=",(SELECT GROUP_CONCAT(name) FROM admin_uda_convention_form_workshop WHERE hand_id=A.id "+group_where_ct_q1+") AS ct_names,(SELECT COUNT(work_id) FROM admin_uda_convention_form_workshop WHERE hand_id=A.id "+group_where_ct_q1+") AS ct_ids1"

        result['select_ct1'] = select_ct1
        result['select_hw1'] = select_hw1
        result['condt'] = condt
        return result

    def condition_query_funtion(self,request,condt):
        result = {}
        reg_cat=request.POST.get('ad_reg_cat_hid')
        group_where_hw=''
        group_where_hw_q=''
        group_where_ct=''
        group_where_ct_q=''
        select_hw=''
        select_ct=''
        if reg_cat:
            reg=reg_cat.split(',')
            for d in reg:
                r=d.split('-')
                if r[0]=='ct':
                    group_where_ct+=','+r[1]
                elif r[0]=='hw':
                    group_where_hw+=','+r[1]
            if group_where_ct!='':
                group_where_ct_q+=" AND (work_id IN ("+group_where_ct.lstrip(",")+"))"
                select_ct+=",(SELECT COUNT(work_id) FROM admin_uda_convention_form_workshop WHERE hand_id=A.id "+group_where_ct_q+") AS ct_ids"
            if group_where_hw!='':
                group_where_hw_q+=" AND (work_id_id IN ("+group_where_hw.lstrip(",")+"))"
                select_hw+=",(SELECT COUNT(work_id_id) FROM admin_uda_handon_form_workshop WHERE hand_id_id=A.id "+group_where_hw_q+") AS ct_ids"

        flt_status=request.POST.get('flt_status')
        if flt_status == "1":
            condt+=" AND ( A.off_transaction_status = '"+flt_status+"' )"
        elif flt_status == "2":
           condt+=" AND ( A.off_transaction_status = '"+flt_status+"' )"

        result['select_ct'] = select_ct
        result['select_hw'] = select_hw
        result['condt'] = condt

        return result

    def advance_search(self,request,condt):
        result = {}
        #advance search filters
        f_name=request.POST.get('f_name')
        if f_name!='':
            condt+=" AND ( A.name LIKE '"+f_name+"%' ) "

        l_name=request.POST.get('l_name')
        if l_name!='':
            condt+=" AND ( A.last_name LIKE '"+l_name+"%' ) "

        p_name=request.POST.get('p_name')
        if p_name!='':
            condt+=" AND ( A.practice_name LIKE '"+p_name+"%' ) "

        phone=request.POST.get('phone')
        if phone!='':
            condt+=" AND ( A.phone LIKE '"+phone+"%' ) "

        email=request.POST.get('email')
        if email!='':
            condt+=" AND ( A.email LIKE '"+email+"%' ) "

        trans_no=request.POST.get('trans_no')
        if trans_no!='':
            condt+=" AND ( A.transaction_ref LIKE '"+trans_no+"%' ) "

        price_start=request.POST.get('price_start')
        if price_start!='':
            condt+=" AND ( A.amount >= "+str(price_start)+" ) "

        price_end=request.POST.get('price_end')
        if price_end!='':
            condt+=" AND ( A.amount <= "+str(price_end)+" ) "

        start_date=request.POST.get('start_date')
        end_date=request.POST.get('end_date')
        if start_date and end_date:
            flt_strdate = dt.datetime.strptime(str(start_date),self.date_format_input).strftime(self.date_format_db)
            flt_endate = dt.datetime.strptime(str(end_date),self.date_format_input).strftime(self.date_format_db)
            condt+=" AND DATE(A.created_on) >= '"+str(flt_strdate)+"' AND DATE(A.created_on) <= '"+str(flt_endate)+"'"

        tr_online=request.POST.get('adv_on')
        tr_offline=request.POST.get('adv_off')
        if tr_online == '1' and tr_offline == '2':
            condt+=" AND ( A.off_transaction_status = "+tr_online+" OR A.off_transaction_status = "+tr_offline+" ) "
        elif tr_online == '1':
            condt+=" AND ( A.off_transaction_status = "+tr_online+" ) "
        elif tr_offline == '2':
            condt+=" AND ( A.off_transaction_status = "+tr_offline+" ) "

        result['condt'] = condt
        return result

    def query_builder(self,select_ct,select_ct1,select_hw,select_hw1,condt):
        trans_que="select A.id as Id,A.name,A.created_on,A.last_name,A.practice_name,A.off_transaction_id,A.amount,A.email,A.phone,A.browser,A.os,A.transaction_status,A.transaction_ref,A.archive_id,A.off_transaction_status,A.status,A.updated_grand_amount,A.created_by,B.name as registered_name,C.id,COUNT(C.id) as printcount "+select_ct+select_hw+select_ct1+select_hw1+" from admin_uda_handon_form As A LEFT JOIN admin_uda_users as B ON B.id = A.created_by LEFT JOIN admin_uda_id_prints as C ON C.parent_id = A.id where "+condt+" GROUP By A.id"
        if select_hw!='':
            trans_que+=" HAVING hw_ids>0 "
        if select_ct!='':
            if select_hw!='':
                trans_que+=" AND ct_ids>0 "
            else:
                trans_que+=" HAVING ct_ids>0 "        
        if select_hw1!='':
            if trans_que.find('HAVING')==-1:
                trans_que+=" HAVING hw_ids1>0 "
            else:
                trans_que+=" OR hw_ids1>0 "        
        if select_ct1!='':
            if trans_que.find('HAVING')==-1:
                trans_que+=" HAVING ct_ids1>0 "
            else:
                trans_que+=" OR ct_ids1>0 "
        return trans_que

    def list_convention_transactions(self,request):
        flt_archive=request.POST.get('archive')
        condt='A.status!=2 AND A.form=1 AND A.form_status IN (1,3)'

        condt+=" AND A.archive_id="+flt_archive if flt_archive else " AND A.archive_id=0 "

        singlenamesearch=request.POST.get('singlenamesearch')
        if singlenamesearch and singlenamesearch!='all':
            condt+=" AND ( A.name LIKE '"+singlenamesearch+"%' OR A.last_name LIKE '"+singlenamesearch+"%' OR A.practice_name LIKE '"+singlenamesearch+"%' OR A.email LIKE '"+singlenamesearch+"%' OR A.phone LIKE '"+singlenamesearch+"%' OR A.transaction_ref LIKE '"+singlenamesearch+"%' "
            """
            if singlenamesearch=='Success' or singlenamesearch=='Failure' or singlenamesearch=='Pending':
                if singlenamesearch=='Pending':
                    condt+=" OR (A.transaction_status IS NULL)"
                else:
                    condt+=" OR A.transaction_status LIKE '"+singlenamesearch+"%' "
            """

            condt+=")"

        condition_query_fn_res = self.condition_query_fn(request,condt)
        select_ct1 = condition_query_fn_res['select_ct1']
        select_hw1 = condition_query_fn_res['select_hw1']
        condt = condition_query_fn_res['condt']
        condition_query_funtion_res = self.condition_query_funtion(request,condt)
        select_ct = condition_query_funtion_res['select_ct']
        select_hw = condition_query_funtion_res['select_hw']
        condt = condition_query_funtion_res['condt']
        advance_search_res = self.advance_search(request,condt)
        condt = advance_search_res['condt']        
        trans_que = self.query_builder(select_ct,select_ct1,select_hw,select_hw1,condt)
        data_new=Handon_form.objects.raw(trans_que,None)
        tot_count=len(list(data_new))
        nd=[]
        res={}
       
        for datas in data_new:
            nested_data=[]
            off_on_status=datas.off_transaction_status
            if off_on_status==2:
                clname="offstatus"
                clnamet="offstatus"
                off_transaction_id=datas.transaction_ref
                reg_name="""<div class="mt-1 mt-sm-2 d-block">
                                    <h6 class="mb-0 fs-12 fw-semibold """+clname+"""">Registered By :
                                        <span class="fs-12 """+clnamet+""""> """+datas.registered_name+"""</span>
                                    </h6>
                                </div>"""
            else:
                clname=''
                clnamet='text-muted'
                off_transaction_id=datas.off_transaction_id
                reg_name=''
            hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
            hashid = hashids.encode(datas.Id) 
            sp_date=datas.created_on.date()
            name=datas.name
            last_name=datas.last_name
            practice_name=datas.practice_name
            email=datas.email
            phone=datas.phone
            amount=datas.amount
            transaction_status=datas.transaction_status
            tran_os=datas.os
            tran_browser=datas.browser
            t_date_f = "<span class="+clname+">"+dt.datetime.strptime(str(sp_date),self.date_format_db).strftime(self.date_format)+"</span>"
            ct_names=''
            hw_names=''
            if select_ct1!='':
                ct_names="<span style='color:yellow'>"+datas.ct_names+"</span>"
            if select_hw1!='':
                hw_names="<span style='color:yellow'>"+datas.hw_names+"</span>"
            
            name_data="""<div class="d-flex align-items-center">
                            <div class="activity-icon avatar-xs me-2">
                                <span class="avatar-title bg-soft-warning text-warning br-5">"""+name[0].capitalize()+last_name[0].capitalize()+"""</span>
                            </div>
                            <span class="""+clnamet+""">"""+name+' '+last_name+"""</span>
                        </div>"""
            practice_info="""<div>
                                <div class="d-block">
                                      <h6 class="mb-0 fs-13 fw-semibold """+clname+"""">Practice Name :
                                        <span class="fs-13 """+clnamet+""""> """+practice_name+"""</span>
                                    </h6>
                                </div>
                                <div class="mt-1 mt-sm-2 d-block">
                                   <h6 class="mb-0 fs-12 fw-semibold """+clname+"""">Email :
                                        <span class="fs-12 """+clnamet+""""> """+email+"""</span>
                                    </h6>
                                </div>
                                <div class="mt-1 mt-sm-2 d-block">
                                   <h6 class="mb-0 fs-12 fw-semibold """+clname+"""">Phone :
                                        <span class="fs-12 """+clnamet+""""> """+str(phone)+"""</span>
                                    </h6>
                                </div>
                            </div>"""
            transactions="""<div>
                                <div class="d-block">
                                    <h6 class="mb-0 fs-13 fw-semibold """+clname+""""">Transaction ID :
                                        <span class="fs-13 """+clnamet+""""> """+str(off_transaction_id)+"""</span>
                                    </h6>
                                </div>
                                <div class="mt-1 mt-sm-2 d-block">
                                   <h6 class="mb-0 fs-13 fw-semibold """+clname+""""">Amount :
                                        <span class="fs-13 """+clnamet+""""> $"""+str(amount)+"""</span>
                                    </h6>
                                </div>
                            </div>"""+reg_name

            if transaction_status is None:
                ts="<i class='fa fa-circle me-2 fs-10 text-warning'></i><span class='"+clname+"'>Pending</span>"
            elif transaction_status!="Success":
                ts="<i class='fa fa-circle me-2 fs-10 text-danger'></i><span class='"+clname+"'>Failure</span>"
            else:
                ts="<i class='fa fa-circle me-2 fs-10 text-success'></i><span class='"+clname+"'>Success</span>"

            transaction_stattuses="""<div class="d-flex align-items-center">
                                        """+ts+"""
                                     </div>"""
            browswer_log="<span class='"+clname+"'>"+tran_browser +" ("+tran_os+")</span>"
            if transaction_status=='Success':
                actions="""<div class="btn-group">
                                <button type="button" class="btn fs-15 py-0" data-toggle="dropdown">
                                    <i class="fa fa-ellipsis-h "></i>
                                </button>
                                <ul class="dropdown-menu show action-dd" role="menu"
                                    data-popper-placement="bottom-end">
                                    <li><a class="text-dark view_details" data-method="view" data-id="""+hashid+"""><span
                                                class='avatar avatar-xs brround bg-violet-transparent'><i
                                                    class='fa fa-eye'></i></span> View</a></li>
                                    <li><a data-id="""+hashid+""" data-bs-effect="effect-flip-vertical"
                                                    data-bs-toggle="modal" class="text-dark edit_details"><span
                                                        class='avatar avatar-xs brround bg-green-transparent'><i
                                                            class=' fas fa-pencil-alt'></i></span> Edit</a></li>
                                    <li><a class="text-dark view_pdf" data-id="""+hashid+"""><span
                                                class='avatar avatar-xs brround bg-brown-transparent'><i
                                                    class='fa fa-download'></i></span> Download</a></li>
                                    <li><a class="text-dark view_details" data-method="print" data-id="""+hashid+"""><span
                                                class='avatar avatar-xs brround bg-brown-transparent'><i
                                                    class='fa fa-print'></i></span> Print</a></li>
                                    <li><a class="text-dark id_card_print" data-id="""+hashid+"""><span
                                                class='avatar avatar-xs brround bg-brown-transparent'><i
                                                    class='fa fa-tag'></i></span> Name tag print</a></li>
                                    <li><a class="text-dark tabArchieve" data-id="""+str(datas.Id)+"""><span
                                                class='avatar avatar-xs brround bg-brown-transparent'><i
                                                    class='fa fa-archive'></i></span> Move to archive</a></li>
                                    <li><a class="text-dark tabDelete" data-id="""+str(datas.Id)+"""><span
                                                class='avatar avatar-xs brround bg-red-transparent'><i
                                                    class='fa fa-trash'></i></span> Delete</a></li>
                                </ul>
                            </div>"""
                check_box="""<td>
                            <div class="form-check mb-0">
                                <input class="form-check-input child_check" name="name_tag_print" type="checkbox" id="formCheck2" value='"""+str(datas.Id)+"""'>
                            </div>
                        </td>"""
            else:
                actions="""<div class="btn-group">
                                <button type="button" class="btn fs-15 py-0" data-toggle="dropdown">
                                    <i class="fa fa-ellipsis-h "></i>
                                </button>
                                <ul class="dropdown-menu show action-dd" role="menu"
                                    data-popper-placement="bottom-end">
                                    <li><a class="text-dark view_details" data-method="view" data-id="""+hashid+"""><span
                                                class='avatar avatar-xs brround bg-violet-transparent'><i
                                                    class='fa fa-eye'></i></span> View</a></li>
                                    <li><a class="text-dark tabArchieve" data-id="""+str(datas.Id)+"""><span
                                                class='avatar avatar-xs brround bg-brown-transparent'><i
                                                    class='fa fa-archive'></i></span> Move to archive</a></li>
                                    <li><a class="text-dark tabDelete" data-id="""+str(datas.Id)+"""><span
                                                class='avatar avatar-xs brround bg-red-transparent'><i
                                                    class='fa fa-trash'></i></span> Delete</a></li>
                                </ul>
                            </div>"""
                check_box=""
            nested_data.append(check_box)
            nested_data.append(t_date_f)
            nested_data.append(name_data)
            nested_data.append(practice_info)
            nested_data.append(transactions)
            nested_data.append(transaction_stattuses)
            nested_data.append(browswer_log)
            nested_data.append(actions)
            nd.append(nested_data)

        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

    def get_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def delete_convention_transactions(self,request):
        ids=request.POST.get('id')
        form=Handon_form.objects.get(id=ids)
        form.status=2
        form.deleted_by = 0
        form.deleted_on = dt.datetime.now()
        form.deleted_ip = self.get_ip(request)
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}

    def archive_convention_transactions(self,request):
        ids=request.POST.get('id')
        arch=request.POST.get('arch')
        form=Handon_form.objects.get(id=ids)
        form.archive_id=arch
        form.updated_by = 0
        form.updated_on = dt.datetime.now()
        form.updated_ip = self.get_ip(request)
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}
    def export_transaction(self):
        res=HttpResponse(content_type='text/csv')
        res['Content-Disposition']='attachment; filename="fall_transaction.csv"'
        writer=csv.writer(res)
        writer.writerow(['Date','Name','Practice Name','Email','Phone','Transaction ID','Transaction Created Date','Payment Mode','Payment Details','Memo','Amount','Status','Browser Log'])
        data=Handon_form.objects.raw("select A.id as Id,A.name,A.created_on,A.last_name,A.practice_name,A.amount,A.email,A.phone,A.browser,A.os,A.transaction_status,A.off_transaction_id,A.transaction_ref,A.archive_id,A.off_transaction_status,A.status,A.created_by,A.off_transaction_created_date,A.off_transaction_payment_mode,A.off_transaction_payment_details,off_transaction_memo,B.name as registered_name,C.id,COUNT(C.id) as printcount from admin_uda_handon_form As A LEFT JOIN admin_uda_users as B ON B.id = A.created_by LEFT JOIN admin_uda_id_prints as C ON C.parent_id = A.id where A.status!=2 AND A.form=1 AND A.form_status IN (1,3) GROUP By A.id",None)
        payment_modes=["","Cash","Cheque/DD","POS","Venmo","Others"]
        for datas in data:
            sp_date=datas.created_on.date()
            name=datas.name
            last_name=datas.last_name
            practice_name=datas.practice_name
            email=datas.email
            phone=datas.phone
            created_date = datas.off_transaction_created_date.date()
            payment_mode=''
            if datas.off_transaction_payment_mode:
                payment_mode=payment_modes[int(datas.off_transaction_payment_mode)]
            payment_details = datas.off_transaction_payment_details
            off_transaction_memo = datas.off_transaction_memo
            amount='$'+str(datas.amount)
            if datas.off_transaction_status==2:
                off_transaction_id=datas.off_transaction_id
            else:
                off_transaction_id=datas.transaction_ref

            transaction_status=datas.transaction_status
            if transaction_status is None:
                transaction_status='Pending'
            elif transaction_status!='Success':
                 transaction_status='Failed'

            tran_os=datas.os
            tran_browser=datas.browser
            os_bro=tran_browser
            if tran_os is not None:
                os_bro=tran_browser+' ('+tran_os+')'
            t_date_f=dt.datetime.strptime(str(sp_date),self.date_format_db).strftime(self.date_format)
            tran_date_f=dt.datetime.strptime(str(created_date),self.date_format_db).strftime(self.date_format)
            writer.writerow([t_date_f,name+' '+last_name,practice_name,email,phone,off_transaction_id,tran_date_f,payment_mode,payment_details,off_transaction_memo,amount,transaction_status,os_bro])
        return res