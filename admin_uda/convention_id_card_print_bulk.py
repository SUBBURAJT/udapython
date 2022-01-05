from admin_uda.models import Handon_form,Convention_form_workshop,Handon_form_workshop,Convention_types,Handon_workshop,Id_prints
import datetime as dt

class convention_id_card_bulk_details:
    def transform_name_title(self,record):
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
    def id_card_details_bulk(self,request):
        ext=0
        result_print=''
        conventionidss=request.POST.getlist('name_tag_print')
        in_workshop_arr = []
        in_convention_arr = []
        covention_list=[]
        workshops_list=[]
        data={}
        if conventionidss:
            check_data=Handon_form.objects.filter(form=1,id__in=conventionidss).exclude(status=2).exists()
            if check_data:
                check_datas=Handon_form.objects.filter(form=1,id__in=conventionidss).exclude(status=2)
                str_con=Convention_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss).values('work_id')
                if str_con:
                    for ids in str_con:
                        in_convention_arr.append(ids['work_id'])
                str_wor=Handon_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss).values('work_id')
                if str_wor:
                    for ids in str_wor:
                        in_workshop_arr.append(ids['work_id'])
                if in_convention_arr:
                    covention_list=Convention_types.objects.filter(status=1,id__in=in_convention_arr).order_by('id')
                if in_workshop_arr:
                    workshops_list=Handon_workshop.objects.filter(status=1,id__in=in_workshop_arr).order_by('id')
                if covention_list:
                    for conven in covention_list:
                        if conven.id in in_convention_arr:
                            subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss,work_id=conven.id)
                            for sub in subrows:
                                if sub.name!='':
                                    index=len(data)
                                    data[index]={}
                                    data[index]['id']=sub.hand_id
                                    record=self.transform_name_title({"name":sub.name,'title':conven.name.replace("NAME", "")})
                                    data[index]['name']=record['name']
                                    data[index]['title']=record['title']
                                    add_count=Id_prints(con_type=2,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=sub.hand_id)
                                    add_count.save()
                if workshops_list:
                    for work in workshops_list:
                        in_status=0
                        subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id__in=conventionidss,work_id=work.id)
                        if subrows:
                            in_status=1
                        if in_status:
                            for sub in subrows:
                                index=len(data)
                                data[index]={}
                                data[index]['id']=sub.hand_id
                                record=self.transform_name_title({"name":sub.name,'title':work.name})
                                data[index]['name']=record['name']
                                data[index]['title']=record['title']
                                add_count=Id_prints(con_type=1,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=sub.hand_id)
                                add_count.save()
            else:
                ext=1
        else:
            ext=1
        return{"data":data,"print":result_print,'ext':ext}


            