import json
from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt
from django_mysql.models import GroupConcat
from hashids import Hashids

class convention_details_pdf():
    def none_to_str(s):
        if s is None:
            return ''
        else:
            return s
    def pdf_transaction_details(hand_id):
        input={}
        table=''
        err=0
        msg=''
        # hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
        # hashid = hashids.decode(ids) 
        # Tid=hashid[0]
        Tid=hand_id
        hidden_hand_id = 0
        total_grand_val=0
        data={}
        check_data=Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).exists()
        if check_data:
            data=list(Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).values())[0]
            input['form_status']=data['form_status']
            hidden_hand_id = data["id"]
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
            today=dt.date.today()
            getPrice=[]
            # set condition for differentiate fall or spring or convention price
            arrPrice=0
            if data['form_status'] is not None and data['form_status']:
                getPrice=Convention_types_prices.objects.filter(form_status=data['form_status'],start_date__lte=today,end_date__gte=today)[0]
                arrPrice = json.loads(getPrice.bulk_price)
            if not getPrice:
                msg='The deadline for all pre-registration is April 11, ' ,today.year
            if data["updated_grand_amount"] is None or data["updated_grand_amount"]=='':
                grand_price = data["amount"]
            else:
                grand_price = data["updated_grand_amount"]
            input['grand_price']=grand_price
            #user and transaction details
            payment_modes=["","Cash","Cheque/DD","POS","Venmo","Others"]
            add=''
            if data['address'] is not None:
                add+=data['address']
            if data['city'] is not None:
                add+=", "+data['city']
            if data['state'] is not None:
                add+=", "+data['state']+"."
            input['full_address']=add
            t_date='-'
            if data['transaction_on'] is not None:
                t_date=data['transaction_on'].strftime("%m/%d/%Y %H:%M:%S %p")
            input['transaction_on']=t_date
            t_date_off='-'
            if data['created_on'] is not None:
                t_date_off=data['created_on'].strftime("%m-%d-%Y")
            if data['off_transaction_status']==1:
                input['transaction_id']=data['transaction_id']
                input['transaction_date']=t_date
                input['transaction_ref']=data["transaction_ref"]
                transaction_status=data["transaction_status"]
                if transaction_status is None:
                    transaction_status='Pending'
                elif transaction_status!='Success':
                    transaction_status='Failed'
                input['transaction_status']=transaction_status
            elif data['off_transaction_status']==2:
                input['transaction_id']=data['off_transaction_id']
                input['transaction_date']=t_date_off
                input["off_transaction_payment_mode"]=payment_modes[int(data["off_transaction_payment_mode"])]
                if data["off_transaction_memo"] is not None:
                    input["off_transaction_memo"]=data["off_transaction_memo"]
                if data["off_transaction_payment_details"] is not None:
                    input["off_transaction_payment_details"]=data["off_transaction_payment_details"]
            #tables
            if data['form_status'] == 1:
                form_head="UDA - Convention Registration"
            elif data['form_status'] == 2:
                form_head="UDA - Spring Registration"
            elif data['form_status'] == 3:
                form_head="UDA - Fall Registration"
            if coventionList:
                table+="""<tr>
                            <td colspan="2">
                                <h4 class='mb-0 text-center py-1'
                                    style='font-size: 22px;color: #000;margin-top: 0px;margin-bottom:0px;padding: 0px;'>
                                    <strong>"""+form_head+"""</strong>
                                </h4>
                            </td>
                        </tr>
                <tr>
                <td colspan='2'>
                    <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 0px;border: 0.5px solid #ababab;padding: 0px;"
                        class="table-bordered table tablelist">
                        <thead>
                            <tr style="border: 0.5px #ddd;">
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>SL
                                        NO</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>NAME</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>EMAIL</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>ADA Number</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>Fee</strong>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="pnt">"""
                for conven in coventionList:
                    in_status=0
                    in_qty=0
                    in_grand=0
                    if conven.id:
                        if str(conven.id) in inConventionArr:
                            subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=conven.id)
                            if subrows:
                                in_status=1
                                in_qty=len(subrows)
                                for sub in subrows:
                                    if sub.updated_price is None or sub.updated_price=='':
                                        in_grand+=int(sub.price)
                                    else:
                                        in_grand+=int(sub.updated_price)
                                total_grand_val+=in_grand
                                table+="""<tr style="border: 0.5px #ddd;">
                                            <td colspan="5" class="for-blue"
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                """+conven.name.replace("NAME", "")+' ($'+str(arrPrice[str(conven.id)])+""")</td>
                                        </tr>"""
                        if conven.id in [1, 2, 5, 15, 18, 19, 20, 22, 23, 24] and in_status:
                                x=1
                                sub_total=0
                                p=0
                                for sub in subrows:
                                    if sub.updated_price is None or sub.updated_price=='':
                                        p=int(sub.price)
                                    else:
                                        p=int(sub.updated_price)
                                    sub_total+=p
                                    table+="""<tr class="adj" style="border: 0.5px #ddd;">
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+str(x)+"""</td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+convention_details_pdf.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;'>
                                        """+convention_details_pdf.none_to_str(sub.email)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+convention_details_pdf.none_to_str(sub.ada)+"""</td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        $"""+str(p)+"""</td>
                                </tr>"""
                                    x+=1
                                table+="""<tr style="border: 0.5px #ddd">
                                            <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                                colspan="3">
                                            </td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                Total</td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                $"""+str(sub_total)+"""</td>
                                        </tr>"""
                        elif conven.id in [3, 4, 6, 7, 9, 11, 12, 13, 14, 16, 17, 21, 25, 26] and in_status:
                            x=1
                            sub_total=0
                            p=0
                            for sub in subrows:
                                sub_total+=int(sub.price)
                                if sub.name!='':
                                    if sub.updated_price is None or sub.updated_price=='':
                                        p=int(sub.price)
                                    else:
                                        p=int(sub.updated_price)
                                    table+="""<tr class="adj" style="border: 0.5px #ddd;">
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+str(x)+"""</td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+convention_details_pdf.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;' colspan="2">
                                        """+convention_details_pdf.none_to_str(sub.email)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        $"""+str(p)+"""</td>
                                </tr>"""
                                x+=1
                            table+="""<tr style="border: 0.5px #ddd">
                                            <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                                colspan="3">
                                            </td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                Total</td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                $"""+str(sub_total)+"""</td>
                                        </tr>"""
                        elif conven.id in [8] and in_status:
                                    x=1
                                    sub_total=0
                                    for sub in subrows:
                                        if sub.updated_price is None or sub.updated_price=='':
                                            p=int(sub.price)
                                        else:
                                            p=int(sub.updated_price)
                                        sub_total+=p
                                        table+="""<tr class="adj" style="border: 0.5px #ddd;">
                                                    <td
                                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                        """+str(x)+"""</td>
                                                    <td
                                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important; ' colspan="3">
                                                        """+convention_details_pdf.none_to_str(sub.name)+""" ("""+convention_details_pdf.none_to_str(sub.ada)+""")
                                                    </td>
                                                    <td
                                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                        $"""+str(p)+"""</td>
                                                </tr>"""
                                        x+=1
                                    table+="""<tr style="border: 0.5px #ddd">
                                            <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                                colspan="3">
                                            </td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                Total</td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                $"""+str(sub_total)+"""</td>
                                        </tr>"""
                table+="""<tr style="border: 0.5px #ddd;">
                                <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                    colspan="3">
                                </td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    TOTAL</td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    $"""+str(data["amount"])+"""</td>
                            </tr>"""
                if data["updated_grand_amount"] is None or data["updated_grand_amount"]=='':
                    pass
                else:
                    table+="""<tr style="border: 0.5px #ddd;">
                                <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                    colspan="3">
                                </td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    TOTAL</td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    $"""+str(data["updated_grand_amount"])+"""</td>
                            </tr>"""
                    balance = data['amount'] - data['updated_grand_amount']
                    if balance > 0:
                        m="UDA to pay"
                        a=balance
                    else:
                        m="User to pay"
                        a=balance*-1
                        table+="""<tr style="border: 0.5px #ddd;">
                                <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                    colspan="3">
                                </td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    """+m+"""</td>
                                <td
                                    style="font-family: Nunito, sans-serif;font-size: 15px;padding: 5px;font-weight:600;border-bottom: 1px solid #eaedf1;border: 1px solid #ddd !important;">
                                    $"""+str(a)+"""</td>
                            </tr>"""
                table+='</tbody></table></td></tr>'
            if workshopsList:     
                table+="""<tr>
                            <td colspan="2">
                                <h4 class='mb-0 text-center py-1'
                                    style='font-size: 22px;color: #000;margin-top: 0px;margin-bottom:0px;padding: 0px;'>
                                    <strong>UDA - Hands on workshop Registration</strong>
                                </h4>
                            </td>
                        </tr>
                <tr>
                <td colspan='2'>
                    <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 0px;border: 0.5px solid #ababab"
                        class="table-bordered table tablelist">
                        <thead>
                            <tr style="border: 0.5px #ddd;">
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>SL
                                        NO</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>NAME</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>EMAIL</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>MOBILE</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-family: Nunito, sans-serif;font-size: 15px;margin-bottom: 0px;margin-top: 0px;padding: 5px; color: #000; border: 1px solid #ddd !important;background: #7164d530 !important;color: #454545;'>
                                    <strong>Fee</strong>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="pnt">"""
                for work in workshopsList:
                    in_status=0
                    in_qty=0
                    in_grand=0
                    subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=work.id)
                    if subrows:
                        in_status=1
                        in_qty=len(subrows)
                        for sub in subrows:
                            if sub.updated_price is None or sub.updated_price=='':
                                in_grand+=int(sub.amount)
                            else:
                                in_grand+=int(sub.updated_price)
                        total_grand_val+=in_grand
                    table+="""<tr style="border: 0.5px #ddd;">
                                            <td colspan="5" class="for-blue"
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                """+convention_details_pdf.none_to_str(work.name)+'($'+ str(work.amount)+""")</td>
                                        </tr>""" 
                    if in_status:
                        x=1
                        sub_total=0
                        for sub in subrows:
                            if sub.updated_price is None or sub.updated_price=='':
                                p=int(sub.amount)
                            else:
                                p=int(sub.updated_price)
                            sub_total+=p
                            table+="""<tr class="adj" style="border: 0.5px #ddd;">
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+str(x)+"""</td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+convention_details_pdf.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;'>
                                        """+convention_details_pdf.none_to_str(sub.email)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+convention_details_pdf.none_to_str(sub.mobile)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        $"""+str(p)+"""</td>
                                </tr>"""
                            x+=1
                        table+="""<tr style="border: 0.5px #ddd">
                                            <td style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'
                                                colspan="3">
                                            </td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                Total</td>
                                            <td
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                $"""+str(sub_total)+"""</td>
                                        </tr>"""
                table+='</tbody></table></td></tr>'
                                                        
        else:
            err=1
       
        return {"input":input,"con_datas":table,"err":err,"msg":msg,"all_data":data}
