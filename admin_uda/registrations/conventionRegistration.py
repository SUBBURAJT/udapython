from admin_uda.models import Convention_types,Convention_types_prices,Handon_workshop,Handon_form,Convention_form_workshop,Handon_form_workshop,Send_Mail
from django.db.models import Count
import json
import datetime as dt
from admin_uda.registrations.registration import Registration
from django_mysql.models import GroupConcat
from django.conf import settings
import os

class ConventionRegistration():
    rt_qrcode = "/uploads/mail_qrcode/"
    rt_mailpdf = "/uploads/mail_pdf/"
    def get_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_convention(self,today):        
        convention_list = Convention_types.objects.filter(status=1,form_status=1)
        convention_prices = Convention_types_prices.objects.values().filter(form_status='1',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        prices_list = json.loads(convention_prices[0]['bulk_price'])
        cv_res = []
        for con in list(convention_list):
            cv = {}
            cv['id'] = con.id
            cv['name'] = con.name
            cv['price'] = prices_list[str(con.id)]
            cv_res.append(cv)
        return cv_res

    def get_worshop(self):
        workshop_list = Handon_workshop.objects.values('event_date').filter(status=1).annotate(dcnt = Count('event_date')).all()
        cv_res = []
        if(len(workshop_list) > 0):
            for workshop in workshop_list:                
                event_date = workshop['event_date']
                if(event_date!='' and event_date!='0000-00-00'):
                    ent_m = dt.datetime.strptime(str(event_date),'%Y-%m-%d').strftime('%b %d , %A, %Y')
                    workshop_list_am = Handon_workshop.objects.filter(status=1,timeslot=1,event_date=event_date).order_by('id')
                    workshop_list_pm = Handon_workshop.objects.filter(status=1,timeslot=2,event_date=event_date).order_by('id')
                    if len(workshop_list_am) > 0:
                        cv = {}
                        event_list = ''
                        event_list = 'CLICK HERE FOR '+ ent_m +' (AM) WORKSHOPS REGISTRATION'
                        cv['workshop'] = event_list
                        cv['workshop_slot'] = workshop_list_am
                        cv_res.append(cv)
                    if len(workshop_list_pm) > 0:
                        cv = {}
                        event_list = ''
                        event_list = 'CLICK HERE FOR '+ ent_m +' (PM) WORKSHOPS REGISTRATION'
                        cv['workshop'] = event_list
                        cv['workshop_slot'] = workshop_list_pm
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
            form_status = 1,            
            created_ip=self.get_ip(request),   
            created_on=dt.datetime.now(),
            created_by= request.session['user_id']
        )
        form_data.save()
        last_insert_id = form_data.id
        if last_insert_id:
            convention_type = request.POST.get('conventionType')
            convention_list = json.loads(convention_type)
            # workshop details
            workshops = request.POST.get('workshops')
            workshops_list = json.loads(workshops)
            
            no_wrkshop = 0
            a = int(dt.datetime.now().timestamp())
            if convention_list != [] and len(convention_list)>0:
                for cv in convention_list:
                    if cv['input'] and len(cv['input'])>0:
                        for val in cv['input']:
                            if val['name'] != '':
                                price = cv['price']
                                work_shop_form = Convention_form_workshop(
                                    sno = a,
                                    hand_id = last_insert_id,
                                    work_id = cv['id'],
                                    price = price,
                                    name = val['name'],
                                )
                                if cv['id'] == '1' or cv['id'] == '2' or cv['id'] == '5' or cv['id'] == '8' or cv['id'] == '15':
                                    work_shop_form.ada = val['ada'] if val['ada'] != '' else ''
                                else:
                                    work_shop_form.ada = ''

                                work_shop_form.save()
                                last_insert_wid = work_shop_form.id
                                no_wrkshop += last_insert_wid
            else:
                no_wrkshop = 1
            if workshops_list != [] and len(workshops_list)>0:
                for wh in workshops_list:
                    if wh['input'] and len(wh['input'])>0:
                        for val in wh['input']:
                            if val['wh_name'] != '':
                                price = wh['price']
                                work_shop_form = Handon_form_workshop(
                                    sno = a,
                                    hand_id = Handon_form.objects.get(id = last_insert_id),
                                    work_id = Handon_workshop.objects.get(id = wh['id']),
                                    amount = price,
                                    name = val['wh_name']
                                )
                                work_shop_form.save()
                                last_insert_wid = work_shop_form.id
                                no_wrkshop += last_insert_wid
            else:
                no_wrkshop = 1
                
            if no_wrkshop == 0:
                # delete
                data = Handon_form.objects.get(id=last_insert_id)
                data.delete()
                result = 0
            else:
                file = []
                rt = os.path.join(settings.BASE_DIR).replace("\\","/")
                body_content = Registration.mail_template(1,last_insert_id)
                file_name = Registration.mail_pdf(last_insert_id)
                file1 = rt+self.rt_mailpdf+file_name
                file.append(file1)
                qr_code = Registration.mail_qr_attachment(last_insert_id)
                if(qr_code['convention']):
                    for cv in qr_code['convention']:
                        tmp_file = ''
                        tmp_file = rt+self.rt_qrcode+ cv +'.pdf'
                        file.append(tmp_file)
                if(qr_code['workshops']):
                    for ws in qr_code['workshops']:
                        tmp_file = ''
                        tmp_file = rt+self.rt_qrcode+ ws +'.pdf'
                        file.append(tmp_file)

                
                txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'],file_name=file)
                if txt_res:
                    result = txt_res
                else:
                    result = 2
        else:
            result=0
        return result

    def get_form(self,hand_id):
        result = {}
        res = Handon_form.objects.values().filter(id = hand_id,status =1)
        
        if res:
            result = res[0]
            #get convention workshop            
            convention_ws = Convention_form_workshop.objects.values().filter(is_deleted=1,hand_id=hand_id)
            result['convention_ws'] = {}
            result['convention_ws']['cv_ws_ids']=[]
            for cv in convention_ws:                
                if (cv['work_id'] in result['convention_ws']) == False:
                    result['convention_ws'][cv['work_id']] = []
                    result['convention_ws']['cv_ws_ids'].append(cv['work_id'])
                result['convention_ws'][cv['work_id']].append(cv)

            if len(result['convention_ws']):                
                cnt_values = {}
                amt_values = {}
                for key,value in result['convention_ws'].items():
                    if key != 'cv_ws_ids':
                        cnt_values[key] = len(value)
                        amt = 0
                        for val in value:
                            amt += float(val['price'])
                        amt_values[key] = amt

                result['convention_ws']['cv_ws_cnt'] = cnt_values                
                result['convention_ws']['cv_ws_price'] = amt_values

            #get handon workshop
            handon_ws = Handon_form_workshop.objects.values().filter(is_deleted=1,hand_id=hand_id)
            result['handon_ws'] = {}
            result['handon_ws']['ws_ids']=[]
            for ws in handon_ws: 
                if (ws['work_id_id'] in result['handon_ws']) == False:
                    result['handon_ws'][ws['work_id_id']] = []
                    result['handon_ws']['ws_ids'].append(ws['work_id_id'])
                result['handon_ws'][ws['work_id_id']].append(ws)

            if len(result['handon_ws']):                
                cnt_values = {}
                amt_values = {}
                for key,value in result['handon_ws'].items():
                    if key != 'ws_ids':
                        cnt_values[key] = len(value)
                        amt = 0
                        for val in value:
                            amt += float(val['amount'])
                        amt_values[key] = amt

                result['handon_ws']['cv_ws_cnt'] = cnt_values                
                result['handon_ws']['cv_ws_price'] = amt_values
        return result

    def update_form(self,request,hand_id):
        if hand_id:
            form_data = Handon_form.objects.get(id=hand_id)
            form_data.practice_name = request.POST.get('practice_name')
            form_data.name = request.POST.get('first_name')
            form_data.last_name = request.POST.get('last_name')
            form_data.phone = request.POST.get('phone')
            form_data.email = request.POST.get('email')
            form_data.address = request.POST.get('address')
            form_data.city = request.POST.get('city')
            form_data.state = request.POST.get('state')
            form_data.zipcode = request.POST.get('zipcode')
            form_data.off_transaction_payment_details= request.POST.get('payment_details')
            form_data.off_transaction_memo= request.POST.get('memo')
            form_data.updated_on=dt.datetime.now()
            form_data.updated_ip=self.get_ip(request)
            form_data.updated_by= request.session['user_id']
            form_data.updated_grand_amount = request.POST.get('new_tot')
            form_data.balance_amount = request.POST.get('user_to_pay')
            form_data.save()

            last_insert_id = form_data.id
            if last_insert_id:
                convention_type = request.POST.get('conventionType')
               
                convention_list = json.loads(convention_type)
                # workshop details
                workshops = request.POST.get('workshops')
                workshops_list = json.loads(workshops)
                
                no_wrkshop = 0
                a = int(dt.datetime.now().timestamp())
                if convention_list != [] and len(convention_list)>0:
                    for cv in convention_list:
                        if cv['input'] and len(cv['input'])>0:
                            for val in cv['input']:
                                if val['name'] != '':
                                    price = cv['price']
                                    if 'hdn_cv_ws_id' in val:
                                        work_shop_form = Convention_form_workshop.objects.get(id=val['hdn_cv_ws_id'])
                                        work_shop_form.sno = a
                                        work_shop_form.hand_id = last_insert_id
                                        work_shop_form.work_id = cv['id']
                                        work_shop_form.price = price
                                        work_shop_form.name = val['name']
                                        if cv['id'] == '1' or cv['id'] == '2' or cv['id'] == '5' or cv['id'] == '8' or cv['id'] == '15':
                                            work_shop_form.ada = val['ada'] if val['ada'] != '' else ''
                                        else:
                                            work_shop_form.ada = ''

                                        work_shop_form.save()
                                        last_insert_wid = work_shop_form.id
                                        no_wrkshop += last_insert_wid
                                    else:
                                        work_shop_form = Convention_form_workshop(
                                            sno = a,
                                            hand_id = last_insert_id,
                                            work_id = cv['id'],
                                            price = price,
                                            name = val['name'],
                                        )
                                        if cv['id'] == '1' or cv['id'] == '2' or cv['id'] == '5' or cv['id'] == '8' or cv['id'] == '15':
                                            work_shop_form.ada = val['ada'] if val['ada'] != '' else ''
                                        else:
                                            work_shop_form.ada = ''

                                        work_shop_form.save()
                                        last_insert_wid = work_shop_form.id
                                        no_wrkshop += last_insert_wid
                else:
                    no_wrkshop = 1
                if workshops_list != [] and len(workshops_list)>0:
                    for wh in workshops_list:
                        if wh['input'] and len(wh['input'])>0:
                            for val in wh['input']:
                                if val['wh_name'] != '':
                                    price = wh['price']
                                    if 'hdn_ws_id' in val:
                                        work_shop_form = Handon_form_workshop.objects.get(id=val['hdn_ws_id'])
                                        work_shop_form.sno = a
                                        work_shop_form.hand_id = Handon_form.objects.get(id = last_insert_id)
                                        work_shop_form.work_id = Handon_workshop.objects.get(id = wh['id'])
                                        work_shop_form.amount = price
                                        work_shop_form.name = val['wh_name']
                                        work_shop_form.save()
                                        last_insert_wid = work_shop_form.id
                                        no_wrkshop += last_insert_wid
                                    else:
                                        work_shop_form = Handon_form_workshop(
                                            sno = a,
                                            hand_id = Handon_form.objects.get(id = last_insert_id),
                                            work_id = Handon_workshop.objects.get(id = wh['id']),
                                            amount = price,
                                            name = val['wh_name']
                                        )
                                        work_shop_form.save()
                                        last_insert_wid = work_shop_form.id
                                        no_wrkshop += last_insert_wid
                else:
                    no_wrkshop = 1
                    
                if no_wrkshop == 0:
                    # delete
                    data = Handon_form.objects.get(id=last_insert_id)
                    data.delete()
                    result = 0
                else:
                    file = []
                    rt = os.path.join(settings.BASE_DIR).replace("\\","/")
                    body_content = Registration.mail_template(1,last_insert_id)
                    file_name = Registration.mail_pdf(last_insert_id)
                    file1 = rt+self.rt_mailpdf+file_name
                    file.append(file1)
                    qr_code = Registration.mail_qr_attachment(last_insert_id)
                    if(qr_code['convention']):
                        for cv in qr_code['convention']:
                            tmp_file = ''
                            tmp_file = rt+self.rt_qrcode+ cv +'.pdf'
                            file.append(tmp_file)
                    if(qr_code['workshops']):
                        for ws in qr_code['workshops']:
                            tmp_file = ''
                            tmp_file = rt+self.rt_qrcode+ ws +'.pdf'
                            file.append(tmp_file)

                    
                    txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'],file_name=file)   

                    if txt_res:
                        result = txt_res
                    else:
                        result = 2
            else:
                result=0
        else:
            result=0
        return result