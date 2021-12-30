from django.db.models.aggregates import Count
from django.db.models import Q , FilteredRelation
from admin_uda.models import *
from django.contrib.auth.hashers import make_password,check_password
import datetime
from django.contrib.auth.models import User

class user_managements():
 
    def get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def add_user_management(request):
        err=""
        msg = ""
        err_cnt = 0
        req_email = request.POST.get('email')
        req_id = request.POST.get('data_id')
        req_name = request.POST.get('name')
        req_mobile = request.POST.get('mobile')
        req_password = request.POST.get('password')
        id=request.session['user_id']
        print(id)
        
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
                user.modified_ip = user_managements.get_ip(request)
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
                user.created_ip = user_managements.get_ip(request)
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

    def list_user_management(request):
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