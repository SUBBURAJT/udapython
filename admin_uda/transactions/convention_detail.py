import json
from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
import datetime as dt
from django_mysql.models import GroupConcat
from hashids import Hashids

class convention_details():
    def view_transaction_details(request,ids,method):
        if method=='print':
            colspan='4'
            pri_head='<th class="bg-color text-uppercase"><strong>No. 123 of Prints</strong></th>'
            pri_head_p='<th class="bg-color text-uppercase" style="font-size: 15px; color: #000; border-color: #ddd !important;"><strong>No.of Prints</strong></th>'
        else:
            colspan='3'
            pri_head=''
            pri_head_p=''
        hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
        hashid = hashids.decode(ids) 
        Tid=hashid[0]
        input = {}
        inWorkShopArr = []
        inConventionArr = []
        Action = 0
        hidden_hand_id = 0
        err=0
        msg=''
        check_data=Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).exists()
        if check_data:
            data=list(Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).values())[0]
            input['name']=data["name"]
            input['lname']=data["last_name"]
            input['phone']=data["phone"]
            input['email']=data["email"]
            input['address']=data["address"]
            input['state']=data["state"]
            input['city']=data["city"]
            input['zipcode']=data["zipcode"]
            input['form_status']=data['form_status']
            input['practice_name']=data['practice_name']
            input['off_transaction_status']=data['off_transaction_status']
            input['methods']=method
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
            total_grand_val=0
            reg_type_val_tr=''
            reg_type_val_trp=''
            input['contab1']=0
            input['contab2']=0
            if inWorkShopArr:
                workshopsList=Handon_workshop.objects.filter(status=1,id__in=inWorkShopArr).order_by('id')
                input['contab1']=1
            if inConventionArr:
                coventionList=Convention_types.objects.filter(status=1,id__in=inConventionArr).order_by('id')
                input['contab2']=1

            if data['form_status'] == 1:
                form_head="UDA - Convention Registration"
            elif data['form_status'] == 2:
                form_head="UDA - Spring Registration"
            elif data['form_status'] == 3:
                form_head="UDA - Fall Registration"

            if coventionList:
                reg_type_val_tr+="""<tr>
                                        <td colspan="2">
                                        <h4 class='mb-0 mt-4 text-lg-center py-1'><strong>"""+form_head+"""</strong></h4>
                                        </td>
                                    </tr>"""
                reg_type_val_tr+="""<tr>
                                    <td colspan='2'>
                                        <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 10px;"
                                            class="table-bordered table">
                                            <thead>
                                                <tr>
                                                    <th class='bg-color text-uppercase'><strong>SL NO</strong></th>
                                                    """+pri_head+"""
                                                    <th class='bg-color text-uppercase'><strong>NAME</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>EMAIL</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>ADA Number</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>Fee</strong></th>
                                                </tr>
                                            </thead>
                                            <tbody class="pnt">"""
                reg_type_val_trp+="""<tr>
                                        <td colspan="2">
                                            <h4 class='mb-0 text-center py-1'
                                                style='font-size: 22px;color: #000;margin-top: 25px;margin-bottom:25px;'>
                                                <strong>
                                                    """+form_head+"""
                                                </strong>
                                            </h4>
                                        </td>
                                    </tr>"""
                reg_type_val_trp+=""" <tr>
                <td colspan='2'>
                    <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 10px;"
                        class="table-bordered table">
                        <thead>
                            <tr>
                                <th class='bg-color text-uppercase'
                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'><strong>SL
                                        NO</strong></th>
                                """+pri_head_p+"""
                                <th class='bg-color text-uppercase'
                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
                                    <strong>NAME</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
                                    <strong>EMAIL</strong>
                                </th>
                                <th class='bg-color text-uppercase'
                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'><strong>ADA
                                        Number</strong></th>
                                <th class='bg-color text-uppercase'
                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
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
                                #view
                                reg_type_val_tr+='<tr><td colspan="6" class="for-blue">'+conven.name+' ($'+str(arrPrice[str(conven.id)])+')</td></tr>'
                                #print
                                reg_type_val_trp+='<tr><td colspan="6" class="for-blue" style="font-size: 15px; border-color: #ddd !important;">'+conven.name+' ($'+str(arrPrice[str(conven.id)])+')</td></tr>'
                            if conven.id in [1, 2, 5, 15, 18, 19, 20, 22, 23, 24] and in_status:
                                x=1
                                sub_total=0
                                for sub in subrows:
                                    print_count=Id_prints.objects.filter(con_type=2,ref_id=sub.id).aggregate(print=Count(id))
                                    if sub.updated_price is None or sub.updated_price=='':
                                        p=int(sub.price)
                                    else:
                                        p=int(sub.updated_price)
                                    sub_total+=p
                                    if method=='print':
                                        pri_cond='<td>'+str(print_count['print'])+'</td>'
                                        pri_cond1='<td style="font-size: 15px; border-color: #ddd !important;">'+str(print_count['print'])+'</td>'
                                    else:
                                        pri_cond=''
                                        pri_cond1=''
                                    #view
                                    reg_type_val_tr+="""<tr class="adj">
                                                            <td>"""+str(x)+"""</td>
                                                            """+pri_cond+"""
                                                            <td>"""+sub.name+"""</td>
                                                            <td>"""+sub.email+"""</td>
                                                            <td>"""+sub.ada+"""</td>
                                                            <td>$"""+str(p)+"""</td>
                                                        </tr>"""
                                    #print
                                    reg_type_val_trp+="""<tr class="adj">
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                                            """+pri_cond1+"""
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.name+"""</td>
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.email+"""</td>
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.ada+"""</td>
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                                        </tr>"""
                                    x+=1
                                #view
                                reg_type_val_tr+="""<tr style='border: 0;'>
                                                        <td colspan='"""+colspan+"""' style='border: 0;'></td>
                                                        <td>Total</td>
                                                        <td>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                                #print
                                reg_type_val_trp+="""<tr style='border: 0;'>
                                                        <td style='font-size: 15px; border-color: #ddd !important;' colspan='"""+colspan+"""'></td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                            elif conven.id in [3, 4, 6, 7, 9, 11, 12, 13, 14, 16, 17, 21, 25, 26] and in_status:
                                x=1
                                sub_total=0
                                for sub in subrows:
                                    print_count=Id_prints.objects.filter(con_type=2,ref_id=sub.id).aggregate(print=Count(id))
                                    sub_total+=int(sub.price)
                                    if sub.name!='':
                                        if sub.updated_price is None or sub.updated_price=='':
                                            p=int(sub.price)
                                        else:
                                            p=int(sub.updated_price)
                                        if method=='print':
                                            pri_cond='<td>'+str(print_count['print'])+'</td>'
                                            pri_cond1='<td style="font-size: 15px; border-color: #ddd !important;">'+str(print_count['print'])+'</td>'
                                        else:
                                            pri_cond=''
                                            pri_cond1=''
                                        #view
                                        reg_type_val_tr+="""<tr class="adj">
                                                            <td>"""+str(x)+"""</td>
                                                            """+pri_cond+"""
                                                            <td>"""+sub.name+"""</td>
                                                            <td colspan="2">"""+sub.email+"""</td>
                                                            <td>$"""+str(p)+"""</td>
                                                        </tr>"""
                                        #print
                                        reg_type_val_trp+="""<tr class="adj">
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                                            """+pri_cond1+"""
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.name+"""</td>
                                                            <td style='font-size: 15px; border-color: #ddd !important;' colspan="2">"""+sub.email+"""</td>
                                                            <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                                        </tr>"""
                                #view
                                reg_type_val_tr+="""<tr style='border: 0;'>
                                                        <td colspan='"""+colspan+"""' style='border: 0;'></td>
                                                        <td>Total</td>
                                                        <td>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                                #print
                                reg_type_val_trp+="""<tr style='border: 0;'>
                                                        <td colspan='"""+colspan+"""' style='font-size: 15px; border-color: #ddd !important;'></td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                            elif conven.id in [8] and in_status:
                                    x=1
                                    sub_total=0
                                    for sub in subrows:
                                        print_count=Id_prints.objects.filter(con_type=2,ref_id=sub.id).aggregate(print=Count(id))
                                        if sub.updated_price is None or sub.updated_price=='':
                                            p=int(sub.price)
                                        else:
                                            p=int(sub.updated_price)
                                        sub_total+=p
                                        if method=='print':
                                            pri_cond='<td>'+str(print_count['print'])+'</td>'
                                            pri_cond1='<td style="font-size: 15px; border-color: #ddd !important;">'+str(print_count['print'])+'</td>'
                                        else:
                                            pri_cond=''
                                            pri_cond1=''
                                        #view
                                        reg_type_val_tr+="""<tr class="adj">
                                                                <td>"""+str(x)+"""</td>
                                                                """+pri_cond+"""
                                                                <td colspan="3">"""+sub.name+""" ("""+sub.ada+""") </td>
                                                                <td>$"""+str(p)+"""</td>
                                                            </tr>"""
                                        #print
                                        reg_type_val_trp+="""<tr class="adj">
                                                                <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                                                """+pri_cond1+"""
                                                                <td colspan="3" style='font-size: 15px; border-color: #ddd !important;'>"""+sub.name+""" ("""+sub.ada+""") </td>
                                                                <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                                            </tr>"""
                                    #view
                                    reg_type_val_tr+="""<tr style='border: 0;'>
                                                        <td colspan='"""+colspan+"""' style='border: 0;'></td>
                                                        <td>Total</td>
                                                        <td>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                                    #print
                                    reg_type_val_trp+="""<tr style='border: 0;'>
                                                        <td colspan='"""+colspan+"""' style='font-size: 15px; border-color: #ddd !important;'></td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                                        <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                                                    </tr>"""
                #view
                reg_type_val_tr+="""<tr style='border: 0;'>
                            <td colspan='"""+colspan+"""' style='border: 0'></td>
                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">TOTAL
                            </td>
                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">$"""+str(data["amount"])+"""
                            </td>
                        </tr>"""
                #print
                reg_type_val_trp+="""<tr style='border: 0;'>
                            <td colspan='"""+colspan+"""' style='font-size: 15px; border-color: #ddd !important;'></td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">TOTAL
                            </td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">$"""+str(data["amount"])+"""
                            </td>
                        </tr>"""
                if data["updated_grand_amount"] is None or data["updated_grand_amount"]=='':
                    pass
                else:
                    reg_type_val_tr+="""<tr style='border: 0;'>
                                            <td colspan='"""+colspan+"""' style='border: 0'></td>
                                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">GRAND TOTAL
                                            </td>
                                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">$"""+str(data["updated_grand_amount"])+"""
                                            </td>
                                        </tr>"""
                    reg_type_val_trp+="""<tr style='border: 0;'>
                            <td colspan='"""+colspan+"""' style='font-size: 15px; border-color: #ddd !important;'></td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">GRAND TOTAL
                            </td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">$"""+str(data["updated_grand_amount"])+"""
                            </td>
                        </tr>"""
                    balance = data['amount'] - data['updated_grand_amount']
                    if balance > 0:
                        m="UDA to pay"
                        a=balance
                    else:
                        m="User to pay"
                        a=balance*-1
                    reg_type_val_tr+="""<tr style='border: 0;'>
                                            <td colspan='"""+colspan+"""' style='border: 0'></td>
                                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">"""+m+"""
                                            </td>
                                            <td style="font-weight:600;border-bottom: 1px solid #eaedf1;">$"""+str(a)+"""
                                            </td>
                                        </tr>"""
                    reg_type_val_trp+="""<tr style='border: 0;'>
                            <td colspan='"""+colspan+"""' style='font-size: 15px; border-color: #ddd !important;'></td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">"""+m+"""
                            </td>
                            <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">$"""+str(a)+"""
                            </td>
                        </tr>"""
                reg_type_val_tr+="</tbody></table></td></tr>"
                reg_type_val_trp+="</tbody></table></td></tr>"
            if workshopsList:
                reg_type_val_tr+="""
                                    <tr>
                                        <td colspan="2">
                                            <h4 class='mb-0 mt-4 text-lg-center py-1'><strong>UDA - Hands on Exhibitor Registration</strong></h4>
                                        </td>
                                    </tr>
                                    <tr>
                                    <td colspan='2'>
                                        <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 10px;"
                                            class="table-bordered table">
                                            <thead>
                                                <tr>
                                                    <th class='bg-color text-uppercase'><strong>SL NO</strong></th>
                                                    """+pri_head+"""
                                                    <th class='bg-color text-uppercase'><strong>NAME</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>EMAIL</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>MOBILE</strong></th>
                                                    <th class='bg-color text-uppercase'><strong>Fee</strong></th>
                                                </tr>
                                            </thead>
                                            <tbody class="pnt">"""
                reg_type_val_trp+="""<tr>
                                <td colspan="2">
                                    <h4 class='mb-0 text-center py-1'
                                        style='font-size: 22px;color: #000;margin-top: 25px;margin-bottom:25px;'>
                                        <strong>
                                            UDA - Hands on Exhibitor Registration
                                        </strong>
                                    </h4>
                                </td>
                            </tr>
                            <tr>
                                <td colspan='2'>
                                    <table style="width: 100%;border-bottom: 0;border-left: 0;margin-top: 10px;"
                                        class="table-bordered table">
                                        <thead>
                                            <tr>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'><strong>SL
                                                        NO</strong></th>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'><strong>No.
                                                        of Prints</strong></th>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
                                                    <strong>NAME</strong>
                                                </th>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
                                                    <strong>EMAIL</strong>
                                                </th>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'><strong>MOBILE</strong></th>
                                                <th class='bg-color text-uppercase'
                                                    style='font-size: 15px; color: #000; border-color: #ddd !important;'>
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
                    reg_type_val_tr+='<tr><td colspan="6" class="for-blue">'+work.name+'($'+ str(work.amount)+')</td></tr>'
                    reg_type_val_trp+='<tr><td colspan="6" class="for-blue" style="font-size: 15px; border-color: #ddd !important;">'+work.name+'($'+ str(work.amount)+')</td></tr>'
                    if in_status:
                        x=1
                        sub_total=0
                        for sub in subrows:
                            if sub.updated_price is None or sub.updated_price=='':
                                p=int(sub.price)
                            else:
                                p=int(sub.updated_price)
                            sub_total+=p
                            print_count=Id_prints.objects.filter(con_type=1,ref_id=sub.id).aggregate(print=Count(id))
                            if method=='print':
                                pri_cond='<td>'+str(print_count['print'])+'</td>'
                                pri_cond1='<td style="font-size: 15px; border-color: #ddd !important;">'+str(print_count['print'])+'</td>'
                            else:
                                pri_cond=''
                                pri_cond1=''
                            reg_type_val_tr+="""<tr class="adj">
                                                    <td>"""+str(x)+"""</td>
                                                    """+pri_cond+"""
                                                    <td>"""+sub.name+"""</td>
                                                    <td>"""+sub.email+"""</td>
                                                    <td>"""+sub.mobile+"""</td>
                                                    <td>$"""+str(p)+"""</td>
                                                </tr>"""
                            reg_type_val_trp+="""<tr class="adj">
                                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                                    <td style="font-size: 15px; border-color: #ddd !important;">"""+str(print_count['print'])+"""</td>
                                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.name+"""</td>
                                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.email+"""</td>
                                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+sub.mobile+"""</td>
                                                    <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                                </tr>"""
                            x+=1
                        reg_type_val_tr+="""<tr style='border: 0;'>
                                                <td colspan='"""+colspan+"""' style='border: 0;'></td>
                                                <td>Total</td>
                                                <td>$"""+str(sub_total)+"""</td>
                                            </tr>"""
                        reg_type_val_trp+="""<tr style='border: 0;'>
                                                <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
                                                <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                                <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                                            </tr>"""
                reg_type_val_tr+="</tbody></table></td></tr>"
                reg_type_val_trp+="</tbody></table></td></tr>"
        else:
            err=1
        return {"input":input,"con_datas":reg_type_val_tr,"con_datas_print":reg_type_val_trp,"err":err,"msg":msg}
