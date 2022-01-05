from django.db import models
from django.db.models.deletion import CASCADE
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from uda.settings import DEFAULT_FROM_EMAIL,TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,TWILIO_FROM_NUMBER,TWILIO_COUNTRY_CODE
from django.core.mail import send_mail,EmailMessage

class Send_Sms():

    def Send(**data):
        msg_text=data['msg_txt']
        to_number=data['to_number']
        sid=''
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages \
            .create(
            body=msg_text,
            from_=TWILIO_FROM_NUMBER,
            to=TWILIO_COUNTRY_CODE+to_number
            )
            sid=message.sid
        except TwilioRestException as err:
            sid=''
        return sid

class Send_Mail():
    def Send(**data):
        subject=data['subject']
        body=data['body']
        to_mail=data['to_mail']
        html_message = data['html_message'] if data['html_message'] else None
        attachment = data['file_name'] if data['file_name'] else None
        is_sent=1
        
        try:
            # send_mail(subject, body,DEFAULT_FROM_EMAIL,[to_mail],fail_silently= False,html_message=html_message )
            email_msg = EmailMessage(
                subject = subject,
                body = body,
                from_email = DEFAULT_FROM_EMAIL,
                to = [to_mail],                
            )
            if html_message !=None:
                email_msg.content_subtype = "html"
                email_msg.body = html_message
            if attachment!=None:
                for file in attachment:
                    if os.path.isfile(file):
                        email_msg.attach_file(file)  
            email_msg.send()
        except Exception as e:
            is_sent=str(e)
        return is_sent

class default_functions():
    def get_payment_method(self,method):
        payment = {
            '1':"Cash",
            '2':"Cheque/DD",
            '3':"POS",
            '4':"Venmo",
            '5':"Others"
        }
        result = ''
        try:
            result = payment[method]
        except Exception as e:    
            result = ''
        return result 

    def check_key_val(self,key,list):
        value = ''
        if key in list:
            value = list[key]
        return value

        
# Create your models here.
class Users(models.Model):
    name = models.CharField(max_length=200,null=True,db_index=True)
    username = models.CharField(max_length=50,db_index=True)
    password = models.CharField(max_length=250,db_index=True)
    email = models.CharField(max_length=200,db_index=True)
    mobile = models.CharField(max_length=20,null=True,db_index=True)
    reset_pass = models.CharField(max_length=250,null=True)
    profile_img = models.CharField(max_length = 255,null=True)
    profile_img_status = models.IntegerField(default=0)
    auth_user_id=models.IntegerField(default=0)
    role = models.CharField(max_length=20,null=True)
    status = models.SmallIntegerField(default=1)
    api_random_key = models.CharField(max_length=250,null=True)
    created_by = models.IntegerField(null=True)
    created_at = models.DateTimeField(editable=True,null=True)
    created_ip = models.CharField(max_length=50,null=True)
    modified_by = models.IntegerField(null=True)
    modified_at = models.DateTimeField(editable=True,null=True)
    modified_ip = models.CharField(max_length=50,null=True)
    deleted_by = models.IntegerField(null=True)
    deleted_at = models.DateTimeField(editable=True,null=True)
    deleted_ip = models.CharField(max_length=50,null=True)

class Ada_membership(models.Model):
    Membership_id=models.BigIntegerField(unique=True)
    Prefix  =	models.CharField(max_length=3,null=True)		
    ADA_Number  =	models.IntegerField(null=False)	
    Last_Name  =	models.CharField(max_length=70,null=True)		
    First_Name  =	models.CharField(max_length=70,null=True)		
    Middle_Name  =	models.CharField(max_length=70,null=True)		
    Suffix  =	models.CharField(max_length=10,null=True)			
    Constituent_Current_Level  =	models.CharField(max_length=2,null=True)
    Retirement_Date  =	models.CharField(max_length=25,null=True)	
    Primary_Function  =	models.CharField(max_length=7,null=True)	
    Phone  =	models.CharField(max_length=15,null=True)			
    Member_Type  =	models.CharField(max_length=20,null=True)		
    Address_Line_1  =	models.CharField(max_length=100,null=True)		
    Address_Line_2  =	models.CharField(max_length=50,null=True)	
    Address_Line_3  =	models.CharField(max_length=50,null=True)	
    City  =	models.CharField(max_length=50,null=True)
    State  =	models.CharField(max_length=10,null=True)
    Zip_Code  =	models.CharField(max_length=15,null=True)
    MembershipYear  =	models.CharField(max_length=4,null=True)
    PracticeName  =	models.CharField(max_length=70,null=True)
    Component_Jurisdiction  =	models.CharField(max_length=4,null=True)
    
class Hygienist(models.Model):
    hygienist_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=100,null=True)
    city = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=10,null=True)
    zip = models.CharField(max_length=15,null=True)
    phone = models.CharField(max_length=15,null=True)

class Handon_workshop(models.Model):
    event_date = models.DateField(null=True)
    timeslot = models.SmallIntegerField(default=1)
    speaker_name = models.CharField(max_length=200,null=True)
    name = models.CharField(max_length=255,null=True)
    amount = models.CharField(max_length=10,null=True)
    status = models.SmallIntegerField(default=0)
    qty = models.SmallIntegerField(default=0)
    total_hours = models.BigIntegerField(null=True)
    options = models.SmallIntegerField(default=1)

class Handon_form(models.Model):
    form = models.SmallIntegerField(default=0)
    archive_id = models.BigIntegerField(default=0)
    practice_name = models.CharField(max_length=120,null=True)
    name = models.CharField(max_length=50,null=True)
    last_name = models.CharField(max_length=50,null=True)
    phone = models.CharField(max_length=50,null=True)
    email = models.CharField(max_length=200,null=True)
    address = models.TextField()
    city = models.CharField(max_length=80,null=True)
    state = models.CharField(max_length=80,null=True)
    zipcode = models.CharField(max_length=15,null=True)
    off_transaction_created_date = models.DateTimeField(null=True)
    off_transaction_id = models.CharField(max_length=20,null=True)
    off_transaction_payment_mode = models.CharField(max_length=20,null=True)
    off_transaction_payment_details = models.CharField(max_length=100,null=True)
    off_transaction_memo = models.CharField(max_length=255,null=True)
    off_transaction_status = models.BigIntegerField(default=1)
    status = models.SmallIntegerField(default=0)
    transaction_id = models.CharField(max_length=20,null=True)
    transaction_ref = models.CharField(max_length=20,null=True)
    amount = models.FloatField(null=True)
    updated_grand_amount = models.FloatField(null=True)
    balance_amount = models.FloatField(null=True)
    transaction_status = models.CharField(max_length=30,null=True)
    reason_code = models.CharField(max_length=10,null=True)
    reason_text = models.TextField()
    card_type = models.CharField(max_length=50,null=True)
    account_number = models.CharField(max_length=30,null=True)
    transaction_on = models.DateTimeField(editable=True,null=True)
    os = models.CharField(max_length=100,null=True)
    browser = models.CharField(max_length=100,null=True)
    mobile_true = models.CharField(max_length=10,null=True)
    screen_size = models.CharField(max_length=20,null=True)
    user_agent = models.CharField(max_length=255,null=True)
    form_status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(editable=True,null=True)
    created_ip = models.CharField(max_length=50,null=True)
    updated_by = models.IntegerField(null=True)
    updated_on = models.DateTimeField(editable=True,null=True)
    updated_ip = models.CharField(max_length=50,null=True)
    deleted_by = models.IntegerField(null=True)
    deleted_on = models.DateTimeField(editable=True,null=True)
    deleted_ip = models.CharField(max_length=50,null=True)


class Handon_form_workshop(models.Model):
    sno = models.IntegerField(null=True)
    hand_id = models.ForeignKey(Handon_form,on_delete=CASCADE)
    work_id = models.ForeignKey(Handon_workshop,on_delete=CASCADE)
    amount = models.CharField(max_length=10,null=True)
    name = models.CharField(max_length=200,null=True)
    email = models.CharField(max_length=100,null=True)
    mobile = models.CharField(max_length=20,null=True)
    updated_price = models.CharField(max_length=20,null=True)
    is_deleted = models.SmallIntegerField(default=1)
    deleted_by = models.IntegerField(null=True)
    deleted_on = models.DateTimeField(editable=True,null=True)

class Convention_types(models.Model):
    name = models.CharField(max_length=255,null=True)
    status = models.SmallIntegerField(default=0)
    form_status = models.SmallIntegerField(default=1)

class Convention_types_prices(models.Model):
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    bulk_price = models.TextField()
    form_status = models.SmallIntegerField(default=1)

class Convention_form_workshop(models.Model):
    sno = models.CharField(max_length=15,null=True)
    hand_id = models.IntegerField(null=True)
    work_id = models.IntegerField(null=True)
    price = models.CharField(max_length=10,null=True)
    name = models.CharField(max_length=255,null=True)
    email = models.CharField(max_length=255,null=True)
    ada = models.CharField(max_length=30,null=True)
    updated_price = models.CharField(max_length=20,null=True)
    is_deleted = models.SmallIntegerField(default=1)
    delted_by = models.IntegerField(null=True)
    deleted_on = models.DateTimeField(editable=True,null=True)

class Id_prints(models.Model):
    con_type = models.SmallIntegerField(null=False)
    ref_id = models.IntegerField(null=False)
    printing_date_time = models.DateTimeField(editable=True,null=True)
    dev_id = models.CharField(max_length=70,null=True)
    dev_os = models.SmallIntegerField(null=True)
    parent_id = models.CharField(max_length=20,null=True)

class Convention_archive(models.Model):
    archive = models.CharField(max_length=20,null=True)

class Message_center(models.Model):
    message = models.CharField(max_length=255,null=True)
    reg_type = models.IntegerField(null=True)
    type_of_member = models.IntegerField(null=True)
    uni_con_id = models.TextField(null=True)
    status = models.SmallIntegerField(default=0)
    created_by = models.IntegerField(null=True)
    created_on = models.DateTimeField(editable=True,null=True)
    created_ip = models.CharField(max_length=50,null=True)
    deleted_by = models.IntegerField(null=True)
    deleted_on = models.DateTimeField(editable=True,null=True)
    deleted_ip = models.CharField(max_length=50,null=True)

class Message_center_ref(models.Model):
    ref_id = models.IntegerField(null=True)
    number = models.CharField(max_length=15,null=True)
    message_id = models.CharField(max_length=50,null=True)
    triggered_status = models.SmallIntegerField(null=True)
    triggered_time = models.DateTimeField(editable=True,null=True)
    uni_con_id = models.IntegerField(null=True)

class Vendor_registration_form(models.Model):
    company_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    zipcode = models.CharField(max_length=15)
    created_on = models.DateTimeField(editable=True,null=True)
    status = models.SmallIntegerField(default=1)

class Vendor_employees(models.Model):
    vendor_id = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    qr_code_png = models.CharField(max_length=255,null=True)
    qr_code_pdf = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(editable=True,null=True)
    modified_at = models.DateTimeField(editable=True,null=True)