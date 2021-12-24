import json
from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt
from django_mysql.models import GroupConcat
from hashids import Hashids

class convention_id_card_details():
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
    def id_card_details(request,ids):
        ext=0
        result=''
        result_print=''
        hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
        hashid = hashids.decode(ids) 
        Tid=hashid[0]
        input = []
        inWorkShopArr = []
        inConventionArr = []
        Action = 0
        hidden_hand_id = 0
        check_data=Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).exists()
        if check_data:
            all_data=list(Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).values())[0]
            hidden_hand_id = all_data["id"]
            strConvShop=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(con_works=GroupConcat('work_id'))
            strWrkShop=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(hand_works=GroupConcat('work_id'))
            inConventionArr=[]
            inWorkShopArr=[]
            if strConvShop['con_works'] is not None:
                inConventionArr=strConvShop['con_works'].split(',')
            if strWrkShop['hand_works'] is not None:
                inWorkShopArr=strWrkShop['hand_works'].split(',')
            workshopsList=[]
            coventionList=[]
            if inWorkShopArr:
                workshopsList=Handon_workshop.objects.filter(status=1,id__in=inWorkShopArr).order_by('id')
            if inConventionArr:
                coventionList=Convention_types.objects.filter(status=1,id__in=inConventionArr).order_by('id')
            data={}
            if coventionList:
                for conven in coventionList:
                    in_status = 0
                    in_qty = 0
                    in_grand = 0
                    if conven.id:
                        if str(conven.id) in inConventionArr:
                            subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=conven.id)
                            if subrows:
                                for sub in subrows:
                                    if sub.name!='':
                                        index=len(data)
                                        data[index]={}
                                        data[index]['name']=sub.name
                                        data[index]['title']=conven.name.replace("NAME", "")
                                        add_count=Id_prints(con_type=2,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=hidden_hand_id)
                                        add_count.save()
            if workshopsList:
                for work in workshopsList:
                    in_status=0
                    in_qty=0
                    in_grand=0
                    if work.id:
                        subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=work.id)
                        if subrows:
                            in_status=1
                            in_qty = len(subrows)
                    if in_status:
                        for sub in subrows:
                            index=len(data)
                            data[index]={}
                            data[index]['name']=sub.name
                            data[index]['title']=work.name.replace("NAME", "")
                            add_count=Id_prints(con_type=1,ref_id=sub.id,printing_date_time=dt.datetime.now(),parent_id=hidden_hand_id)
                            add_count.save()
            if data:
                it=[]
                con=""
                con_date=""
                if len(data)==1:
                    lastel=data
                    cnt=1
                    sin=0
                elif len(data)%2==0:
                    cnt=2
                    it = iter(data)
                else:
                    cnt=3
                    sin=len(data)-1
                    lastel=data[list(data)[-1]]
                    data.pop(list(data)[-1])      
                    it = iter(data)
               
                if all_data['form_status']==1:
                            con="UDA Convention"
                            con_date="March 26-27, 2020"
                if all_data['form_status']==2:
                    con="Spring Seminar"
                    con_date="April 24, 2020"
                if all_data['form_status']==3:
                    img_src="/static/images/logo-black.png"
                else:
                    img_src="/static/images/head-logo-black.png"
                if cnt==2 or cnt==3:
                    for datas in it:
                        res1=data[datas]
                        res2=data[next(it)]
                        result+=""" <div class="col-lg-12" style='margin-bottom: 25px;'>
                                        <div class='qrCont'>
                                            <div style='border-bottom: 1px solid #ddd;display: flex; justify-content: space-between;'>
                                                <div style='width: 25;'>
                                                    <img class='webViewlogo d-block' src='"""+img_src+"""'
                                                        style='height: 45px;margin: 0 auto 30px;' alt="Logo">
                                                </div>
                                                <div style="width: 25%;">
                                                    <p
                                                        style='font-size: 20px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                                        """+con+"""</p>
                                                    <p style='text-align: right;font-size: 16px;'>"""+con_date+"""</p>
                                                </div>
                                                <div style="width: 50%;">
                                                    <p
                                                        style='font-size: 20px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                                        """+con+"""</p>
                                                    <p style='text-align: right;font-size: 16px;'>"""+con_date+"""</p>
                                                </div>
                                            </div>
                                            <div style="display: flex;">
                                                <div class='mt-2' style="width:50%">
                                                    <div class='text-center'>
                                                        <p class='doc-name text-center mt-4'>"""+convention_id_card_details.transformNameAndTitle(res1)['name']+"""</p>
                                                        <p class='doc-title text-center'>"""+convention_id_card_details.transformNameAndTitle(res1)['title']+"""</p>
                                                    </div>
                                                </div>
                                                <div class='mt-2' style="width:50%">
                                                    <div class='text-center'>
                                                        <p class='doc-name text-center mt-4'>"""+convention_id_card_details.transformNameAndTitle(res2)['name']+"""</p>
                                                        <p class='doc-title text-center'>"""+convention_id_card_details.transformNameAndTitle(res2)['title']+"""</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>"""
                        result_print+="""<tr>
                                            <td class='text-start' style='width: 50%;padding-bottom: 15px; padding-top: 15px;'>
                                                <div class="col-lg-12" style='margin-bottom: 25px;'>
                                                    <div
                                                        style='border-bottom: 1pt solid #ddd;padding-bottom: 0px;display: flex; justify-content: space-between;'>
                                                        <div style='width: 25%;'>
                                                            <img class='webViewlogo d-block' src='"""+img_src+"""'
                                                                style='height: 40px !important;margin: 0 auto 0px;' alt="Logo">
                                                        </div>
                                                        <div style="width: 28%;">
                                                            <p
                                                                style='font-size: 18px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                                                """+con+"""</p>
                                                            <p style='text-align: right;font-size: 14px;'>"""+con_date+"""</p>
                                                        </div>
                                                        <div style="width: 47%;">
                                                            <p
                                                                style='font-size: 18px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                                                """+con+"""</p>
                                                            <p style='text-align: right;font-size: 14px;'>"""+con_date+"""</p>
                                                        </div>
                                                    </div>
                                                    <hr>
                                                    <div style="display: flex;margin-top:30px;">
                                                        <div style="width: 50%;">
                                                            <p
                                                                style='font-size: 20px;text-align: center;margin-bottom: 0;color: #000;font-weight: 600 !important;'>
                                                                """+convention_id_card_details.transformNameAndTitle(res1)['name']+"""
                                                            </p>
                                                            <p style='font-size: 18px;margin-top: 0;color: #000;text-align: center;'>"""+convention_id_card_details.transformNameAndTitle(res1)['title']+"""</p>
                                                        </div>
                                                        <div style="width: 50%;">
                                                            <p
                                                                style='font-size: 20px;text-align: center;margin-bottom: 0;color: #000;font-weight: 600 !important;'>
                                                                """+convention_id_card_details.transformNameAndTitle(res2)['name']+"""
                                                            </p>
                                                            <p style='font-size: 18px;margin-top: 0;color: #000;text-align: center;'>"""+convention_id_card_details.transformNameAndTitle(res2)['title']+"""</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>"""
                if cnt==1 or cnt==3:
                    if cnt==1:
                        res3=lastel[sin]
                    else:
                        res3=lastel
                    result+=""" <div class="col-lg-12" style='margin-bottom: 25px;'>
                                        <div class='qrCont'>
                                            <div style='border-bottom: 1px solid #ddd;display: flex; justify-content: space-between;'>
                                                <div style='width: 25;'>
                                                    <img class='webViewlogo d-block' src='"""+img_src+"""'
                                                        style='height: 45px;margin: 0 auto 30px;' alt="Logo">
                                                </div>
                                                <div style="width: 25%;">
                                                    <p
                                                        style='font-size: 20px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                                        """+con+"""</p>
                                                    <p style='text-align: right;font-size: 16px;'>"""+con_date+"""</p>
                                                </div>
                                            </div>
                                            <div style="display: flex;">
                                                <div class='mt-2' style="width:50%">
                                                    <div class='text-center'>
                                                        <p class='doc-name text-center mt-4'>"""+convention_id_card_details.transformNameAndTitle(res3)['name']+"""</p>
                                                        <p class='doc-title text-center'>"""+convention_id_card_details.transformNameAndTitle(res3)['title']+"""</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>"""
                    result_print+="""<tr>
                    <td class='text-start' style='width: 50%;padding-bottom: 15px; padding-top: 15px;'>
                        <div class="col-lg-12" style='margin-bottom: 25px;'>
                            <div
                                style='border-bottom: 1pt solid #ddd;padding-bottom: 0px;display: flex; justify-content: space-between;'>
                                <div style='width: 25%;'>
                                    <img class='webViewlogo d-block' src='"""+img_src+"""'
                                        style='height: 40px !important;margin: 0 auto 0px;' alt="Logo">
                                </div>
                                <div style="width: 28%;">
                                    <p
                                        style='font-size: 18px; margin-bottom: 0;text-transform: uppercase;font-weight: 700;text-align: right'>
                                        """+con+"""</p>
                                    <p style='text-align: right;font-size: 14px;'>"""+con_date+"""</p>
                                </div>
                            </div>
                            <hr>
                            <div style="display: flex;margin-top:30px;">
                                <div style="width: 50%;">
                                    <p
                                        style='font-size: 20px;text-align: center;margin-bottom: 0;color: #000;font-weight: 600 !important;'>
                                        """+convention_id_card_details.transformNameAndTitle(res3)['name']+"""
                                    </p>
                                    <p style='font-size: 18px;margin-top: 0;color: #000;text-align: center;'>"""+convention_id_card_details.transformNameAndTitle(res3)['title']+"""</p>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>"""
        else:
            ext=1
        return{"data":result,"print":result_print,'ext':ext}


            