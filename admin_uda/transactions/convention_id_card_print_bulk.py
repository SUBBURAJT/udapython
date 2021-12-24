import json
from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt
from django_mysql.models import GroupConcat

class convention_id_card_bulk_details():
    def transformNameAndTitle(record):
        res={}
        name=record['name'].strip().lower()
        title=record['title'].strip().upper()
        if title[0:18]=='UDA MEMBER DENTIST' or title[0:31]=='OUT-OF-STATE ADA MEMBER DENTIST' or title[0:19]=='NON-UDA/ADA DENTIST' or title[0:21]=='FULLY RETIRED DENTIST':
            res['name']="Dr. "+name
            res['title']=""
        elif title[0:31]=='SPOUSE OF FULLY RETIRED DENTIST' or title[0:17]=='SPOUSE OF DENTIST' or title[0:44]=='ALLIANCE LUNCHEON (SPOUSE OF DENTAL STUDENT)':
            res['name']=name
            res['title']='SPOUSE'
        elif title[0:11]=='STUDENT (S)' or title[0:30]=='DENTAL STUDENT LUNCH AND LEARN':
            res['name']=name
            res['title']='STUDENT'
        elif title[0:46]=='STAFF DOES NOT NEED TO REGISTER WITH A DENTIST' or title[0:13]=='TEAM LUNCHEON' or title[0:43]=='ALLIANCE LUNCHEON GUEST/NON-ALLIANCE MEMBER':
            res['name']=name
            res['title']='ASSISTANT'
        elif title[0:37]=='UDA DENTAL HYGIENIST AFFILIATE MEMBER' or title[0:27]=='NON-UDA AFFILIATE HYGIENIST' or title[0:29]=='AFFILIATE HYGIENIST BREAKFAST':
            res['name']=name
            res['title']='HYGIENIST'
        else:
            res['name']=name
            res['title']=title
        return res
    def id_card_details_bulk(request):
        ext=0
        result=''
        result_print=''
        conventionidss=request.POST.getlist('name_tag_print')
        inWorkShopArr = []
        inConventionArr = []
        coventionList=[]
        workshopsList=[]
        data={}
        if conventionidss:
            check_data=Handon_form.objects.filter(form=1,id__in=conventionidss).exclude(status=2).exists()
            if check_data:
                check_datas=Handon_form.objects.filter(form=1,id__in=conventionidss).exclude(status=2)
                strCon=Convention_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss).values('work_id')
                if strCon:
                    for ids in strCon:
                        inConventionArr.append(ids['work_id'])
                strWor=Handon_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss).values('work_id')
                if strWor:
                    for ids in strWor:
                        inWorkShopArr.append(ids['work_id'])
                if inConventionArr:
                    coventionList=Convention_types.objects.filter(status=1,id__in=inConventionArr).order_by('id')
                if inWorkShopArr:
                    workshopsList=Handon_workshop.objects.filter(status=1,id__in=inWorkShopArr).order_by('id')
                if coventionList:
                    for conven in coventionList:
                        if conven.id in inConventionArr:
                            subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss,work_id=conven.id)
                            for sub in subrows:
                                if sub.name!='':
                                    index=len(data)
                                    data[index]={}
                                    data[index]['id']=sub.hand_id
                                    record=convention_id_card_bulk_details.transformNameAndTitle({"name":sub.name,'title':conven.name.replace("NAME", "")})
                                    data[index]['name']=record['name']
                                    data[index]['title']=record['title']
                                    add_count=Id_prints(con_type=2,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=sub.hand_id)
                                    add_count.save()
                if workshopsList:
                    for work in workshopsList:
                        in_status=0
                        subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss,work_id=work.id)
                        if subrows:
                            in_status=1
                            in_qty=len(subrows)
                        if in_status:
                            for sub in subrows:
                                index=len(data)
                                data[index]={}
                                data[index]['id']=sub.hand_id
                                record=convention_id_card_bulk_details.transformNameAndTitle({"name":sub.name,'title':work.name})
                                data[index]['name']=record['name']
                                data[index]['title']=record['title']
                                add_count=Id_prints(con_type=1,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=sub.hand_id)
                                add_count.save()
            else:
                ext=1
        else:
            ext=1
        return{"data":data,"print":result_print,'ext':ext}


            