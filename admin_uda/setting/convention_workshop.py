from django.db.models.aggregates import Count
from django.db.models import Q 
from admin_uda.models import Handon_workshop,Handon_form_workshop
import datetime as dt

class convention_workshops():
    date_format_db = '%Y-%m-%d'
    date_format_input = '%m/%d/%Y'
    def save_convention_workshop(self,request):
        last_id=''
        msg=''
        event_date_get=request.POST.get('event_date')
        event_date=dt.datetime.strptime(event_date_get, self.date_format_input).strftime(self.date_format_db)
        timeslot=request.POST.get('timeSlot')
        speaker_name=request.POST.get('speaker_name')
        name=request.POST.get('name')
        qty=request.POST.get('qty')
        total_hours=request.POST.get('total_hours')
        amount=request.POST.get('amount')
        edit_rec_id=request.POST.get('edit_rec_id')
        dup=Handon_workshop.objects.filter(event_date=event_date,timeslot=timeslot,name=name.lower()).filter(~Q(id=edit_rec_id)).exclude(status=2).count()
        error=''
        if dup == 0:
            if int(edit_rec_id)==0 or edit_rec_id=='':
                form=Handon_workshop()
                form.event_date=event_date
                form.timeslot=timeslot
                form.speaker_name=speaker_name
                form.name=name
                form.qty=qty
                form.total_hours=total_hours
                form.amount=amount
                form.status=1
                form.save()
                last_id=form.id
                msg="Workshop Added Successfully"
            else:
                form=Handon_workshop.objects.get(id=edit_rec_id)
                form.event_date=event_date
                form.timeslot=timeslot
                form.speaker_name=speaker_name
                form.name=name
                form.qty=qty
                form.total_hours=total_hours
                form.amount=amount
                form.status=1
                form.save()
                last_id=form.id
                msg="Workshop Updated Successfully"
        else:
            error="Workshop Name Already Exists"
            
        return {"error":error,"ids":last_id,"msg":msg}

    def list_convention_workshop(self,request):
        flt_date=request.POST.get('flt_date')
        flt_event_date=''
        if flt_date:
            flt_event_date=dt.datetime.strptime(flt_date, self.date_format_input).strftime(self.date_format_db)

        flt_timeslot=request.POST.get('flt_timeslot')
        tot_count=Handon_workshop.objects.exclude(status=2)
        qry=Handon_workshop.objects.exclude(status=2)
        if flt_event_date:
            tot_count=tot_count.filter(event_date=flt_event_date)
            qry=qry.filter(event_date=flt_event_date)

        if flt_timeslot:
            tot_count=tot_count.filter(timeslot=flt_timeslot)
            qry=qry.filter(timeslot=flt_timeslot)

        tot_count=tot_count.count()
        nd=[]
        res={}
        j=0
        for datas in qry:
            nested_data=[]
            slot=''
            if datas.timeslot==1:
                slot=" AM"
            else:
                slot=" PM"

            if datas.status==1:
                lock="lock-open"
                mod="deactive"
            else:
                lock="lock"
                mod="active"
            res_count=Handon_form_workshop.objects.filter(work_id=datas.id,hand_id__archive_id=0,hand_id__status=1).values('hand_id').annotate(tot=Count('hand_id')).values('tot')
            reg=0
            if res_count:
                reg=res_count[0]['tot']

            avail=datas.qty-reg

            spe_name="""<div class="d-flex align-items-center">
                           <div class="activity-icon avatar-xs me-2">
                                <span class="avatar-title bg-soft-danger text-danger br-5">"""+datas.speaker_name[0].capitalize()+"""</span>
                            </div>
                            <div class="d-block mt-1">
                                 <p class="mb-0 fs-14">"""+datas.speaker_name.capitalize()+"""</p>
                            </div>
                    </div>"""
            nested_data.append(spe_name)
            nested_data.append(datas.name)
            event_date_get=datas.event_date
            event_date=dt.datetime.strptime(str(event_date_get), self.date_format_db).strftime("%m, %A, %Y")
            event_date_f=event_date+slot
            nested_data.append(event_date_f)
            dqty=str(reg) +" / "+ str(datas.qty) +"<br>Bal: "+ str(avail) +" Available" 
            nested_data.append(datas.amount)
            nested_data.append(dqty)
            actions="""<div class='d-flex align-items-center'>
                            <a href="javascript:void(0);" data-id='"""+str(datas.id)+"""' data-attr='"""+mod+"""' class="me-3 text-warning tblBLock"
                                data-bs-container="#tooltip-container"""+str(j)+""""" data-bs-toggle="tooltip"
                                data-bs-placement="top" title="Block Temporarily"><i
                                    class="mdi mdi-"""+lock+""" font-size-18"></i></a>
                            <a href="javascript:void(0);" data-id='"""+str(datas.id)+"""' class="me-3 text-primary tabEdit"
                                data-bs-container="#tooltip-container"""+str(j)+""""" data-bs-toggle="tooltip"
                                data-bs-placement="top" title="Edit"><i
                                    class="mdi mdi-pencil font-size-18"></i></a>
                            <a href="javascript:void(0);" data-id='"""+str(datas.id)+"""' class="text-danger tabDelete"
                                data-bs-container="#tooltip-container"""+str(j)+""""" data-bs-toggle="tooltip"
                                data-bs-placement="top" title="Delete"><i
                                    class="mdi mdi-trash-can font-size-18"></i></a>
                        </div>"""
            nested_data.append(actions)
            nd.append(nested_data)
            j+=1
        res['draw']=request.POST.get('draw')
        res['recordsTotal']=tot_count
        res['recordsFiltered']=tot_count
        res['data']=nd
        return res

    def delete_convention_workshop(self,request):
        ids=request.POST.get('id')
        form=Handon_workshop.objects.get(id=ids)
        form.status=2
        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}

    def block_convention_workshop(self,request):
        ids=request.POST.get('id')
        mod=request.POST.get('mod')
        form=Handon_workshop.objects.get(id=ids)
        if mod=='deactive':
            form.status=0
        else:
            form.status=1

        form.save()
        if form.id:
            res=1
        else:
            res=0

        return {"res":res}

    def get_convention_workshop(self,request):
        ids=request.POST.get('id')
        datas=Handon_workshop.objects.filter(id=ids)
        return datas
