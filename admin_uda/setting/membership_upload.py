from admin_uda.models import Ada_membership
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import datetime as dt
import random
import csv

class membership:
    def add_membership(self,request):
        file=request
        logo_root = os.path.join(settings.MEDIA_ROOT, 'membership_upload/')
        logo_root=logo_root.replace("\\","/")
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
        new_file_name='membership_upload_'+d+t+ext
        fs=FileSystemStorage(location=logo_root)
        filename=fs.save(new_file_name,file)
        rem_mul=lambda a:a.replace("\t"," ")
        if os.path.exists('uploads/membership_upload/'+new_file_name):
            with open('uploads/membership_upload/'+new_file_name, newline='') as csvfile:
                datas = csv.reader(csvfile)
                headers = next(datas)
                de_header=['ID', 'Prefix', 'ADA Number', 'Last Name', 'First Name', 'Middle Name', 'Suffix', 'Constituent Current Level', 'Retirement Date', 'Primary Function', 'Phone', 'Member Type', 'Address Line 1', 'Address Line 2', 'Address Line 3', 'City', 'State', 'Zip Code', 'MembershipYear', 'PracticeName', 'Component Jurisdiction']
                if len(headers) == 21 and headers==de_header:
                    for fields in datas:
                            if fields:
                                if fields[0]!='ID':
                                    me_Id = rem_mul(fields[0])
                                    prefix = rem_mul(fields[1])
                                    ada_number = rem_mul(fields[2])
                                    last_name = rem_mul(fields[3])
                                    first_name = rem_mul(fields[4])
                                    middle_name = rem_mul(fields[5])
                                    suffix = rem_mul(fields[6])
                                    Constituent_Current_Level = rem_mul(fields[7])
                                    Retirement_Date = rem_mul(fields[8])
                                    Primary_Function = rem_mul(fields[9])
                                    Phone = rem_mul(fields[10])
                                    Member_Type = rem_mul(fields[11])
                                    Address_Line_1 = rem_mul(fields[12])
                                    Address_Line_2 = rem_mul(fields[13])
                                    Address_Line_3 = rem_mul(fields[14])
                                    City = rem_mul(fields[15])
                                    State = rem_mul(fields[16])
                                    Zip_Code = rem_mul(fields[17])
                                    MembershipYear = rem_mul(fields[18])
                                    PracticeName = rem_mul(fields[19])
                                    Component_Jurisdiction = rem_mul(fields[20])
                                    c_all+=1
                                    if ada_number.isnumeric():
                                        if Ada_membership.objects.filter(ADA_Number = ada_number).exists():
                                            form=Ada_membership.objects.get(ADA_Number = ada_number)
                                            form.Membership_id = me_Id
                                            form.Prefix = prefix
                                            form.ADA_Number = ada_number
                                            form.Last_Name = last_name
                                            form.First_Name = first_name
                                            form.Middle_Name = middle_name
                                            form.Suffix = suffix
                                            form.Constituent_Current_Level = Constituent_Current_Level
                                            form.Retirement_Date = Retirement_Date
                                            form.Primary_Function = Primary_Function
                                            form.Phone = Phone
                                            form.Member_Type = Member_Type
                                            form.Address_Line_1 = Address_Line_1
                                            form.Address_Line_2 = Address_Line_2
                                            form.Address_Line_3 = Address_Line_3
                                            form.City = City
                                            form.State = State
                                            form.Zip_Code = Zip_Code
                                            form.MembershipYear = MembershipYear
                                            form.PracticeName = PracticeName
                                            form.Component_Jurisdiction = Component_Jurisdiction
                                            form.save()
                                            al_e_a.append(ada_number)
                                            al_e+=1
                                        else:
                                            form=Ada_membership()
                                            form.Membership_id = me_Id
                                            form.Prefix = prefix
                                            form.ADA_Number = ada_number
                                            form.Last_Name = last_name
                                            form.First_Name = first_name
                                            form.Middle_Name = middle_name
                                            form.Suffix = suffix
                                            form.Constituent_Current_Level = Constituent_Current_Level
                                            form.Retirement_Date = Retirement_Date
                                            form.Primary_Function = Primary_Function
                                            form.Phone = Phone
                                            form.Member_Type = Member_Type
                                            form.Address_Line_1 = Address_Line_1
                                            form.Address_Line_2 = Address_Line_2
                                            form.Address_Line_3 = Address_Line_3
                                            form.City = City
                                            form.State = State
                                            form.Zip_Code = Zip_Code
                                            form.MembershipYear = MembershipYear
                                            form.PracticeName = PracticeName
                                            form.Component_Jurisdiction = Component_Jurisdiction
                                            form.save()
                                            ids.append(form.id)
                                            add_count+=1
                                    else:
                                        invalid_ada.append(ada_number)
                else:
                    err="Please Upload a Correct row and columns"
        else:
            err='File Not Found'

        return {"exists_id":al_e_a,"Added_id":add_count,"err":err,'total_given':c_all}

    def list_membership(self):
        data=Ada_membership.objects.all()
        return data
    
