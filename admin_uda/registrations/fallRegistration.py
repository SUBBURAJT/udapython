from django.http.response import JsonResponse
from admin_uda.models import *
import json
import datetime as dt
from admin_uda.registrations.registration import Registration


class FallRegistration():
    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_convention(today):
        conventionList = Convention_types.objects.filter(status=1,form_status=3)
        convention_prices = Convention_types_prices.objects.values().filter(form_status='3',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        prices_list = json.loads(convention_prices[0]['bulk_price'])
        cv_res = []
        for con in list(conventionList):
            cv = {}
            cv['id'] = con.id
            cv['name'] = con.name
            cv['price'] = prices_list[str(con.id)]
            cv_res.append(cv)

        return cv_res
        
    def save_form(request):
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
            created_ip=FallRegistration.get_ip(request),   
            created_on=dt.datetime.now(),
            created_by=1,
        )
        form_data.save()
        LastInsertId = form_data.id
        if LastInsertId:
            conventionType = request.POST.get('conventionType')
            # if conventionType != '':
            conventionList = json.loads(conventionType)
            if conventionList != [] and len(conventionList)>0:
                no_wrkshop = 0
                a = int(dt.datetime.now().timestamp())
                for cv in conventionList:
                    if cv['input'] and len(cv['input'])>0:
                        for val in cv['input']:
                            if val['name'] != '':
                                price = cv['price']
                                workShopForm = Convention_form_workshop(
                                    sno = a,
                                    hand_id = LastInsertId,
                                    work_id = cv['id'],
                                    price = price,
                                    name = val['name'],
                                    email = val['email']
                                )
                                if cv['id'] == '25' or cv['id'] == '26':
                                    workShopForm.ada = ''
                                else:
                                    workShopForm.ada = val['ada'] if val['ada'] != '' else ''

                                workShopForm.save()
                                LastInsertWID = workShopForm.id
                                no_wrkshop += LastInsertWID
                if no_wrkshop == 0:
                    # delete
                    data = Handon_form.objects.get(id=LastInsertId)
                    data.delete()
                    result = 0
                else:
                    body_content = Registration.mail_template(3,LastInsertId)
                    txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'])
                    if txt_res:
                        result = txt_res
                    else:
                        result = 2
            else:
                result = 1
        else:
            result=0
        return result

    def get_convention_type():
        conventionList = Convention_types.objects.filter(status=1,form_status=3)
        return conventionList
    def get_convention_prices(today):
        convention_prices = Convention_types_prices.objects.values().filter(form_status='3',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        return convention_prices