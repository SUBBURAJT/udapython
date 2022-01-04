from django.db.models.aggregates import Count
from admin_uda.models import Handon_form_workshop,Convention_form_workshop,Vendor_employees
from hashids import Hashids

class qr_search_list:
    def list_registered_name(self,request):
        if request.POST.get('keyword'):
            records=''
            status_res=0
            name=request.POST.get('keyword')
            data=Handon_form_workshop.objects.annotate(dcount=Count('id')).select_related('hand_id','work_id').filter(hand_id__archive_id=0,hand_id__status=1,work_id__status=1)
            if name:
                data=data.filter(name__icontains=name)
            resultval=[]
            group={}
            for group_names in data:
                group['userid']=group_names.id
                group['id']=group_names.work_id.id
                group['name']=group_names.work_id.name
                group['usertype']='Workshop'
                group['usertype_id']=1
                resultval.append(group)
                records+="<tr><td style='padding: 10px;'>Workshop</td><td style='padding: 10px;'>"+group_names.work_id.name+"</td></tr>"
                status_res=1
            # FOR convention workshop
            get_all_users_con=Convention_form_workshop.objects.raw("SELECT A.*,B.id as bid,C.id as cid,C.name AS workshop_name FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id AND B.archive_id=0 AND B.status=1 LEFT JOIN admin_uda_convention_types AS C ON C.id=A.work_id AND C.status=1 WHERE A.name LIKE '%"+name+ "%' GROUP BY A.id",None)
            groupcon={}
            for groupnames_con in get_all_users_con:
                groupcon['userid']=groupnames_con.id
                groupcon['id']=groupnames_con.work_id
                groupcon['name']=groupnames_con.workshop_name
                groupcon['usertype']='Convention'
                groupcon['usertype_id']=2
                resultval.append(groupcon)
                records+="<tr><td style='padding: 10px;'>Convention</td><td style='padding: 10px;'>"+groupnames_con.workshop_name+"</td></tr>"
                status_res=1
            # For Exhibitor Staffs
            get_all_users_exh=Vendor_employees.objects.raw("SELECT ve.id, vrf.company_name, vrf.id AS vid FROM admin_uda_vendor_employees AS ve LEFT JOIN admin_uda_vendor_registration_form AS vrf ON vrf.id=ve.vendor_id WHERE ve.name LIKE '%"+name+ "%' GROUP BY ve.id",None)
            group_exh={}
            for groupnames_exh in get_all_users_exh:
                group_exh['userid']=groupnames_exh.id
                group_exh['id']=groupnames_exh.vid
                group_exh['name']=groupnames_exh.company_name
                group_exh['usertype']='Exhibitor'
                group_exh['usertype_id']=3
                resultval.append(group_exh)
                records+="<tr><td style='padding: 10px;'>Exhibitor</td><td style='padding: 10px;'>"+groupnames_exh.company_name+"</td></tr>"
                status_res=1
        return {"res":status_res,"records":records}

    def list_registered_name_qr(self,request,ids,types):
        status_res=0
        records=''
        if ids and types:
            hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
            hashid = hashids.decode(ids) 
            hidden_hand_id=hashid[0]
            resultval=[]
            cfw_hfw=types.split('-')
            if cfw_hfw[0]=='cfw':
                con_id=cfw_hfw[1]
                hashidcon = hashids.decode(con_id) 
                dec_con_id=hashidcon[0]
                get_all_users_con=Convention_form_workshop.objects.raw("SELECT A.*,B.id as bid,C.id as cid,C.name AS workshop_name FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id AND B.archive_id=0 AND B.status=1 LEFT JOIN admin_uda_convention_types AS C ON C.id=A.work_id AND C.status=1 WHERE A.id='"+dec_con_id+"' AND A.hand_id='"+hidden_hand_id+"' GROUP BY A.id",None)
                groupcon={}
                for groupnames_con in get_all_users_con:
                    groupcon['userid']=groupnames_con.id
                    groupcon['id']=groupnames_con.work_id
                    groupcon['name']=groupnames_con.workshop_name
                    groupcon['usertype']='Convention'
                    groupcon['usertype_id']=2
                    resultval.append(groupcon)
                    records+="<tr><td style='padding: 10px;'>Convention</td><td style='padding: 10px;'>"+groupnames_con.workshop_name+"</td></tr>"
                    status_res=1
            if cfw_hfw[0]=='hfw':
                work_id=cfw_hfw[1]
                hashidwork = hashids.decode(work_id) 
                dec_work_id=hashidwork[0]
                data=Handon_form_workshop.objects.annotate(dcount=Count('id')).select_related('hand_id','work_id').filter(hand_id__archive_id=0,hand_id__status=1,work_id__status=1,id=dec_work_id,hand_id=hidden_hand_id)
                group={}
                for groupnames in data:
                    group['userid']=groupnames.id
                    group['id']=groupnames.work_id.id
                    group['name']=groupnames.work_id.name
                    group['usertype']='Workshop'
                    group['usertype_id']=1
                    resultval.append(group)
                    records+="<tr><td style='padding: 10px;'>Workshop</td><td style='padding: 10px;'>"+groupnames.work_id.name+"</td></tr>"
                    status_res=1
        return {"res":status_res,"records":records}

