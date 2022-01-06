import json
from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import Handon_form,Convention_types_prices,Convention_form_workshop,Handon_form_workshop,Handon_workshop,Id_prints,Convention_types
import datetime as dt
from django_mysql.models import GroupConcat
from hashids import Hashids

class convention_details():
    def none_to_str(self,s):
        if s is None:
            return ''
        else:
            return s

    # set condition for differentiate fall or spring or convention price
    def get_prices(self,form_status,amount,updated_grand_amount):
        today=dt.date.today()
        get_price=[]
        msg=''
        arr_price=0
        grand_price=0
        if form_status is not None and form_status:
            get_price=Convention_types_prices.objects.filter(form_status=form_status,start_date__lte=today,end_date__gte=today)[0]
            arr_price = json.loads(get_price.bulk_price)
        if not get_price:
            msg='The deadline for all pre-registration is April 11, ' ,today.year
        if updated_grand_amount is None or updated_grand_amount=='':
            grand_price = amount
        else:
            grand_price = updated_grand_amount
        return {"arr_price":arr_price,"grand_price":grand_price,"msg":msg}

    #transaction details
    def transaction_detail(self,data):
        payment_modes=["","Cash","Cheque/DD","POS","Venmo","Others"]
        t_date='-'
        transaction_ref=''
        transaction_status=''
        off_transaction_payment_mode=''
        off_transaction_memo=''
        off_transaction_payment_details=''
        if data['transaction_on'] is not None:
            t_date=data['transaction_on'].strftime("%m/%d/%Y %H:%M:%S %p")
        t_date_off='-'
        if data['created_on'] is not None:
            t_date_off=data['created_on'].strftime("%m-%d-%Y")
        # online
        if data['off_transaction_status']==1:
            transaction_id=data['transaction_id']
            transaction_date=t_date
            transaction_ref=data["transaction_ref"]
            transaction_status=data["transaction_status"]
            if transaction_status is None:
                transaction_status='Pending'
            elif transaction_status!='Success':
                transaction_status='Failed'
        # offline
        elif data['off_transaction_status']==2:
            transaction_id=data['off_transaction_id']
            transaction_date=t_date_off
            off_transaction_payment_mode=payment_modes[int(data["off_transaction_payment_mode"])]
            if data["off_transaction_memo"] is not None:
                off_transaction_memo=data["off_transaction_memo"]
            if data["off_transaction_payment_details"] is not None:
                off_transaction_payment_details=data["off_transaction_payment_details"]
        return {"transaction_on":t_date,"transaction_id":transaction_id,"transaction_date":transaction_date,"transaction_ref":transaction_ref,"transaction_status":transaction_status,"off_transaction_payment_mode":off_transaction_payment_mode,"off_transaction_memo":off_transaction_memo,"off_transaction_payment_details":off_transaction_payment_details}

    def formhead(self,status):
        form_head=''
        if status == 1:
            form_head="UDA - Convention Registration"
        elif status == 2:
            form_head="UDA - Spring Registration"
        elif status == 3:
            form_head="UDA - Fall Registration"
        return {"form_head":form_head}

    def get_conventions(self,hidden_hand_id,data,arr_price,print_de):
        covention_list=''
        reg_type_val_tr=''
        reg_type_val_trp=''
        contab2=0
        in_convention_arr = []
        li_conv_shop=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(con_works=GroupConcat('work_id'))
        if li_conv_shop['con_works'] is not None:
            in_convention_arr=li_conv_shop['con_works'].split(',')
        if in_convention_arr:
            covention_list=Convention_types.objects.filter(status=1,id__in=in_convention_arr).order_by('id')
            contab2=1
            conven_datas=self.convention_list_data(covention_list,data['form_status'],print_de,hidden_hand_id,arr_price,in_convention_arr,data)
            reg_type_val_tr=conven_datas['reg_type_val_tr']
            reg_type_val_trp=conven_datas['reg_type_val_trp']
        return {"contab2":contab2,"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def conven_data_list_first(self,subrows,print_de):
        reg_type_val_tr=""
        reg_type_val_trp=""
        x=1
        sub_total=0
        colspan=print_de['colspan']
        method=print_de['method']
        for sub in subrows:
            print_count=Id_prints.objects.filter(con_type=2,ref_id=sub.id).aggregate(print=Count(id))
            if sub.updated_price is None or sub.updated_price=='':
                p=int(sub.price)
            else:
                p=int(sub.updated_price)
            sub_total+=p
            if method=='print':
                pri_cond='<td>'+str(print_count['print'])+'</td>'
            else:
                pri_cond=''
            #view
            reg_type_val_tr+="""<tr class="adj">
                                    <td>"""+str(x)+""" </td>
                                    """+pri_cond+"""
                                    <td>"""+self.none_to_str(sub.name)+"""</td>
                                    <td>"""+self.none_to_str(sub.email)+"""</td>
                                    <td>"""+self.none_to_str(sub.ada)+"""</td>
                                    <td>$"""+str(p)+""" </td>
                                    </tr>"""
            #print
            reg_type_val_trp+="""<tr class="adj">
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                    <td style="font-size: 15px; border-color: #ddd !important;">"""+str(print_count['print'])+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.name)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.email)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.ada)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                </tr>"""
            x+=1
        #view
        reg_type_val_tr+="""<tr style='border:0;'>
                                <td colspan='"""+colspan+"""' style='border:0;'></td>
                                <td>Total</td>
                                <td>$"""+str(sub_total)+"""</td>
                            </tr>"""
        #print
        reg_type_val_trp+="""<tr style='border: 0;'>
                                <td style='font-size: 15px; border-color: #ddd !important;' colspan='4'></td>
                                <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                            </tr>"""
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def conven_data_list_second(self,subrows,print_de):
        reg_type_val_tr=""
        reg_type_val_trp=""
        colspan=print_de['colspan']
        method=print_de['method']
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
                else:
                    pri_cond=''
                #view
                reg_type_val_tr+="""<tr class="adj">
                                    <td>"""+str(x)+"""  </td>
                                    """+pri_cond+"""
                                    <td>"""+self.none_to_str(sub.name)+"""</td>
                                    <td colspan="2">"""+self.none_to_str(sub.email)+"""</td>
                                    <td>$"""+str(p)+""" </td> 
                                </tr>"""
                #print
                reg_type_val_trp+="""<tr class="adj">
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""   </td>
                                    <td style="font-size: 15px; border-color: #ddd !important;">"""+str(print_count['print'])+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.name)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;' colspan="2">"""+self.none_to_str(sub.email)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+""" </td>  
                                </tr>"""
        #view
        reg_type_val_tr+="""<tr style='border: 0;'>
                                    <td colspan='"""+colspan+"""' style='border: 0;'></td>
                                <td> Total</td>
                                <td>$"""+str(sub_total)+"""</td>
                            </tr>"""
        #print
        reg_type_val_trp+="""<tr style='border: 0;'>
                                <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
                                <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                                <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                            </tr>"""
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def conven_data_list_third(self,subrows,print_de):
        reg_type_val_tr=""
        reg_type_val_trp=""
        colspan=print_de['colspan']
        method=print_de['method']
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
            else:
                pri_cond=''
            #view
            reg_type_val_tr+="""<tr class="adj">
                                    <td>"""+str(x)+"""</td>
                                    """+pri_cond+"""
                                    <td colspan="3">"""+self.none_to_str(sub.name)+""" ("""+self.none_to_str(sub.ada)+""") </td>
                                    <td>$"""+str(p)+"""</td>
                                </tr>"""
            #print
            reg_type_val_trp+="""<tr class="adj">
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                    <td style="font-size: 15px; border-color: #ddd !important;">"""+str(print_count['print'])+"""</td>
                                    <td colspan="3" style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.name)+""" ("""+self.none_to_str(sub.ada)+""") </td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(p)+"""</td>
                                </tr>"""
        #view
        reg_type_val_tr+="""<tr style='border: 0;'>
                            <td colspan='"""+colspan+"""' style='border:0;'></td>
                            <td>Total</td>
                            <td>$"""+str(sub_total)+"""</td>
                        </tr>"""
        #print
        reg_type_val_trp+="""<tr style='border: 0;'>
                            <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
                            <td style='font-size: 15px; border-color: #ddd !important;'>Total</td>
                            <td style='font-size: 15px; border-color: #ddd !important;'>$"""+str(sub_total)+"""</td>
                        </tr>"""
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def conven_records(self,covention_list,hidden_hand_id,in_convention_arr,arr_price,print_de):
        reg_type_val_tr=''
        reg_type_val_trp=''
        for conven in covention_list:
            in_status=0
            if conven.id and str(conven.id) in in_convention_arr:
                subrows=Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=conven.id)
                if subrows:
                    in_status=1
                    #view
                    reg_type_val_tr+='<tr><td colspan="6" class="for-blue">'+conven.name.replace("NAME", "")+' ($'+str(arr_price[str(conven.id)])+')</td></tr>'
                    #print
                    reg_type_val_trp+='<tr><td colspan="6" class="for-blue" style="font-size: 15px; border-color: #ddd !important;">'+conven.name.replace("NAME", "")+' ($'+str(arr_price[str(conven.id)])+')</td></tr>'
                if conven.id in [1, 2, 5, 15, 18, 19, 20, 22, 23, 24] and in_status:
                    conven_data_list_first_data=self.conven_data_list_first(subrows,print_de)
                    reg_type_val_tr+=conven_data_list_first_data['reg_type_val_tr']
                    reg_type_val_trp+=conven_data_list_first_data['reg_type_val_trp']
                elif conven.id in [3, 4, 6, 7, 9, 11, 12, 13, 14, 16, 17, 21, 25, 26] and in_status:
                    conven_data_list_second_data=self.conven_data_list_second(subrows,print_de)
                    reg_type_val_tr+=conven_data_list_second_data['reg_type_val_tr']
                    reg_type_val_trp+=conven_data_list_second_data['reg_type_val_trp']
                elif conven.id in [8] and in_status:
                    conven_data_list_third_data=self.conven_data_list_third(subrows,print_de)
                    reg_type_val_tr+=conven_data_list_third_data['reg_type_val_tr']
                    reg_type_val_trp+=conven_data_list_third_data['reg_type_val_trp']
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}
        
    
    def convention_list_data(self,covention_list,form_status,print_de,hidden_hand_id,arr_price,in_convention_arr,data):
        head=self.formhead(form_status)
        form_head=head['form_head']
        reg_type_val_tr=''
        reg_type_val_trp=''
        colspan=print_de['colspan']
        pri_head=print_de['pri_head']
        if covention_list:
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
                            <th class="bg-color text-uppercase" style="font-size: 15px; color: #000; border-color: #ddd !important;"><strong>No.of Prints</strong></th>
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
            table_records=self.conven_records(covention_list,hidden_hand_id,in_convention_arr,arr_price,print_de)
            reg_type_val_tr+=table_records['reg_type_val_tr']
            reg_type_val_trp+=table_records['reg_type_val_trp']
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
                        <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
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
                        <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
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
                        <td colspan='4' style='font-size: 15px; border-color: #ddd !important;'></td>
                        <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">"""+m+"""
                        </td>
                        <td style="font-size: 15px;font-weight:600;border-bottom: 1px solid #eaedf1;border-color: #ddd !important;">$"""+str(a)+"""
                        </td>   
                    </tr>"""
            reg_type_val_tr+="</tbody> </table> </td> </tr>"
            reg_type_val_trp+="</tbody>  </table> </td></tr>"
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def print_defaults(self,method):
        if method=='print':
            colspan='4'
            pri_head='<th class="bg-color text-uppercase"><strong>No. of Prints</strong></th>'
            pri_head_p='<th class="bg-color text-uppercase" style="font-size: 15px; color: #000; border-color: #ddd !important;"><strong>No.of Prints</strong></th>'
        else:
            colspan='3'
            pri_head=''
            pri_head_p=''
        return {"colspan":colspan,"pri_head":pri_head,"pri_head_p":pri_head_p,"method":method}

    def get_workshops_data(self,hidden_hand_id):
        contab1=0
        li_wrk_shop=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id).aggregate(hand_works=GroupConcat('work_id'))
        workshops_list=[]
        in_workshop_arr=[]
        if li_wrk_shop['hand_works'] is not None:
            in_workshop_arr=li_wrk_shop['hand_works'].split(',')
        if in_workshop_arr:
            contab1=1
            workshops_list=Handon_workshop.objects.filter(status=1,id__in=in_workshop_arr).order_by('id')
        return {"contab1":contab1,"workshops_list":workshops_list}

    def work_shop_records(self,subrows,print_de):
        reg_type_val_tr=''
        reg_type_val_trp=''
        colspan=print_de['colspan']
        method=print_de['method']
        x=1
        sub_total=0
        for sub in subrows:
            if sub.updated_price is None or sub.updated_price=='':
                p=int(sub.amount)
            else:
                p=int(sub.updated_price)
            sub_total+=p
            print_count=Id_prints.objects.filter(con_type=1,ref_id=sub.id).aggregate(print=Count(id))
            if method=='print':
                pri_cond='<td>'+str(print_count['print'])+'</td>'
            else:
                pri_cond=''
            reg_type_val_tr+="""<tr class="adj">
                                    <td>"""+str(x)+"""</td>
                                    """+pri_cond+"""
                                    <td>"""+self.none_to_str(sub.name)+"""</td>
                                    <td>"""+self.none_to_str(sub.email)+"""</td>
                                    <td>"""+self.none_to_str(sub.mobile)+"""</td>
                                    <td>$"""+str(p)+"""</td>
                                </tr>"""
            reg_type_val_trp+="""<tr class="adj">
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+str(x)+"""</td>
                                    <td style="font-size: 15px; border-color: #ddd !important;">"""+str(print_count['print'])+""" </td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.name)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.email)+"""</td>
                                    <td style='font-size: 15px; border-color: #ddd !important;'>"""+self.none_to_str(sub.mobile)+"""</td>
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
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp}

    def workshop_table_datas(self,hidden_hand_id,print_de):
        reg_type_val_tr=''
        reg_type_val_trp=''
        pri_head=print_de['pri_head']
        workshops_list_data=self.get_workshops_data(hidden_hand_id)
        workshops_list=workshops_list_data['workshops_list']
        contab1=workshops_list_data['contab1']
        if workshops_list:
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
                for work in workshops_list:
                    in_status=0
                    subrows=Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hidden_hand_id,work_id=work.id)
                    if subrows:
                        in_status=1
                    reg_type_val_tr+='<tr><td colspan="6" class="for-blue">'+work.name+'($'+ str(work.amount)+')</td></tr>'
                    reg_type_val_trp+='<tr><td colspan="6" class="for-blue" style="font-size: 15px; border-color: #ddd !important;">'+self.none_to_str(work.name)+'($'+ str(work.amount)+')</td></tr>'
                    if in_status:
                        work_record_data=self.work_shop_records(subrows,print_de)
                        reg_type_val_tr+=work_record_data['reg_type_val_tr']
                        reg_type_val_trp+=work_record_data['reg_type_val_trp']
                reg_type_val_tr+="</tbody> </table></td></tr>"
                reg_type_val_trp+="</tbody></table> </td></tr>"
        return {"reg_type_val_tr":reg_type_val_tr,"reg_type_val_trp":reg_type_val_trp,"contab1":contab1}
    
    def view_transaction_details(self,request,ids):
        id_method=ids.split('-')
        method=id_method[1]
        print_de=self.print_defaults(method)
        hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
        hashid = hashids.decode(id_method[0]) 
        Tid=hashid[0]
        input = {}
        hidden_hand_id = 0
        err=1
        msg=''
        reg_type_val_tr=''
        reg_type_val_trp=''
        check_data=Handon_form.objects.filter(form=1,id=Tid).exclude(status=2).exists()
        if check_data:
            err=0
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
            add=''
            if data['address'] is not None:
                add+=data['address']
            if data['city'] is not None:
                add+=", "+data['city']
            if data['state'] is not None:
                add+=", "+data['state']+"."
            input['full_address']=add

            #Transactions Info
            transactions_info=self.transaction_detail(data)
            input['transaction_on']=transactions_info['transaction_on']
            input['transaction_id']=transactions_info['transaction_id']
            input['transaction_date']=transactions_info['transaction_date']
            input['transaction_ref']=transactions_info["transaction_ref"]
            input['transaction_status']=transactions_info["transaction_status"]
            input['off_transaction_payment_mode']=transactions_info["off_transaction_payment_mode"]
            input['off_transaction_memo']=transactions_info["off_transaction_memo"]
            input['off_transaction_payment_details']=transactions_info["off_transaction_payment_details"]

            # set condition for differentiate fall or spring or convention price
            prices_res=self.get_prices(data['form_status'],data["amount"],data["updated_grand_amount"])
            input['grand_price']=prices_res['grand_price']
            msg=prices_res['msg']
            arr_price=prices_res['arr_price']

            hidden_hand_id = data["id"]
            
            #Conventions
            conven_records=self.get_conventions(hidden_hand_id,data,arr_price,print_de)
            input['contab2']=conven_records['contab2']
            reg_type_val_tr+=conven_records['reg_type_val_tr']
            reg_type_val_trp+=conven_records['reg_type_val_trp']
            #Workshops
            work_records=self.workshop_table_datas(hidden_hand_id,print_de)
            input['contab1']=work_records['contab1']
            reg_type_val_tr+=work_records['reg_type_val_tr']
            reg_type_val_trp+=work_records['reg_type_val_trp']
        return {"input":input,"con_datas":reg_type_val_tr,"con_datas_print":reg_type_val_trp,"err":err,"msg":msg}
