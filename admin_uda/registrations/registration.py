from django.http.response import JsonResponse
from admin_uda.models import Handon_form,Convention_form_workshop,Handon_form_workshop,Convention_types,Handon_workshop,Convention_types_prices,Convention_types_prices,default_functions
import datetime as dt
from django_mysql.models import GroupConcat
import json
from django.utils.html import strip_tags
import os
from admin_uda.transactions.convention_detail_pdf import convention_details_pdf
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from io import BytesIO
from django.template.loader import get_template,render_to_string
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
import qrcode
from django.core.files import File
from PIL import ImageDraw,Image
from hashids import Hashids

default_obj = default_functions()
class Registration():
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_format_time = "%m/%d/%Y %I:%M:%S %p"
    def link_callback(self,uri, rel):
        try:
            """
            Convert HTML URIs to absolute system paths so xhtml2pdf can access those
            resources
            """
            result = finders.find(uri)
            if result:
                    if not isinstance(result, (list, tuple)):
                            result = [result]
                    result = list(os.path.realpath(path) for path in result)
                    path=result[0]
            else:
                    surl = settings.STATIC_URL        # Typically /static/
                    sroot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                    murl = settings.MEDIA_URL         # Typically /media/
                    mroot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                    if uri.startswith(murl):
                            path = os.path.join(mroot, uri.replace(murl, ""))
                    elif uri.startswith(surl):
                            path = os.path.join(sroot, uri.replace(surl, ""))
                    else:
                            return uri

            # make sure that file exists
            if not os.path.isfile(path):
                    raise FileNotFoundError(
                            'media URI must start with %s or %s' % (surl, murl)
                    )
            return path
        except Exception as e:
            return e
    
    def mail_qr_convention(self,rt,hashid,convention_ws):
        con_list = []
        for cv in convention_ws:
            hashids_cvid = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
            hashid_cvid = hashids_cvid.encode(cv.id)
            if cv.id != 9:                        
                url = 'admin/convention-id-card-print-ind.php?q={hashid}&cfw='+hashid_cvid
                filename = cv.name.replace(' ','') + '_cfw' + str(cv.id)
                #qrcode image
                img=qrcode.make(url)
                img.save(rt+f"/uploads/mail_qrcode/"+ filename +".png")
                #qrcode pdf
                pdf = Image.open(rt+f"/uploads/mail_qrcode/"+ filename +".png")
                pdf_off = pdf.convert('RGB')
                pdf_off.save(rt+f"/uploads/mail_qrcode/"+ filename +".pdf")
                con_list.append(filename)
        return con_list

    def mail_qr_attachment(self,hand_id):
        result = {}
        rt = os.path.join(settings.BASE_DIR).replace("\\","/")
        if hand_id>0:
            hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
            hashid = hashids.encode(hand_id)
            convention_ws = Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hand_id)
            # .aggregate(con_ws_ids = GroupConcat('work_id'))
            handon_ws = Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hand_id)
            # .aggregate(hands_ws_ids = GroupConcat('work_id'))
            if not os.path.exists(rt+f'/uploads/mail_qrcode/'):
                os.makedirs(rt+f'/uploads/mail_qrcode/')
            if convention_ws:
                result['convention'] = self.mail_qr_convention(rt,hashid,convention_ws)
            if handon_ws:
                workshop_lists = []
                for ws in handon_ws:
                    hashids_wsid = Hashids(salt='UDAHEALTHDENTALSALT',min_length=10)
                    hashid_wsid = hashids_wsid.encode(ws.id)

                    url = 'admin/convention-id-card-print-ind.php?q={hashid}&hfw='+hashid_wsid
                    filename = ws.name.replace(' ','') + '_hfw' + str(ws.id)
                    #qrcode image
                    img=qrcode.make(url)
                    img.save(rt+f"/uploads/mail_qrcode/"+ filename +".png")
                    #qrcode pdf
                    pdf = Image.open(rt+f"/uploads/mail_qrcode/"+ filename +".png")
                    pdf_off = pdf.convert('RGB')
                    pdf_off.save(rt+f"/uploads/mail_qrcode/"+ filename +".pdf")
                    workshop_lists.append(filename)
                result['workshops'] = workshop_lists
        return result


    def mail_pdf(self,hand_id):
        context_dict = {}
        file_name = ''
        rt = os.path.join(settings.BASE_DIR).replace("\\","/")
        obj_pdf_con=convention_details_pdf()
        dat=obj_pdf_con.pdf_transaction_details(hand_id)

        if dat['input']['form_status'] and dat['input']['form_status']==1:
            context_dict['title'] = 'Convention Transaction Details'
        elif dat['input']['form_status'] and dat['input']['form_status']==2:
            context_dict['title'] = 'Spring Transaction Details'
        elif dat['input']['form_status'] and dat['input']['form_status']==3:
            context_dict['title'] = 'Fall Transaction Details'
        else:
            context_dict['title'] = ''

        context_dict['datas'] = dat
        
        template = get_template('mail_attachment.html')        
        html  = template.render(context_dict)        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result,link_callback=self.link_callback) 
        t1=dt.datetime.now().timestamp()
        t = str(t1).replace(".","_")
        file_name= str(hand_id)+'-'+str(t)+'.pdf'

        try:
            if not os.path.exists(rt+f'/uploads/mail_pdf/'):
                os.makedirs(rt+f'/uploads/mail_pdf/')
            with open(rt+f'/uploads/mail_pdf/{file_name}','wb+') as output:
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), output,link_callback=self.link_callback)

        except Exception as e:
            print(e)

        if not pdf.err:
            return file_name

    def mail_temp_con(self,convention_ws):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        convention_lists = Convention_types.objects.filter(status=1,id__in= (none_to_str(convention_ws['con_ws_ids']).split(","))).order_by('id')
        con_list = []
        for cv in convention_lists:
            con_list.append(cv.id)

        result['con_list'] = con_list
        result['convention_lists'] = convention_lists

        return result

    def mail_temp_ws(self,handon_ws):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        workshop_lists = []
        if none_to_str(handon_ws['hands_ws_ids']):
            workshop_lists = Handon_workshop.objects.filter(status=1,id__in= (none_to_str(handon_ws['hands_ws_ids']).split(","))).order_by('id')

        result['workshop_lists'] = workshop_lists

        return result

    def get_dynamic_thead(self,form,handon_res,grand_price):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        trans_date = ''
        pay_mode = ''
        thank_mess = ''
        transaction_section = ''
        tbl_head = ''

        if form == 1:
            thank_mess = 'Thank You ! <p style=" font-size: 14px; margin: 0; ">For  Registering. Please Find Your Registered Conventions...</p>'
            if none_to_str(handon_res['transaction_on']) != '':
                trans_date = dt.datetime.strptime(none_to_str(handon_res['transaction_on'])[:19],self.datetime_format).strftime(self.datetime_format_time)

            transaction_section = '''<h4 style="padding-left: 20px; font-size: 20px;margin-bottom: 0;  margin-top: 0"><strong>Transaction Details</strong></h4>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction ID :</strong> '''+ none_to_str(handon_res["transaction_id"])+ ''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction Reference No :</strong> '''+ none_to_str(handon_res["transaction_ref"]) + ''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Amount ($) :</strong> '''+ grand_price + '''</p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction Status :</strong> '''+ none_to_str(handon_res["transaction_status"]) + ''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction Date :</strong>'''+  trans_date +''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>&nbsp;</strong></p>
            '''
            tbl_head = 'UDA - Convention Registration'
        elif form == 2:
            thank_mess = 'Thank You ! - Spring Convention Registration <p style=" font-size: 14px; margin: 0; ">For  Registering. Please Find Your Registered Spring...</p>'
            if none_to_str(handon_res['created_on']) != '':
                trans_date = dt.datetime.strptime(none_to_str(handon_res['created_on'])[:19],self.datetime_format).strftime(self.datetime_format_time)

            if none_to_str(handon_res["off_transaction_payment_mode"]):
                pay_mode = default_obj.get_payment_method(none_to_str(handon_res["off_transaction_payment_mode"]))
                
            transaction_section = '''<h4 style="padding-left: 20px; font-size: 20px"><strong>Transaction Details</strong></h4>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction ID :</strong> '''+ none_to_str(handon_res["off_transaction_id"]) + ''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction Date :</strong> '''+ trans_date +'''</p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Amount ($) :</strong> '''+ grand_price + '''</p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Payment Mode :</strong> '''+ pay_mode  +'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Payment Details :</strong> '''+ handon_res["off_transaction_payment_details"]+'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Memo :</strong> '''+ none_to_str(handon_res["off_transaction_memo"]) +'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>&nbsp;</strong></p>'''
            tbl_head = 'UDA - Spring Registration'
        elif form == 3:
            thank_mess = 'Thank You ! - Fall Convention Registration <p style=" font-size: 14px; margin: 0; ">For  Registering. Please Find Your Registered Fall...</p>'
            if none_to_str(handon_res['created_on']) != '':
                trans_date = dt.datetime.strptime(none_to_str(handon_res['created_on'])[:19],self.datetime_format).strftime(self.datetime_format_time)

            if none_to_str(handon_res["off_transaction_payment_mode"]):
                pay_mode = default_obj.get_payment_method(none_to_str(handon_res["off_transaction_payment_mode"]))

            transaction_section = '''<h4 style="padding-left: 20px; font-size: 20px"><strong>Transaction Details</strong></h4>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction ID :</strong> '''+ none_to_str(handon_res["off_transaction_id"]) + ''' </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Transaction Date :</strong> '''+ trans_date +'''</p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Amount ($) :</strong> '''+ grand_price + '''</p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Payment Mode :</strong> '''+ pay_mode +'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Payment Details :</strong> '''+ none_to_str(handon_res["off_transaction_payment_details"]) +'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Memo :</strong> '''+ none_to_str(handon_res["off_transaction_memo"]) +'''  </p>
            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>&nbsp;</strong></p>'''
            tbl_head = 'UDA - Fall Registration'

        result['thank_mess'] = thank_mess
        result['transaction_section'] = transaction_section
        result['tbl_head'] = tbl_head
        return result
    def mail_dy_gnd_cal(self,subrows,in_grand):
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        for row in subrows:
            if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
                in_grand += float(row['price']) if none_to_str(row['price']) else 0 
            else:
                in_grand += float(row['updated_price']) if none_to_str(row['updated_price']) else 0 
        return in_grand
    def dy_sub_cal(self,subrows,sub_total):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        table = ''
        for row in subrows:
            if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
                p = float(row['price']) if none_to_str(row['price']) else 0 
            else:
                p = float(row['updated_price']) if none_to_str(row['updated_price']) else 0 
            sub_total += p
            table += '''<tr>
                        <td style="border-bottom: 1px dashed #e3e5e8;    padding-left: 6px;">'''+ none_to_str(row['name'])+' '+none_to_str(row['email'])+'<br> '+none_to_str(row['ada'])+'''</td>
                        <td style="border-bottom: 1px dashed #e3e5e8;"></td>
                        <td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(p) +'''</td>
                    </tr>'''

        result['sub_total'] = sub_total
        result['table'] = table
        return result


    def dy_sub_cal2(self,cv_id,subrows,sub_total):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        table = ''
        display_style=''
        if cv_id == 9 :
            display_style=' style="display:none;" '
        for row in subrows:
            if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
                p = float(row['price'])
            else:
                p = float(row['updated_price'])
            sub_total += p
            table += '''<tr '''+ display_style +'''>
                        <td colspan="2" style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;padding-left: 6px;">'''+ none_to_str(row['name']) +' '+none_to_str(row['email'])+'''</td><td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(p) +'''</td> 
                    </tr>'''
        result['sub_total'] = sub_total
        result['table'] = table
        return result

    def dy_sub_cal3(self,subrows):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        table = ''
        sub_total = 0
        for row in subrows:
            if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
                p = float(row['price'])
            else:
                p = float(row['updated_price'])
            sub_total += p

            table += '''<tr>
                        <td style="border-bottom: 1px dashed #e3e5e8;padding-left: 6px;">'''+row['name']+''' ( '''+row['ada']+''' )</td>
                        <td style="border-bottom: 1px dashed #e3e5e8;"></td>
                        <td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(p) +'''</td>  
                    </tr>'''
        result['sub_total'] = sub_total
        result['table'] = table
        return result


    def get_dynamic_cond(self,total_grand_val,table,convention_lists,con_list,hand_id,prices_list):
        result = {}
           
        for cv in convention_lists:
            in_status = 0
            in_grand = 0
            if len(con_list) and cv.id in con_list:                            
                subrows = Convention_form_workshop.objects.values().filter(is_deleted=1,hand_id=hand_id,work_id=cv.id)
                if len(subrows)>0:
                    in_status = 1
                    in_grand = self.mail_dy_gnd_cal(subrows,in_grand)
                    total_grand_val += in_grand
                    table += '''<tr>
                                <td colspan="3" style="border-bottom: 1px dashed #e3e5e8;padding-left: 6px;">'''+ cv.name +''' ($'''+ str(prices_list[str(cv.id)]) +''')</td>
                            </tr>'''
                if cv.id in [1,2,5,15,18,19,20,22,23,24] and in_status:
                    sub_total = 0
                    
                    dy_sub_res = self.dy_sub_cal(subrows,sub_total)
                    sub_total = dy_sub_res['sub_total']
                    table += dy_sub_res['table']
                    table += '''<tr>
                                <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;"></td>
                                <td style="border-bottom: 1px dashed #e3e5e8;">Total</td>
                                <td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(sub_total) +'''</td>
                            </tr>'''
                elif cv.id in [3, 4, 6, 7, 9, 11, 12, 13, 14, 16, 17,21,25,26] and in_status:
                    sub_total = 0
                    cv_id2 = cv.id
                    dy_sub_res2 = self.dy_sub_cal2(cv_id2,subrows,sub_total)
                    sub_total = dy_sub_res2['sub_total']
                    table += dy_sub_res2['table']
                    table += '''<tr>
                        <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;"></td>
                        <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;">Total</td>
                        <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;">$'''+ str(sub_total) +'''</td>
                    </tr>'''

                elif cv.id in [8] and in_status:
                    
                    dy_sub_res3 = self.dy_sub_cal3(subrows)
                    sub_total = dy_sub_res3['sub_total']
                    table += dy_sub_res3['table']

                    table += '''<tr>
                                    <td  style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;"></td>
                                    <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;">Total</td>
                                    <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;">$'''+ str(sub_total) +''' </td>
                                </tr>'''
        
        result['table'] = table
        result['total_grand_val'] = total_grand_val
        return result


    def get_dynamic_content_action(self,tbl_head,convention_lists,con_list,hand_id,prices_list):
        result = {}
        table = ''
        total_grand_val = 0
        count_convention = len(convention_lists)
        if count_convention>0:
            table +='<tr><th colspan="12"><h4><strong>'+ tbl_head +'</strong></h4></th></tr>'
            table += '''
            <tr style="border: 1px dashed #ddd;color: #1c202a;">
                <th colspan="2" style="width:60%;text-align:left;border-bottom: 1px dashed #e3e5e8;padding-left: 6px;"><strong>NAME</strong></th>
                
                <th style="width:10%;text-align:left;border-bottom: 1px dashed #e3e5e8;"><strong>Fee</strong></th>
            </tr>
            '''
            
            get_dynamic_cond_res = self.get_dynamic_cond(total_grand_val,table,convention_lists,con_list,hand_id,prices_list)
            table += get_dynamic_cond_res['table']
            total_grand_val = get_dynamic_cond_res['total_grand_val']
        
        result['table'] = table
        result['total_grand_val'] = total_grand_val
        return result





    def amount_calculation_fn(self,handon_res):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        if none_to_str(handon_res['updated_grand_amount']) == 'NULL' or none_to_str(handon_res['updated_grand_amount']) =='':
            updated_grand_amount_sec = ''
            balance = 0
        else:
            updated_grand_amount_sec = '''<tr>
                    <td style="padding:10px 0px;"></td>
                    <td style="font-weight:600;padding:10px 0px;">New Grand Total</td>
                    <td style="font-weight:600;padding:10px 0px;">$'''+ none_to_str(handon_res['updated_grand_amount']) +'''</td>
                </tr>
                <tr>
                    <td style="padding:10px 0px;"></td>'''
            balance = handon_res['amount'] - (handon_res['updated_grand_amount'] if none_to_str(handon_res['updated_grand_amount']) else 0)
            if balance > 0:
                m="UDA to pay"
                a=balance
            else:
                m="User to pay"
                a=balance*-1
            updated_grand_amount_sec += '''
                <td style="font-weight:600;padding:10px 0px;">'''+ m +'''</td>
                <td style="font-weight:600;padding:10px 0px;">$'''+ str(a) +'''</td>
            </tr>'''
        
        result['updated_grand_amount_sec'] = updated_grand_amount_sec
        return result

    def mail_workshop_gnd_cal(self,row,in_grand):
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
            in_grand += float(row['amount']) if none_to_str(row['amount']) else 0 
        else:
            in_grand += float(row['updated_price']) if none_to_str(row['updated_price']) else 0

        return in_grand

    def mail_workshop_subtot_cal(self,row):
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        if none_to_str(row['updated_price']) == 'NULL' or none_to_str(row['updated_price']) == '':
            p = float(row['amount']) if none_to_str(row['amount']) else 0 
        else:
            p = float(row['updated_price']) if none_to_str(row['updated_price']) else 0 

        return p
    

    def mail_workshop_list(self,workshop_lists,hand_id,total_grand_val):
        result = {}
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        table = ''
        for wh in workshop_lists:
            in_status = 0
            in_qty = 0
            in_grand = 0
            subrows = Handon_form_workshop.objects.values().filter(is_deleted=1,hand_id=hand_id,work_id=wh.id)
            if len(subrows)>0:
                in_status = 1
                in_qty = len(subrows)
                for row in subrows:
                    gnd_cal_res = self.mail_workshop_gnd_cal(row,in_grand)
                    in_grand += gnd_cal_res
                total_grand_val += in_grand
                table += '''<tr>
                        <td colspan="4" style="border-bottom: 1px dashed #e3e5e8;padding-left: 6px;">'''+ wh.name +''' ($'''+ str(wh.amount) +''')</td>
                    </tr>'''
                x = 1
                sub_total = 0
                for row in subrows:
                    sub_cal_res = self.mail_workshop_subtot_cal(row)
                    p = sub_cal_res
                    sub_total += p
                    table += '''<tr>
                                    <td style="border-bottom: 1px dashed #e3e5e8;padding-left:10px;">'''+ str(x) +'''</td>
                                    <td colspan="2" style="border-bottom: 1px dashed #e3e5e8;padding-left: 6px;">'''+ none_to_str(row['name']) +'''</td>
                                    <td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(p) +'''</td>
                                </tr>'''
                    x += 1
                table += '''<tr>
                            <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;"></td>
                            <td style="border-bottom: 1px dashed #e3e5e8;padding:6px 0px;"></td>
                            <td style="border-bottom: 1px dashed #e3e5e8;">Total</td>
                            <td style="border-bottom: 1px dashed #e3e5e8;">$'''+ str(sub_total) +'''</td>
                        </tr>'''

        result['in_status'] = in_status
        result['in_qty'] = in_qty
        result['in_grand'] = in_grand
        result['table'] = table
        result['total_grand_val'] = total_grand_val
        return result                
    

    def mail_template(self,form,hand_id):
        result = {}
        body = ''
        
        none_to_str=lambda a:str(a) if str(a) != 'None' else ''
        handon_res = (Handon_form.objects.values().filter(id=hand_id,status=1)[:1])[0]
        convention_ws = Convention_form_workshop.objects.filter(is_deleted=1,hand_id=hand_id).aggregate(con_ws_ids = GroupConcat('work_id'))
        handon_ws = Handon_form_workshop.objects.filter(is_deleted=1,hand_id=hand_id).aggregate(hands_ws_ids = GroupConcat('work_id'))
        if convention_ws:
            mail_temp_con_res = self.mail_temp_con(convention_ws)
            con_list = mail_temp_con_res['con_list']
            convention_lists = mail_temp_con_res['convention_lists']
        if handon_ws:
            mail_temp_ws_res = self.mail_temp_ws(handon_ws)
            workshop_lists = mail_temp_ws_res['workshop_lists']
            
        today_dt = dt.date.today() 
        if handon_res['created_on']:
            today_dt = handon_res['created_on'].date()

        get_price = Convention_types_prices.objects.values().filter(form_status=form,start_date__lte=today_dt,end_date__gte=today_dt).order_by('id')[:1]

        if get_price== '':
            return 'The deadline for all pre-registration is Expired'

        prices_list = json.loads(get_price[0]['bulk_price'])

        grand_price = none_to_str(handon_res['amount'])
        if handon_res['updated_grand_amount']:
            grand_price = none_to_str(handon_res['updated_grand_amount'])

        action = 1

        get_dynamic_thead_res = self.get_dynamic_thead(form,handon_res,grand_price)
        thank_mess = get_dynamic_thead_res['thank_mess']
        transaction_section = get_dynamic_thead_res['transaction_section']
        tbl_head = get_dynamic_thead_res['tbl_head']   

        table = ""
        if action == 1:
            get_dy_con_act_res = self.get_dynamic_content_action(tbl_head,convention_lists,con_list,hand_id,prices_list)
        table += get_dy_con_act_res['table']
        total_grand_val = get_dy_con_act_res['total_grand_val']
        count_workshop = len(workshop_lists)
        if count_workshop>0:
            table += '''<tr>
                            <th colspan="12">
                                <h4><strong>UDA - Hands on workshop Registration</strong></h4>
                            </th>
                        </tr>
                        <tr style="border: 1px dashed #ddd;color: #1c202a;">
                            <th style="width:10%;text-align:left;border-bottom: 1px dashed #e3e5e8;padding-left: 6px;"><strong>SL NO</strong></th>
                            <th colspan="2" style="width:80%;text-align:left;border-bottom: 1px dashed #e3e5e8;"><strong>NAME</strong></th>
                            <th style="width:10%;text-align:left;border-bottom: 1px dashed #e3e5e8;"><strong>Fee</strong></th>
                        </tr>'''


            mail_workshop_res = self.mail_workshop_list(workshop_lists,hand_id,total_grand_val)
            table += mail_workshop_res['table']


        amount_res = self.amount_calculation_fn(handon_res)
        updated_grand_amount_sec = amount_res['updated_grand_amount_sec']
        head_sec = "Registration " if handon_res['amount']==0 else "Transaction " 

        body += '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html>
            <head>
                <style>
                @media screen and (max-width: 500px) {
                    .mobile_col{display: block !important;width: 100% !important;}  .mobile_col1{display: block !important;width: 100% !important;margin-bottom: 10px;margin-top: 10px;}
                }
                </style>
            </head>
            <body>
                <div id="body">
                    <table border="0" width="100%" cellpadding="0" cellspacing="0" bgcolor="e8e8e8">
                        <tr>
                            <td height="90" style="font-size: 90px; line-height: 90px;">&nbsp;</td>
                        </tr>
                        <tr>
                            <td>
                                <table border="0" align="center" width="510" cellpadding="0" cellspacing="0" bgcolor="3b5ab2" class="container590 bodybg_color" style="border-top-left-radius: 4px; border-top-right-radius: 4px; width: 90% !important">
                                    <tr>
                                        <td height="7" style="font-size: 7px; line-height: 7px;">&nbsp;</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <table border="0" align="center" width="510" cellpadding="0" cellspacing="0" bgcolor="ffffff" style="width:90% !important" class="container590 bodybg_color">
                                    <tr>
                                        <!-- ======= logo ======= -->
                                        <td align="center" class="section-img">
                                            <a href="'''+ settings.EMAIL_URL +'''" style="display: block; border-style: none !important; border: 0 !important;"><img width="510" border="0" style="display: block; margin: 60px 0px 20px 0px; width: 270px;" src="'''+ settings.EMAIL_LOGO +'''" /></a>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td height="35" style="font-size: 35px; line-height: 35px;">&nbsp;</td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="color: #1c2029; font-size: 24px; font-family: "Varela Round", sans-serif; mso-line-height-rule: exactly; line-height: 30px;" class="title_color main-header">
                                            <!-- ======= section header ======= -->
                                            <div style="line-height: 30px;">'''+ thank_mess +'''</div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td height="20" style="font-size: 20px; line-height: 20px;">&nbsp;</td>
                                    </tr>
                                    <tr style=" float: left; width: 90%; margin: 0 5%;     font-family: "Varela Round", sans-serif;color: #1c202a; font-size: 14px; ">
                                        <td style=" width: 100%; display: block; ">
                                            <table style="width:100%">
                                                <tbody>
                                                    <tr>
                                                        <td class="mobile_col" style="border: 1px dashed #ddd;padding: 15px 0;border-radius: 10px;">
                                                            <h4 style="padding-left: 20px; font-size: 20px; margin-bottom: 0; margin-top: 0"><strong>User Details no</strong></h4>
                                                            <p style="margin-bottom: 5px; padding-left: 20px;"><strong>Practice Name :</strong> '''+ handon_res['practice_name']+'''</p>
                                                            <p style="margin-bottom: 5px; padding-left: 20px;"><strong>Name :</strong> '''+ handon_res['name'] + ' ' + handon_res['last_name'] +'''</p>
                                                            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Phone :</strong> '''+ handon_res['phone'] +''' </p>
                                                            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>E-Mail:</strong> '''+ handon_res['email'] +'''</p>
                                                            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Address :</strong> '''+ handon_res['address'] +', '+ handon_res['city'] +', '+ handon_res['state'] + '''. </p>
                                                            <p style="margin-bottom: 5px;padding-left: 20px;"><strong>Zip Code :</strong> '''+ handon_res['zipcode']+''' </p>
                                                        </td>
                                                        <td class="mobile_col1" style="border: 1px dashed #ddd;padding: 15px 0;border-radius: 10px;">'''+ transaction_section +'''
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                                    
                                    <tr>
                                        <td>
                                            <table border="0" align="center" cellpadding="0" cellspacing="0" style="width:100%;color: #1c202a;" class="container580">
                                                <tr>
                                                    <td align="center" style="color: #1c202a; font-size: 16px; font-family: "Varela Round", sans-serif; mso-line-height-rule: exactly; line-height: 24px;" class="resize-text text_color">
                                                        <div style="line-height: 24px">
                                                            <table style="width: 90%; border: 1px dashed #ddd;border-radius:10px;">
                                                                <tbody>
                                                                '''+ table + '''
                                                                <tr>
                                                                    <td style="padding:10px 0px;"></td>
                                                                    <td style="font-weight:600;padding:10px 0px;">Grand Total</td>
                                                                    <td style="font-weight:600;padding:10px 0px;">$'''+ str(handon_res['amount']) +'''</td>
                                                                </tr>'''+ updated_grand_amount_sec +'''
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td height="35" style="font-size: 35px; line-height: 35px;">&nbsp;</td>
                                    </tr>
                                    <!-- <tr>
                                        <td align="center">
                                            <table border="0" align="center" width="220" cellpadding="0" cellspacing="0" bgcolor="3b5ab2" style="margin: 5px 0px 15px 0px; border-radius: 50px; box-shadow: 0 1px 2px rgba(0,0,0,.3);" class="cta-button main_color">
                                                <tr>
                                                    <td height="13" style="font-size: 13px; line-height: 13px;">&nbsp;</td>
                                                </tr>
                                                <tr>
                                                    <td align="center" style="color: #ffffff; font-size: 14px; font-family: "Varela Round", sans-serif;" class="cta-text">
                                                        
                                                        <div style=" line-height: 24px;">
                                                            <a href="convention-on-transaction.php?p=id&e=email" style="font-size: 17px; color: #ffffff; text-decoration: none;">'''+ head_sec+'''Detail</a>
                                                        </div>
                                                    </td>
                                                </tr> 
                                                <tr>
                                                    <td height="13" style="font-size: 13px; line-height: 13px;">&nbsp;</td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>-->
                                    <tr>
                                        <td height="30" style="font-size: 30px; line-height: 30px;">&nbsp;</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                <table border="0" width="90%" align="center" cellpadding="0" cellspacing="0" bgcolor="f2f4f6" class="container590">
                                    <tr>
                                        <td height="20" style="font-size: 20px; line-height: 20px;">&nbsp;</td>
                                    </tr>
                                    <tr>
                                        <td align="center" style="color: #b0b7c7; font-size: 14px; font-family: "Questrial", sans-serif; mso-line-height-rule: exactly; line-height: 30px;" class="text_color">
                                            <div style="line-height: 30px">
                                                <!-- ======= section text ======= -->
                                                <a href="'''+ settings.EMAIL_URL +'''" style=" text-decoration: none; color: inherit; ">www.udainpy.in</a>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td height="20" style="font-size: 20px; line-height: 20px;">&nbsp;</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        <tr>
                            <td height="90" style="font-size: 90px; line-height: 90px;">&nbsp;</td>
                        </tr>
                    </table>
                </div>
            </body>
        </html>
        '''
        result = {
            'html':body,
            'plain':strip_tags(body)
        }

        return result    