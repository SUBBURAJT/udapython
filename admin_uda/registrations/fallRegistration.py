from django.http.response import JsonResponse
from admin_uda.models import Convention_types,Convention_types_prices,Handon_form,Convention_form_workshop,Send_Mail
import json
import datetime as dt
from admin_uda.registrations.registration import Registration
from django.conf import settings
import os

class FallRegistration():
    def get_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_convention(self,today):
        convention_list = Convention_types.objects.filter(status=1,form_status=3)
        convention_prices = Convention_types_prices.objects.values().filter(form_status='3',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        prices_list = json.loads(convention_prices[0]['bulk_price'])
        cv_res = []
        for con in list(convention_list):
            cv = {}
            cv['id'] = con.id
            cv['name'] = con.name
            cv['price'] = prices_list[str(con.id)]
            cv_res.append(cv)

        return cv_res
        
    def save_form(self,request):
        form_data = Handon_form(
            form = 1,
            practice_name = request.POST.get('practice_name'),
            name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name'),
            phone = request.POST.get('phone'),
            email = request.POST.get('email'),
            address = request.POST.get('address'),
            city = request.POST.get('city'),
            state = request.POST.get('state'),
            zipcode = request.POST.get('zipcode'),
            off_transaction_created_date= dt.datetime.strptime(request.POST.get('transaction_date'), '%m/%d/%Y').strftime('%Y-%m-%d'), 
            off_transaction_id= request.POST.get('transaction_id'),
            off_transaction_payment_mode= request.POST.get('payment_mode'),
            off_transaction_payment_details= request.POST.get('payment_details'),
            off_transaction_memo= request.POST.get('memo'),
            amount = request.POST.get('gnd_tot'),
            off_transaction_status=2,
            os = request.POST.get('os'),
            browser = request.POST.get('browser'),
            mobile_true = request.POST.get('mobile_true'),
            screen_size = request.POST.get('screen_size'),
            user_agent = request.POST.get('user_agent'),   
            status = 1,         
            form_status = 3,            
            created_ip=self.get_ip(request),   
            created_on=dt.datetime.now(),
            created_by=request.session['user_id'],
        )
        form_data.save()
        last_insert_id = form_data.id
        if last_insert_id:
            convention_type = request.POST.get('conventionType')
            # if convention_type != '':
            convention_list = json.loads(convention_type)
            if len(convention_list)>0:
                no_wrkshop = 0
                res = self.save_convention(last_insert_id,convention_list)
                no_wrkshop = res
                
                if no_wrkshop == 0:
                    # delete
                    data = Handon_form.objects.get(id=last_insert_id)
                    data.delete()
                    result = 0
                else:
                    result = self.mail_pdf_func(last_insert_id)
            else:
                result = 1
        else:
            result=0
        return result

    def save_convention(self,last_insert_id,convention_list):
        a = int(dt.datetime.now().timestamp())
        no_wrkshop = 0
        for cv in convention_list:
            if len(cv['input'])>0:
                for val in cv['input']:
                    if val['name'] != '':
                        price = cv['price']
                        work_shop_form = Convention_form_workshop(
                            sno = a,
                            hand_id = last_insert_id,
                            work_id = cv['id'],
                            price = price,
                            name = val['name'],
                            email = val['email']
                        )
                        work_shop_form.ada = ''    
                        if 'ada' in val:
                            work_shop_form.ada = val['ada'] 
                        work_shop_form.save()
                        last_insertwid = work_shop_form.id
                        no_wrkshop += last_insertwid
        return no_wrkshop

    def mail_pdf_func(self,last_insert_id):
        reg_obj = Registration()
        file = []
        rt = os.path.join(settings.BASE_DIR).replace("\\","/")
        body_content = reg_obj.mail_template(3,last_insert_id)
        file_name = reg_obj.mail_pdf(last_insert_id)
        file1 = rt+self.rt_mailpdf+file_name
        file.append(file1)
        qr_code = reg_obj.mail_qr_attachment(last_insert_id)
        if(qr_code['convention']):
            for cv in qr_code['convention']:
                tmp_file = ''
                tmp_file = rt+self.rt_qrcode+ cv +'.pdf'
                file.append(tmp_file)    
        txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'],file_name=file)   
        if txt_res:
            result = txt_res
        else:
            result = 2
        return result

    def get_convention_type(self):
        convention_list = Convention_types.objects.filter(status=1,form_status=3)
        return convention_list
    def get_convention_prices(self,today):
        convention_prices = Convention_types_prices.objects.values().filter(form_status='3',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        return convention_prices