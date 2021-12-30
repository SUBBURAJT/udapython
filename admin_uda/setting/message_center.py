from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt

class message_centers():
    def list_message_center(request):
        tot_count=Message_center.objects.filter(status=0).count()
        qry=Message_center.objects.filter(status=0)
        nd=[]
        res={}
        reg_cat=["All","Convention Registration","Spring Registration","Fall Registration"]
        j=0
        for datas in qry:
            sent_co=Message_center_ref.objects.exclude(message_id__isnull=True).exclude(message_id__exact='').filter(ref_id=datas.id).aggregate(tot=Count('id'))
            not_sent_co=Message_center_ref.objects.filter(Q(message_id__isnull=True)|Q(message_id__exact=''),ref_id=datas.id).aggregate(newtot=Count('id'))
            del_not_del=str(sent_co['tot']),' Delivered / '+str(not_sent_co['newtot'])+' Not delivered'
            c_date=''
            if datas.created_on:
                c_date=datas.created_on.strftime("%m-%d-%Y %H:%M %p")

            nestedData=[]
            nestedData.append(c_date)
            nestedData.append(reg_cat[datas.reg_type])
            nestedData.append(datas.message)
            nestedData.append(del_not_del)
            actions="""<span class="view_msg" data-id="""+str(datas.id)+""" data-msg="""+datas.message+""">
                            <a href="javascript:void(0);" class="me-3 text-primary"
                                data-bs-container="#tooltip-container"""+str(j)+""""  data-bs-toggle="tooltip"
                                data-bs-placement="top" title="View">
                            <i class="mdi mdi-eye font-size-18"></i></a></span>
                        <a href="javascript:void(0);" data-id="""+str(datas.id)+""" class="text-danger tabDelete"
                            data-bs-container="#tooltip-container"""+str(j)+"""" data-bs-toggle="tooltip"
                            data-bs-placement="top" title="Delete"><i
                                class="mdi mdi-trash-can font-size-18"></i>
                        </a>"""
            nestedData.append(actions)
            nd.append(nestedData)
            j+=1
        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

    def type_of_members(request):
        category=request.POST.get('category')
        data=Convention_types.objects.filter(status=1,form_status=int(category)).order_by('name')
        opt="<option value='0'>All</option>"
        for datas in data:
            opt+="<option value='"+str(datas.id)+"'>"+datas.name.replace("NAME", "")+"</option>"
        return opt

    def member_names(request):
        memnames=request.POST.get('memnames')
        data=Convention_form_workshop.objects.raw("SELECT A.id,A.name FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id WHERE 1=1 AND A.is_deleted=1 AND B.status=1 AND A.work_id="+memnames+" ORDER BY A.name")
        opt="<option value='0'>All</option>"
        for datas in data:
            opt+="<option value='"+str(datas.id)+"'>"+datas.name+"</option>"
        return opt

    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def add_messages(request):
        members=request.POST.getlist('memnames')
        ids=','.join(members)
        reg_type=request.POST.get('category')
        type_of_member=request.POST.get('typeofmem')
        message=request.POST.get('message')
        form=Message_center()
        form.message=message
        form.reg_type=reg_type
        form.type_of_member=type_of_member
        form.uni_con_id=ids
        form.created_by=request.session['user_id']
        form.created_on=dt.datetime.now()
        form.created_ip=message_centers.get_ip(request)
        form.save()
        res=form.id
        if res > 0:
            error=''
            if '0' not in members:
                get_datas = Convention_form_workshop.objects.raw("SELECT A.id,A.name,B.id as h_id,B.phone FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id WHERE A.is_deleted=1 AND B.status=1 AND A.id IN ("+ids+")")
                 #trigger to selected user
            elif int(type_of_member) > 0:
                get_datas = Convention_form_workshop.objects.raw("SELECT A.id,A.name,B.id as h_id,B.phone FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id WHERE A.is_deleted=1 AND B.status=1 AND A.work_id='"+(type_of_member)+"'")#trigger to multiple user based on Member type choosen
            else:
                get_datas = Convention_form_workshop.objects.raw("SELECT B.id,B.phone,0 AS uni_con_id FROM admin_uda_handon_form AS B WHERE B.status=1 AND B.form_status='"+reg_type+"'")
                #trigger to all based on registration type
            arr=[]
            for da in get_datas:
                form_ref=Message_center_ref()
                form_ref.ref_id=res
                form_ref.number=da.phone
                form_ref.uni_con_id=da.id
                form_ref.triggered_status=0
                form_ref.save()
                if form_ref.id > 0:
                    arr.append(form_ref.id)
            if arr:
                msg="Message Add to Queue"
            else:
                error="Message Not Added"
        else:
            error="Message Not Added"
            msg=""
        return {"error":error,"msg":msg}

    def delete_message(request):
        ids=request.POST.get('id')
        form=Message_center.objects.get(id=ids)
        form.status=1
        form.deleted_by = request.session['user_id']
        form.deleted_on = dt.datetime.now()
        form.deleted_ip = message_centers.get_ip(request)
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}

    def view_msgs(request):
        nd=[]
        res={}
        tot_count=0
        ref_id=request.POST.get('ref_id')
        start=request.POST.get('start')
        length=request.POST.get('length')
        order=request.POST.get("order[0][column]")
        as_de=request.POST.get("order[0][dir]")
        search_val=request.POST.get("search[value]")
        search_on=request.POST.get("search_on")
        column = ['C.name','B.number','D.`name`','B.triggered_time','B.message_id']
        if ref_id:
            cond=''
            if search_on!='':
                cond+=' AND ('+search_on+' LIKE "%' + search_val + '%")'
            elif search_val!='':
                cond+=' AND (B.number LIKE "%' +search_val+ '%" OR C.name LIKE "%' +search_val+ '%" OR D.name LIKE "%' +search_val+ '%" OR B.triggered_time LIKE "%' +search_val+ '%")'

            qry="SELECT A.id as m_id,B.id,B.number,B.triggered_time,B.message_id,C.`name`,D.`name` AS reg_type FROM admin_uda_message_center AS A JOIN admin_uda_message_center_ref AS B ON A.id=B.ref_id JOIN admin_uda_convention_form_workshop AS C ON B.uni_con_id=C.id JOIN admin_uda_convention_types AS D ON D.id=C.work_id WHERE A.status=0 AND B.ref_id="+ref_id+cond+" ORDER BY "+column[int(order)] + " "+as_de
            data_tot=Message_center.objects.raw(qry,None)
            tot_count=len(list(data_tot))
            if length!="-1":
                qry+=" LIMIT "+start+" , "+length
            data=Message_center.objects.raw(qry,None)
            cl_names=["bg-soft-primary text-primary","bg-soft-success text-success","bg-soft-warning text-warning"]
            j=0
            for datas in data:
                nestedData=[]
                name="""<div class="d-flex align-items-center">
                        <div class="activity-icon avatar-xs me-2">
                            <span class="avatar-title """+cl_names[(j%3)]+""" br-5">J</span>
                        </div>
                        """+datas.name+"""
                    </div>"""
                p_number=datas.number
                reg_type=datas.reg_type
                c_date='-'
                if datas.triggered_time:
                    c_date=datas.triggered_time.strftime("%m-%d-%Y %H:%M %p")
                if datas.message_id=='':
                    st="Delivered"
                    cl="text-success"
                else:
                    st="Not Triggered"
                    cl="text-danger"
                status="""<div class="d-flex align-items-center"><i
                                class='fa fa-circle me-2 fs-10 mt-1 """+cl+"""'></i>"""+st+"""
                        </div>"""
                nestedData.append(name)
                nestedData.append(p_number)
                nestedData.append(reg_type)
                nestedData.append(c_date)
                nestedData.append(status)
                nd.append(nestedData)
                j+=1
        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

