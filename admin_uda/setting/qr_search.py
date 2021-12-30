from django.db.models.aggregates import Count
from admin_uda.models import *
import datetime as dt
from hashids import Hashids

class qr_search_list():
    def list_registered_name(request):
        if request.POST.get('keyword'):
            records=''
            status_res=0
            name=request.POST.get('keyword')
            data=Handon_form_workshop.objects.annotate(dcount=Count('id')).select_related('hand_id','work_id').filter(hand_id__archive_id=0,hand_id__status=1,work_id__status=1)
            if name:
                data=data.filter(name__icontains=name)
            resultval=[]
            if data:
                status_res=1
                group={}
                for groupNames in data:
                    group['userid']=groupNames.id
                    group['id']=groupNames.work_id.id
                    group['name']=groupNames.work_id.name
                    group['usertype']='Workshop'
                    group['usertype_id']=1
                    resultval.append(group)
                    records+="<tr><td style='padding: 10px;'>Workshop</td><td style='padding: 10px;'>"+groupNames.work_id.name+"</td></tr>"
            # FOR convention workshop
            getAllUsers_con=Convention_form_workshop.objects.raw("SELECT A.*,B.id as bid,C.id as cid,C.name AS workshop_name FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id AND B.archive_id=0 AND B.status=1 LEFT JOIN admin_uda_convention_types AS C ON C.id=A.work_id AND C.status=1 WHERE A.name LIKE '%"+name+ "%' GROUP BY A.id",None)
            if getAllUsers_con:
                status_res=1
                groupCon={}
                for groupNames_con in getAllUsers_con:
                    groupCon['userid']=groupNames_con.id
                    groupCon['id']=groupNames_con.work_id
                    groupCon['name']=groupNames_con.workshop_name
                    groupCon['usertype']='Convention'
                    groupCon['usertype_id']=2
                    resultval.append(groupCon)
                    records+="<tr><td style='padding: 10px;'>Convention</td><td style='padding: 10px;'>"+groupNames_con.workshop_name+"</td></tr>"
            # For Exhibitor Staffs
            getAllUsers_exh=Vendor_employees.objects.raw("SELECT ve.id, vrf.company_name, vrf.id AS vid FROM admin_uda_vendor_employees AS ve LEFT JOIN admin_uda_vendor_registration_form AS vrf ON vrf.id=ve.vendor_id WHERE ve.name LIKE '%"+name+ "%' GROUP BY ve.id",None)
            if getAllUsers_exh:
                status_res=1
                groupExh={}
                for groupNames_exh in getAllUsers_exh:
                    groupExh['userid']=groupNames_exh.id
                    groupExh['id']=groupNames_exh.vid
                    groupExh['name']=groupNames_exh.company_name
                    groupExh['usertype']='Exhibitor'
                    groupExh['usertype_id']=3
                    resultval.append(groupExh)
                    records+="<tr><td style='padding: 10px;'>Exhibitor</td><td style='padding: 10px;'>"+groupNames_exh.company_name+"</td></tr>"
        return {"res":status_res,"records":records}

    def list_registered_name_qr(request,ids,types):
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
                getAllUsers_con=Convention_form_workshop.objects.raw("SELECT A.*,B.id as bid,C.id as cid,C.name AS workshop_name FROM admin_uda_convention_form_workshop AS A JOIN admin_uda_handon_form AS B ON A.hand_id=B.id AND B.archive_id=0 AND B.status=1 LEFT JOIN admin_uda_convention_types AS C ON C.id=A.work_id AND C.status=1 WHERE A.id='"+dec_con_id+"' AND A.hand_id='"+hidden_hand_id+"' GROUP BY A.id",None)
                if getAllUsers_con:
                    status_res=1
                    groupCon={}
                    for groupNames_con in getAllUsers_con:
                        groupCon['userid']=groupNames_con.id
                        groupCon['id']=groupNames_con.work_id
                        groupCon['name']=groupNames_con.workshop_name
                        groupCon['usertype']='Convention'
                        groupCon['usertype_id']=2
                        resultval.append(groupCon)
                        records+="<tr><td style='padding: 10px;'>Convention</td><td style='padding: 10px;'>"+groupNames_con.workshop_name+"</td></tr>"
            if cfw_hfw[0]=='hfw':
                work_id=cfw_hfw[1]
                hashidwork = hashids.decode(work_id) 
                dec_work_id=hashidwork[0]
                data=Handon_form_workshop.objects.annotate(dcount=Count('id')).select_related('hand_id','work_id').filter(hand_id__archive_id=0,hand_id__status=1,work_id__status=1,id=dec_work_id,hand_id=hidden_hand_id)
                if data:
                    status_res=1
                    group={}
                    for groupNames in data:
                        group['userid']=groupNames.id
                        group['id']=groupNames.work_id.id
                        group['name']=groupNames.work_id.name
                        group['usertype']='Workshop'
                        group['usertype_id']=1
                        resultval.append(group)
                        records+="<tr><td style='padding: 10px;'>Workshop</td><td style='padding: 10px;'>"+groupNames.work_id.name+"</td></tr>"
        return {"res":status_res,"records":records}

