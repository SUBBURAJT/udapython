from admin_uda.models import Hygienist
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import datetime as dt
import random
import csv

class hygienist():
    def add_hygienist(self,request):
        file=request
        logo_root = os.path.join(settings.MEDIA_ROOT, 'hygienist_upload/')
        logo_root=logo_root.replace("\\","/")
        al_e_a=[]
        invalid_ada=[]
        add_count=0
        c_all=0
        err=''
        today=dt.datetime.now()
        d=str(today.date())
        t=str(random.randint(111111111, 9999999999))
        ext='.csv'
        new_file_name='hygienist_upload_'+d+t+ext
        fs=FileSystemStorage(location=logo_root)
        fs.save(new_file_name,file)
        err="File Not Found"
        if os.path.exists('uploads/hygienist_upload/'+new_file_name):
            with open('uploads/hygienist_upload/'+new_file_name, newline='') as csvfile:
                datas = csv.reader(csvfile)
                headers = next(datas)
                de_header=['ID', 'First Name', 'Last Name', 'Address', 'City', 'State', 'Zip Code', 'Phone']
                if len(headers) == 8 and headers==de_header:
                    result=self.save_update(datas)
                    err=''
                    return {"exists_id":result['al_e_a'],"Added_id":result['add_count'],"err":err,'total_given':result['c_all'],'invalid_ada':result['invalid_ada']}
                else:
                    err="Please Upload a Correct row and columns"
        return {"exists_id":al_e_a,"Added_id":add_count,"err":err,'total_given':c_all,'invalid_ada':invalid_ada}

    def save_update(self,datas):
        rem_mul=lambda a:a.replace("\t"," ")
        c_all=0
        add_count=0
        al_e_a=[]
        invalid_ada=[]
        for fields in datas:
            if fields and fields[0]!='ID':
                    hy_id = rem_mul(fields[0])
                    first_name = rem_mul(fields[1])
                    last_name = rem_mul(fields[2])
                    address = rem_mul(fields[3])
                    city = rem_mul(fields[4])
                    state = rem_mul(fields[5])
                    hzip = rem_mul(fields[6])
                    phone = rem_mul(fields[7])
                    c_all+=1
                    if hy_id.isnumeric():
                        if Hygienist.objects.filter(hygienist_id = hy_id).exists():
                            form=Hygienist.objects.get(hygienist_id = hy_id)
                            form.hygienist_id = hy_id
                            form.first_name = first_name
                            form.last_name = last_name
                            form.address = address
                            form.city = city
                            form.state = state
                            form.zip = hzip
                            form.phone = phone
                            form.save()
                            al_e_a.append(hy_id)
                        else:
                            form=Hygienist()
                            form.hygienist_id = hy_id
                            form.first_name = first_name
                            form.last_name = last_name
                            form.address = address
                            form.city = city
                            form.state = state
                            form.zip = hzip
                            form.phone = phone
                            form.save()
                            add_count+=1
                    else:
                        invalid_ada.append(hy_id)
        return {"al_e_a":al_e_a,"add_count":add_count,"c_all":c_all,"invalid_ada":invalid_ada}


    def list_hygienist(self):
        data=Hygienist.objects.all()
        return data
    
