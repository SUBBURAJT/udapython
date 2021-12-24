from admin_uda.models import *
from django.db.models import Count
import json
import datetime as dt
from admin_uda.registrations.registration import Registration

class ConventionRegistration():
    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_convention(today):
        conventionList = Convention_types.objects.filter(status=1,form_status=1)
        convention_prices = Convention_types_prices.objects.values().filter(form_status='1',start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        prices_list = json.loads(convention_prices[0]['bulk_price'])
        cv_res = []
        for con in list(conventionList):
            cv = {}
            cv['id'] = con.id
            cv['name'] = con.name
            cv['price'] = prices_list[str(con.id)]
            cv_res.append(cv)
        return cv_res

    def get_worshop():
        workshopList = Handon_workshop.objects.values('event_date').filter(status=1).annotate(dcnt = Count('event_date')).all()
        cv_res = []
        if(len(workshopList) > 0):
            for workshop in workshopList:                
                event_date = workshop['event_date']
                if(event_date!='' and event_date!='0000-00-00'):
                    ent_m = dt.datetime.strptime(str(event_date),'%Y-%m-%d').strftime('%b %d , %A, %Y')
                    workshopListAM = Handon_workshop.objects.filter(status=1,timeslot=1,event_date=event_date).order_by('id')
                    workshopListPM = Handon_workshop.objects.filter(status=1,timeslot=2,event_date=event_date).order_by('id')
                    if len(workshopListAM) > 0:
                        cv = {}
                        event_list = ''
                        event_list = 'CLICK HERE FOR '+ ent_m +' (AM) WORKSHOPS REGISTRATION'
                        cv['workshop'] = event_list
                        cv['workshop_slot'] = workshopListAM
                        cv_res.append(cv)
                    if len(workshopListPM) > 0:
                        cv = {}
                        event_list = ''
                        event_list = 'CLICK HERE FOR '+ ent_m +' (PM) WORKSHOPS REGISTRATION'
                        cv['workshop'] = event_list
                        cv['workshop_slot'] = workshopListPM
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
            form_status = 1,            
            created_ip=ConventionRegistration.get_ip(request),   
            created_on=dt.datetime.now(),
            created_by=1,
        )
        form_data.save()
        LastInsertId = form_data.id
        if LastInsertId:
            conventionType = request.POST.get('conventionType')
            conventionList = json.loads(conventionType)
            # workshop details
            workshops = request.POST.get('workshops')
            workshopsList = json.loads(workshops)
            
            no_wrkshop = 0
            a = int(dt.datetime.now().timestamp())
            if conventionList != [] and len(conventionList)>0:
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
                                    # email = val['email']
                                )
                                if cv['id'] == '1' or cv['id'] == '2' or cv['id'] == '5' or cv['id'] == '8' or cv['id'] == '15':
                                    workShopForm.ada = val['ada'] if val['ada'] != '' else ''
                                else:
                                    workShopForm.ada = ''

                                workShopForm.save()
                                LastInsertWID = workShopForm.id
                                no_wrkshop += LastInsertWID
            else:
                no_wrkshop = 1
            if workshopsList != [] and len(workshopsList)>0:
                for wh in workshopsList:
                    if wh['input'] and len(wh['input'])>0:
                        for val in wh['input']:
                            if val['wh_name'] != '':
                                price = wh['price']
                                workShopForm = Handon_form_workshop(
                                    sno = a,
                                    hand_id = Handon_form.objects.get(id = LastInsertId),
                                    work_id = Handon_workshop.objects.get(id = wh['id']),
                                    amount = price,
                                    name = val['wh_name']
                                )
                                workShopForm.save()
                                LastInsertWID = workShopForm.id
                                no_wrkshop += LastInsertWID
            else:
                no_wrkshop = 1
                
            if no_wrkshop == 0:
                # delete
                data = Handon_form.objects.get(id=LastInsertId)
                data.delete()
                result = 0
            else:
                body_content = Registration.mail_template(1,LastInsertId)   
                txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'])
                if txt_res:
                    result = txt_res
                else:
                    result = 2
        else:
            result=0
        return result