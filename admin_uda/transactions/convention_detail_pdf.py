import json
from admin_uda.models import Handon_form,Convention_form_workshop,Handon_form_workshop,Handon_workshop,Convention_types,Convention_types_prices
import datetime as dt
from django_mysql.models import GroupConcat

class convention_details_pdf:
    def none_to_str(self,s):
        if s is None:
            return ''
        else:
            return s
    def pdf_transaction_details(self,hand_id):
        input={}
        table=''
        err=0
        msg=''
        tid=hand_id
        hidden_hand_id = 0
        total_grand_val=0
        data={}
        check_data=Handon_form.objects.filter(form=1,id=tid).exclude(status=2).exists()
        if check_data:
            data=list(Handon_form.objects.filter(form=1,id=tid).exclude(status=2).values())[0]
            input['form_status']=data['form_status']
            hidden_hand_id = data["id"]
            str_conv_shop=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(con_works=GroupConcat('work_id'))
            li_wrk_shop=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(hand_works=GroupConcat('work_id'))
            in_convention_arr=[]
            in_workshop_arr=[]
            if str_conv_shop['con_works'] is not None:
                in_convention_arr=str_conv_shop['con_works'].split(',')
            if li_wrk_shop['hand_works'] is not None:
                in_workshop_arr=li_wrk_shop['hand_works'].split(',')
            workshops_list=[]
            covention_list=[]
            if in_workshop_arr:
                workshops_list=Handon_workshop.objects.filter(status=1,id__in=in_workshop_arr).order_by('id')
            if in_convention_arr:
                covention_list=Convention_types.objects.filter(status=1,id__in=in_convention_arr).order_by('id')
            today=dt.date.today()
            get_price=[]
            # set condition for differentiate fall or spring or convention price
            arr_price=0
            if data['form_status'] is not None and data['form_status']:
                get_price=Convention_types_prices.objects.filter(form_status=data['form_status'],start_date__lte=today,end_date__gte=today)[0]
                arr_price = json.loads(get_price.bulk_price)
            if not get_price:
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
            if covention_list:
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
                for conven in covention_list:
                    in_status=0
                    in_grand=0
                    if conven.id:
                        if str(conven.id) in in_convention_arr:
                            subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=conven.id)
                            if subrows:
                                in_status=1
                                for sub in subrows:
                                    if sub.updated_price is None or sub.updated_price=='':
                                        in_grand+=int(sub.price)
                                    else:
                                        in_grand+=int(sub.updated_price)
                                total_grand_val+=in_grand
                                table+="""<tr style="border: 0.5px #ddd;">
                                            <td colspan="5" class="for-blue"
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                """+conven.name.replace("NAME", "")+' ($'+str(arr_price[str(conven.id)])+""")</td>
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
                                        """+self.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;'>
                                        """+self.none_to_str(sub.email)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+self.none_to_str(sub.ada)+"""</td>
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
                                        """+self.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;' colspan="2">
                                        """+self.none_to_str(sub.email)+"""
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
                                                        """+self.none_to_str(sub.name)+""" ("""+self.none_to_str(sub.ada)+""")
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
            if workshops_list:     
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
                for work in workshops_list:
                    in_status=0
                    in_grand=0
                    subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=work.id)
                    if subrows:
                        in_status=1
                        for sub in subrows:
                            if sub.updated_price is None or sub.updated_price=='':
                                in_grand+=int(sub.amount)
                            else:
                                in_grand+=int(sub.updated_price)
                        total_grand_val+=in_grand
                    table+="""<tr style="border: 0.5px #ddd;">
                                            <td colspan="5" class="for-blue"
                                                style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                                """+self.none_to_str(work.name)+'($'+ str(work.amount)+""")</td>
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
                                        """+self.none_to_str(sub.name)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;width: 200px;'>
                                        """+self.none_to_str(sub.email)+"""
                                    </td>
                                    <td
                                        style='font-family: Nunito, sans-serif;font-size: 15px;padding: 5px; border: 1px solid #ddd !important;'>
                                        """+self.none_to_str(sub.mobile)+"""
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
