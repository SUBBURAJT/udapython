from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import Send_Mail, Users
from django.utils.html import strip_tags

from django.contrib.auth.hashers import make_password,check_password
import datetime
from django.contrib.auth.models import User
import re
from hashids import Hashids
import random
class user_managements():
 
    def get_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def add_user_management(self,request):
        err=""
        msg = ""
        err_cnt = 0
        req_email = request.POST.get('email')
        req_id = request.POST.get('data_id')
        req_name = request.POST.get('name')
        req_mobile = request.POST.get('mobile')
        req_password = request.POST.get('password')
        id=request.session['user_id']
        
        if req_id:
            if (req_email != '' and req_name !='' and req_mobile!='' ):
                user = Users.objects.get(id=req_id)
                user.name = req_name
                user.email = req_email
                user.mobile = req_mobile
                auth_id=user.auth_user_id 
                
                if req_password!='':
                    user.password   = make_password(request.POST.get('password'))                
                # user.role       = "User"
                user.modified_at = datetime.datetime.now()
                user.modified_ip = self.get_ip(request)
                user.modified_by = id
                if Users.objects.filter(~Q(id=req_id), email=req_email,status=1).exists():
                    err_cnt = 1
                    err = 'Email Already Exists'
                if err_cnt == 0:  
                    user.save()
                    #Udate auth_user table
                    auth_user = User.objects.get(id=auth_id)
                    auth_user.username=req_email
                    auth_user.email=req_email
                    if req_password!='':
                        auth_user.password   = user.password
                    auth_user.save()  

                    msg =  "User updated Successfully"                    
            else:
                err = "User Added Failed! Missing reqired fields"
        
        elif (req_email != '' and req_name !='' and req_mobile!='' and req_password!='' ):
                user = Users(
                    name = req_name,
                    email = req_email,
                    mobile = req_mobile,
                   
                )
                user.password   = make_password(request.POST.get('password'))                
                user.role       = "User"
                user.created_at = datetime.datetime.now()
                user.created_ip = self.get_ip(request)
                user.created_by = id

                if Users.objects.filter(email=req_email,status=1).exists():
                    err_cnt = 1
                    err = 'Email Already Exists'
                else:
                    #Save To auth_user table 
                    auth_user = User.objects.create(username=req_email, email=req_email, password=user.password)
                    auth_user.save()
                    lastid=auth_user.id
                    user.auth_user_id=lastid
                    user.save()
                    msg = "User Added Successfully"
        else:
            err = "User not added"
        return {"error":err,"msg":msg}

    def list_user_management(self,request):
        qry=Users.objects.filter(status=1,role="User")
        nd=[]
        res={}
        j=0
        for datas in qry:
            name_ltr = datas.name[:1]
            name = datas.name
            cl_names=["bg-soft-primary text-primary","bg-soft-success text-success","bg-soft-warning text-warning"]
            name="""<div class="d-flex align-items-center">
                        <div class="activity-icon avatar-xs me-2">
                            <span class="avatar-title """+cl_names[(j%3)]+""" br-5">
                        """+name_ltr.upper()+"""</span>
                        </div>
                        """+name.capitalize()+"""
                    </div>"""
            email = datas.email
            mobile = datas.mobile
            nestedData=[]
            nestedData.append(name)
            nestedData.append(email)
            nestedData.append(mobile)
            actions="""
           
            <a href="javascript:void(0);" data-id="""+str(datas.id)+"""  class="me-3 text-primary edit_user_management edit_user_act" data-bs-container="#tooltip-container1" data-bs-toggle="tooltip" data-bs-placement="top" title="Edit"><i class="mdi mdi-pencil font-size-18"></i></a>

            <a href="#"  data-id="""+str(datas.id)+"""  class="text-danger tabDelete"  data-bs-container="#tooltip-container1"""+str(j)+"""" data-bs-toggle="tooltip" data-bs-placement="top" title="Delete"><i class="mdi mdi-trash-can font-size-18"></i></a>"""
            nestedData.append(actions)
            nd.append(nestedData)
            j+=1

        res['data']=nd
        return res

    def reset_pass_mail(self,request):
        err=''
        txt_res=''
        email=request.POST.get('email')
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            check_ext=Users.objects.filter(email=email,status=1).exists()
            err=""
            if check_ext:
                hashids = Hashids(salt='UDAHEALTHDENTALSALT',min_length=20)
                rand=random.randint(12345678909999999999,99999999991234567890)
                hashid = hashids.encode(rand) 
                update_pass=Users.objects.get(email=email)
                update_pass.reset_pass=hashid
                update_pass.save()
                body="""<div>
                        <table border="0" align="center" cellpadding="0" cellspacing="0"
                            style='margin: 10px auto;width: 600px; min-width: 400px;background: #fff;'>
                            <tbody>
                                <tr>
                                    <td style='text-align: center;padding: 25px 0 20px;'>
                                        <img src="https://udainpy.in/static/images/uda-logo-blue.png" style='height: 55px' alt="Logo">
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style='padding:0 20px 20px;'>
                                        <table border="0" align="center" cellpadding="0" cellspacing="0"
                                            style='text-align: center;background: #f2f3f9d6; width: 100%;'>
                                            <tbody>
                                                <tr>
                                                    <td style='padding: 20px 0;'>
                                                        <img src="https://udainpy.in/static/images/mailLock.png" height='140px' alt="">

                                                        <h5
                                                            style="font-size: 25px;font-family: 'Raleway', sans-serif;margin: 15px 0 8px;font-weight: 600;">
                                                            Forgot your password?</h5>
                                                        <p style="font-size: 16px;font-family: 'Raleway', sans-serif;margin-top: 0;">Click
                                                            below to reset your password
                                                        </p>
                                                        <a href="https://udainpy.in/reset-password/"""+hashid+"""/"""+email+"""
                                                            style="color: #fff !important;padding: 10px; width: 100%; text-align: center;background: #6259ca;display: block;text-transform: uppercase;font-size: 14px;font-family: 'Raleway', sans-serif;max-width: 300px;margin: 30px auto 10px; text-decoration: none !important;">Reset
                                                            your password</a>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>"""
                plain_message = strip_tags(body)
                txt_res=Send_Mail.Send(subject='Reset Password Confirmation',body=plain_message,to_mail=email,html_message=body,file_name='')
            else:
                err="Couldn't find your email"
        else:
            err="Please enter a Valid Email Address"
        return {"err":err,"txt_res":txt_res}

    def reset_password_submit(self,request):
        res=0
        new_password=request.POST.get('new_password')
        hidden_id=request.POST.get('hidden_id')
        form_for=Users.objects.get(id=hidden_id)
        form_for.password=make_password(new_password)
        form_for.reset_pass=''
        form_for.save()
        auth_user = User.objects.get(id=form_for.auth_user_id)
        auth_user.password=make_password(new_password)
        auth_user.save()     
        if auth_user.id>0:
            res=1
        return {"res":res}  