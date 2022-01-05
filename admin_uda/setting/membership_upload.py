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
        invalid_ada=[]
        add_count=0
        c_all=0
        err=''
        today=dt.datetime.now()
        d=str(today.date())
        t=str(random.randint(111111111, 9999999999))
        ext='.csv'
        new_file_name='membership_upload_'+d+t+ext
        fs=FileSystemStorage(location=logo_root)
        fs.save(new_file_name,file)
        err='File Not Found'
        if os.path.exists('uploads/membership_upload/'+new_file_name):
            with open('uploads/membership_upload/'+new_file_name, newline='') as csvfile:
                datas = csv.reader(csvfile)
                headers = next(datas)
                de_header=['ID', 'Prefix', 'ADA Number', 'Last Name', 'First Name', 'Middle Name', 'Suffix', 'Constituent Current Level', 'Retirement Date', 'Primary Function', 'Phone', 'Member Type', 'Address Line 1', 'Address Line 2', 'Address Line 3', 'City', 'State', 'Zip Code', 'MembershipYear', 'PracticeName', 'Component Jurisdiction']
                if len(headers) == 21 and headers==de_header:
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
                mem_id = rem_mul(fields[0])
                prefix = rem_mul(fields[1])
                ada_number = rem_mul(fields[2])
                last_name = rem_mul(fields[3])
                first_name = rem_mul(fields[4])
                middle_name = rem_mul(fields[5])
                suffix = rem_mul(fields[6])
                constituent_current_level = rem_mul(fields[7])
                retirement_date = rem_mul(fields[8])
                primary_function = rem_mul(fields[9])
                mem_phone = rem_mul(fields[10])
                member_type = rem_mul(fields[11])
                address_line_one = rem_mul(fields[12])
                address_line_two = rem_mul(fields[13])
                address_line_three = rem_mul(fields[14])
                city = rem_mul(fields[15])
                state = rem_mul(fields[16])
                zip_code = rem_mul(fields[17])
                membership_year = rem_mul(fields[18])
                practice_name = rem_mul(fields[19])
                component_jurisdiction = rem_mul(fields[20])
                c_all+=1
                if ada_number.isnumeric():
                    if Ada_membership.objects.filter(ADA_Number = ada_number).exists():
                        form=Ada_membership.objects.get(ADA_Number = ada_number)
                        form.Membership_id = mem_id
                        form.Prefix = prefix
                        form.ADA_Number = ada_number
                        form.Last_Name = last_name
                        form.First_Name = first_name
                        form.Middle_Name = middle_name
                        form.Suffix = suffix
                        form.Constituent_Current_Level = constituent_current_level
                        form.Retirement_Date = retirement_date
                        form.Primary_Function = primary_function
                        form.Phone = mem_phone
                        form.Member_Type = member_type
                        form.Address_Line_1 = address_line_one
                        form.Address_Line_2 = address_line_two
                        form.Address_Line_3 = address_line_three
                        form.City = city
                        form.State = state
                        form.Zip_Code = zip_code
                        form.MembershipYear = membership_year
                        form.PracticeName = practice_name
                        form.Component_Jurisdiction = component_jurisdiction
                        form.save()
                        al_e_a.append(ada_number)
                    else:
                        form=Ada_membership()
                        form.Membership_id = mem_id
                        form.Prefix = prefix
                        form.ADA_Number = ada_number
                        form.Last_Name = last_name
                        form.First_Name = first_name
                        form.Middle_Name = middle_name
                        form.Suffix = suffix
                        form.Constituent_Current_Level = constituent_current_level
                        form.Retirement_Date = retirement_date
                        form.Primary_Function = primary_function
                        form.Phone = mem_phone
                        form.Member_Type = member_type
                        form.Address_Line_1 = address_line_one
                        form.Address_Line_2 = address_line_two
                        form.Address_Line_3 = address_line_three
                        form.City = city
                        form.State = state
                        form.Zip_Code = zip_code
                        form.MembershipYear = membership_year
                        form.PracticeName = practice_name
                        form.Component_Jurisdiction = component_jurisdiction
                        form.save()
                        add_count+=1
                else:
                    invalid_ada.append(ada_number)
        return {"al_e_a":al_e_a,"add_count":add_count,"c_all":c_all,"invalid_ada":invalid_ada}

    def list_membership(self):
        data=Ada_membership.objects.all()
        return data
    
