from admin_uda.models import *
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import datetime as dt
import random
import csv

class hygienist():
    def add_hygienist(request):
        file=request
        logoRoot = os.path.join(settings.MEDIA_ROOT, 'hygienist_upload/')
        logoRoot=logoRoot.replace("\\","/")
        al_e_a=[]
        ids=[]
        invalid_ada=[]
        al_e=0
        add_count=0
        c_all=0
        err=''
        today=dt.datetime.now()
        d=str(today.date())
        t=str(random.randint(111111111, 9999999999))
        ext='.csv'
        new_file_name='hygienist_upload_'+d+t+ext
        fs=FileSystemStorage(location=logoRoot)
        filename=fs.save(new_file_name,file)
        rem_mul=lambda a:a.replace("\t"," ")
        if os.path.exists('uploads/hygienist_upload/'+new_file_name):
            with open('uploads/hygienist_upload/'+new_file_name, newline='') as csvfile:
                datas = csv.reader(csvfile)
                headers = next(datas)
                de_header=['ID', 'First Name', 'Last Name', 'Address', 'City', 'State', 'Zip Code', 'Phone']
                if len(headers) == 8 and headers==de_header:
                    for fields in datas:
                        if fields:
                            if fields[0]!='ID':
                                hy_Id = rem_mul(fields[0])
                                first_name = rem_mul(fields[1])
                                last_name = rem_mul(fields[2])
                                address = rem_mul(fields[3])
                                city = rem_mul(fields[4])
                                state = rem_mul(fields[5])
                                zip = rem_mul(fields[6])
                                phone = rem_mul(fields[7])
                                c_all+=1
                                if hy_Id.isnumeric():
                                    if Hygienist.objects.filter(hygienist_id = hy_Id).exists():
                                        form=Hygienist.objects.get(hygienist_id = hy_Id)
                                        form.hygienist_id = hy_Id
                                        form.first_name = first_name
                                        form.last_name = last_name
                                        form.address = address
                                        form.city = city
                                        form.state = state
                                        form.zip = zip
                                        form.phone = phone
                                        form.save()
                                        al_e_a.append(hy_Id)
                                        al_e+=1
                                    else:
                                        form=Hygienist()
                                        form.hygienist_id = hy_Id
                                        form.first_name = first_name
                                        form.last_name = last_name
                                        form.address = address
                                        form.city = city
                                        form.state = state
                                        form.zip = zip
                                        form.phone = phone
                                        form.save()
                                        ids.append(form.id)
                                        add_count+=1
                                else:
                                    invalid_ada.append(hy_Id)
                else:
                    err="Please Upload a Correct row and columns"
        else:
            err="File Not Found"

        return {"exists_id":al_e_a,"Added_id":add_count,"err":err,'total_given':c_all,'invalid_ada':invalid_ada}

    def list_hygienist():
        data=Hygienist.objects.all()
        return data
    
