import json
from django.core.checks.messages import Error
from admin_uda.models import *
import datetime as dt
from admin_uda.registrations.registration import Registration
from django.conf import settings

class SpringRegistration():
    def get_convention_type():
        conventionList= Convention_types.objects.filter(status=1, from_status=2)
        return conventionList
    def get_convention_price(today):
        con_pric=Convention_types_prices.objects.values().filter(form_status=2,start_date__lte=today,end_date__gte=today).order_by('id')[:1]
    def get_convention(today):
        conventionList=Convention_types.objects.filter(status=1,form_status=2)
        con_pric=Convention_types_prices.objects.values().filter(form_status=2,start_date__lte=today,end_date__gte=today).order_by('id')[:1]
        price_list=json.loads(con_pric[0]['bulk_price'])
        con_list=[]
        for con in list(conventionList):
            con_dis={}
            con_dis['id']=con.id
            con_dis['name']=con.name
            con_dis['price']=price_list[str(con.id)]
            con_list.append(con_dis)
        return con_list

    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    def saveRegistration(request):
        error=''
        form=Handon_form()
        form.practice_name=request.POST.get('practice_name')
        form.name=request.POST.get('name')
        form.last_name=request.POST.get('last_name')
        form.phone=request.POST.get('phone')
        form.email=request.POST.get('email')
        form.address=request.POST.get('address')
        form.city=request.POST.get('city')
        form.state=request.POST.get('state')
        form.zipcode=request.POST.get('zipcode')
        off_tr_date=dt.datetime.strptime(request.POST.get('off_transaction_created_date'), '%m/%d/%Y').strftime('%Y-%m-%d')
        form.off_transaction_created_date=off_tr_date
        form.off_transaction_id=request.POST.get('off_transaction_id')
        form.off_transaction_payment_mode=request.POST.get('off_transaction_payment_mode')
        form.off_transaction_payment_details=request.POST.get('off_transaction_payment_details')
        form.off_transaction_memo=request.POST.get('off_transaction_memo')
        form.off_transaction_status=2
        form.amount = request.POST.get('gnd_tot') 
        form.status=1
        form.form_status=2
        form.created_ip=SpringRegistration.get_ip(request)    
        form.created_on=dt.datetime.now()
        form.created_by=request.session['user_id']
        form.os=request.POST.get('os')
        form.browser=request.POST.get('browser')
        form.mobile_true=request.POST.get('mobile_true')
        form.screen_size=request.POST.get('screen_size')
        form.user_agent=request.POST.get('user_agent')
        form.form=1

        form.save()
        LastInsertId=form.id 
        if LastInsertId:
            conventionType = request.POST.get('conventionType')
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
                                if cv['id'] == '21':
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
                    file = []
                    rt = os.path.join(settings.BASE_DIR).replace("\\","/")
                    body_content = Registration.mail_template(2,LastInsertId)   
                    file_name = Registration.mail_pdf(LastInsertId)
                    file1 = rt+'/uploads/mail_pdf/'+file_name
                    file.append(file1)
                    qr_code = Registration.mail_qr_attachment(LastInsertId)
                    if(qr_code['convention']):
                        for cv in qr_code['convention']:
                            tmp_file = ''
                            tmp_file = rt+'/uploads/mail_qrcode/'+ cv +'.pdf'
                            file.append(tmp_file)
                    
                    txt_res=Send_Mail.Send(subject='UDA Registration Mail',body=body_content['plain'],to_mail='rajiveorchids@gmail.com',html_message=body_content['html'],file_name=file)
                    if txt_res:
                        result = txt_res
                    else:
                        result = 2
            else:
                result = 1
        else:
            result=0
        return result