from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt
from django.http import HttpResponse
import csv
from hashids import Hashids

class spring_transactions():
    def list_spring_transactions(request):
        hav=''
        condt='A.status!=2 AND A.form=1 AND A.form_status=2'
        #filters
        flt_sdate=request.POST.get('flt_start_date')
        flt_edate=request.POST.get('flt_end_date')
        flt_archive=request.POST.get('archive')
        if flt_archive:
            condt+=" AND A.archive_id="+flt_archive
        else:
            condt+= " AND A.archive_id=0 "

        if flt_sdate and flt_edate:
            ed_split=flt_sdate.split('/')
            flt_start_date=dt.date(int(ed_split[2]),int(ed_split[0]),int(ed_split[1]))
            ed_split_end=flt_edate.split('/')
            flt_end_date=dt.date(int(ed_split_end[2]),int(ed_split_end[0]),int(ed_split_end[1]))
            condt+=" AND DATE(A.created_on) >= '"+str(flt_start_date)+"' AND DATE(A.created_on) <= '"+str(flt_end_date)+"'"

        singlenamesearch=request.POST.get('singlenamesearch')
        if singlenamesearch and singlenamesearch!='all':
            condt+=" AND ( A.name LIKE '"+singlenamesearch+"%' OR A.last_name LIKE '"+singlenamesearch+"%' OR A.practice_name LIKE '"+singlenamesearch+"%' OR A.email LIKE '"+singlenamesearch+"%' OR A.phone LIKE '"+singlenamesearch+"%' OR A.transaction_ref LIKE '"+singlenamesearch+"%' "

            condt+=")"

        keywordsearch=request.POST.get('keyword')
        if keywordsearch:
            condt+=" AND ( A.name LIKE '"+keywordsearch+"%' OR A.last_name LIKE '"+keywordsearch+"%' OR A.practice_name LIKE '"+keywordsearch+"%' OR A.email LIKE '"+keywordsearch+"%' OR A.phone LIKE '"+keywordsearch+"%' OR A.transaction_ref LIKE '"+keywordsearch+"%' "
            if keywordsearch=='Success' or keywordsearch=='Failure' or keywordsearch=='Pending':
                if keywordsearch=='Pending':
                    condt+=" OR (A.transaction_status IS NULL)"
                else:
                    condt+=" OR A.transaction_status LIKE '"+keywordsearch+"%' "

            condt+=")"

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

        group_where_hw1=''
        group_where_hw_q1=''
        group_where_ct1=''
        group_where_ct_q1=''
        select_hw1=''
        select_ct1=''
        if keywordsearch:
            group_where_hw1+=" name LIKE '"+keywordsearch+"%'"
            group_where_ct1+=" name LIKE '"+keywordsearch+"%'"
            if group_where_hw1!='':
                group_where_hw_q1+=" AND "+group_where_hw1
                select_hw1+=",(SELECT GROUP_CONCAT(name) FROM admin_uda_handon_form_workshop WHERE hand_id_id=A.id "+group_where_hw_q1+") AS hw_names,(SELECT COUNT(work_id_id) FROM admin_uda_handon_form_workshop WHERE hand_id_id=A.id "+group_where_hw_q1+") AS hw_ids1"
            if group_where_ct1!='':
                group_where_ct_q1+=" AND "+group_where_ct1
                select_ct1+=",(SELECT GROUP_CONCAT(name) FROM admin_uda_convention_form_workshop WHERE hand_id=A.id "+group_where_ct_q1+") AS ct_names,(SELECT COUNT(work_id) FROM admin_uda_convention_form_workshop WHERE hand_id=A.id "+group_where_ct_q1+") AS ct_ids1"

        
        flt_status=request.POST.get('flt_status')
        if flt_status == "1":
            condt+=" AND ( A.off_transaction_status = '"+flt_status+"' )"
        elif flt_status == "2":
           condt+=" AND ( A.off_transaction_status = '"+flt_status+"' )"

        #advance search filters
        ad_first_name=request.POST.get('ad_first_name')
        if ad_first_name!='':
            condt+=" AND ( A.name LIKE '"+ad_first_name+"%' ) "

        ad_last_name=request.POST.get('ad_last_name')
        if ad_last_name!='':
            condt+=" AND ( A.last_name LIKE '"+ad_last_name+"%' ) "

        ad_prac_name=request.POST.get('ad_prac_name')
        if ad_prac_name!='':
            condt+=" AND ( A.practice_name LIKE '"+ad_prac_name+"%' ) "

        ad_phone=request.POST.get('ad_phone')
        if ad_phone!='':
            condt+=" AND ( A.phone LIKE '"+ad_phone+"%' ) "

        ad_email=request.POST.get('ad_email')
        if ad_email!='':
            condt+=" AND ( A.email LIKE '"+ad_email+"%' ) "

        ad_transaction_no=request.POST.get('ad_transaction_no')
        if ad_transaction_no!='':
            condt+=" AND ( A.transaction_ref LIKE '"+ad_transaction_no+"%' ) "

        ad_price_start=request.POST.get('ad_price_start')
        if ad_price_start!='':
            condt+=" AND ( A.amount >= "+str(ad_price_start)+" ) "

        ad_price_end=request.POST.get('ad_price_end')
        if ad_price_end!='':
            condt+=" AND ( A.amount <= "+str(ad_price_end)+" ) "

        ad_start_date=request.POST.get('ad_start_date')
        ad_end_date=request.POST.get('ad_end_date')
        if ad_start_date and ad_end_date:
            ed_split=ad_start_date.split('/')
            flt_start_date=dt.date(int(ed_split[2]),int(ed_split[0]),int(ed_split[1]))
            ed_split_end=ad_end_date.split('/')
            flt_end_date=dt.date(int(ed_split_end[2]),int(ed_split_end[0]),int(ed_split_end[1]))
            condt+=" AND DATE(A.created_on) >= '"+str(flt_start_date)+"' AND DATE(A.created_on) <= '"+str(flt_end_date)+"'"

        tr_online=request.POST.get('adv_on')
        tr_offline=request.POST.get('adv_off')
        if tr_online == '1' and tr_offline == '2':
            condt+=" AND ( A.off_transaction_status = "+tr_online+" OR A.off_transaction_status = "+tr_offline+" ) "
        elif tr_online == '1':
            condt+=" AND ( A.off_transaction_status = "+tr_online+" ) "
        elif tr_offline == '2':
            condt+=" AND ( A.off_transaction_status = "+tr_offline+" ) "
        
        trans_que="select A.id as Id,A.name,A.created_on,A.last_name,A.practice_name,A.off_transaction_id,A.amount,A.email,A.phone,A.browser,A.os,A.transaction_status,A.transaction_ref,A.archive_id,A.off_transaction_status,A.status,A.created_by,B.name as registered_name,C.id,COUNT(C.id) as printcount "+select_ct+select_hw+select_ct1+select_hw1+" from admin_uda_handon_form As A LEFT JOIN admin_uda_users as B ON B.id = A.created_by LEFT JOIN admin_uda_id_prints as C ON C.parent_id = A.id where "+condt+" GROUP By A.id"

        
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

        data_new=Handon_form.objects.raw(trans_que,None)
        tot_count=len(list(data_new))
        nd=[]
        res={}
        for datas in data_new:
            nestedData=[]
            hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
            hashid = hashids.encode(datas.Id) 
            off_on_status=datas.off_transaction_status
            if off_on_status==2:
                clname="offstatus"
                clnamet="offstatus"
                off_transaction_id=datas.off_transaction_id
                reg_name="""<div class="mt-1 mt-sm-2 d-block">
                                    <h6 class="mb-0 fs-12 fw-semibold """+clname+"""">Registered By :
                                        <span class="fs-12 """+clnamet+""""> """+datas.registered_name+"""</span>
                                    </h6>
                                </div>"""
            else:
                clname=''
                clnamet='text-muted'
                off_transaction_id=datas.transaction_ref
                reg_name=''
                
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
            ed_split=str(sp_date).split('-')
            t_date=dt.datetime(int(ed_split[0]),int(ed_split[1]),int(ed_split[2]))
            t_date_f="<span class="+clname+">"+t_date.strftime("%m-%d-%Y")+"</span>"
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
            actions="""<div class="btn-group">
                            <button type="button" class="btn fs-15 py-0" data-toggle="dropdown">
                                <i class="fa fa-ellipsis-h "></i>
                            </button>
                            <ul class="dropdown-menu show action-dd" role="menu"
                                data-popper-placement="bottom-end">
                                <li><a class="text-dark view_details" data-method="view" data-id="""+hashid+"""><span
                                            class='avatar avatar-xs brround bg-violet-transparent'><i
                                                class='fa fa-eye'></i></span> View</a></li>
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
            nestedData.append(t_date_f)
            nestedData.append(name_data)
            nestedData.append(practice_info)
            nestedData.append(transactions)
            nestedData.append(transaction_stattuses)
            nestedData.append(browswer_log)
            nestedData.append(actions)
            nd.append(nestedData)

        
        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def delete_spring_transactions(request):
        ids=request.POST.get('id')
        form=Handon_form.objects.get(id=ids)
        form.status=2
        form.deleted_by = request.session['user_id']
        form.deleted_on = dt.datetime.now()
        form.deleted_ip = spring_transactions.get_ip(request)
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}

    def archive_spring_transactions(request):
        ids=request.POST.get('id')
        arch=request.POST.get('arch')
        form=Handon_form.objects.get(id=ids)
        form.archive_id=arch
        form.updated_by = request.session['user_id']
        form.updated_on = dt.datetime.now()
        form.updated_ip = spring_transactions.get_ip(request)
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}


    def export_transaction():
        res=HttpResponse(content_type='text/csv')
        res['Content-Disposition']='attachment; filename="spring_transaction.csv"'
        writer=csv.writer(res)
        writer.writerow(['Date','Name','Practice Name','Email','Phone','Transaction ID','Transaction Date','Payment Mode','Payment Details','Memo','Amount','Status','Browser Log'])
        data=Handon_form.objects.raw("select A.id as Id,A.name,A.created_on,A.last_name,A.practice_name,A.off_transaction_id,A.amount,A.email,A.phone,A.browser,A.os,A.transaction_status,A.transaction_ref,A.archive_id,A.off_transaction_status,A.status,A.created_by,A.off_transaction_payment_mode,A.off_transaction_payment_details,A.off_transaction_created_date,A.off_transaction_memo,B.name as registered_name,C.id,COUNT(C.id) as printcount from admin_uda_handon_form As A LEFT JOIN admin_uda_users as B ON B.id = A.created_by LEFT JOIN admin_uda_id_prints as C ON C.parent_id = A.id where A.status!=2 AND A.form=1 AND A.form_status=2 GROUP By A.id",None)
        payment_modes=["","Cash","Cheque/DD","POS","Venmo","Others"]
        for datas in data:
            sp_date=datas.created_on.date()
            tran_cdate=datas.off_transaction_created_date.date()
            name=datas.name
            payment_mode=payment_modes[int(datas.off_transaction_payment_mode)]
            payment_details=datas.off_transaction_payment_details
            memo=datas.off_transaction_memo
            last_name=datas.last_name
            practice_name=datas.practice_name
            email=datas.email
            phone=datas.phone
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

            ed_split=str(sp_date).split('-')
            t_date=dt.datetime(int(ed_split[0]),int(ed_split[1]),int(ed_split[2]))
            t_date_f=t_date.strftime("%m-%d-%Y")
            tr_da=str(tran_cdate).split('-')
            tran_date=dt.datetime(int(tr_da[0]),int(tr_da[1]),int(tr_da[2]))
            tran_date_f=tran_date.strftime("%m-%d-%Y")
            writer.writerow([t_date_f,name+' '+last_name,practice_name,email,phone,off_transaction_id,tran_date_f,payment_mode,payment_details,memo,amount,transaction_status,os_bro])
        return res