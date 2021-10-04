from django.shortcuts import render,redirect , get_object_or_404
from django.contrib.auth.models import auth ,Group
from django.http import Http404, HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from . decorators import unauthenticated_user,allowed_users, admin_only
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.mail import BadHeaderError, send_mail
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from  .forms import UserAdminCreationForm,UserProfileCreationForm,UserVerificationForm,UserRejectionForm
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.http import HttpResponseRedirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser,Category,Comment,StartUp,RealEstate,Taxation,Legal,Tradmark,Service,Other
import random
import string
import copy
import datetime
from django.utils.timezone import utc
from django.db import IntegrityError
from django.conf import settings
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML,CSS

import tempfile
import ssl
import logging
logger = logging.getLogger('weasyprint')
logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))
ssl._create_default_https_context = ssl._create_unverified_context
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
import pandas as pd
from django.views.generic.base import TemplateView






@unauthenticated_user
def login(request):
    if request.method == "POST":
        phone = request.POST['phone']
        password = request.POST['password']   
        user = auth.authenticate(phone=phone,password=password)
        if user is not None:
            auth.login(request,user)
             
            if request.user.is_suspended:
               return render(request,'user_html/suspendeduser.htm',{'user':request.user})
            else:
                if request.user.password_update:
                    if request.user.role == 'BO':
                        request.user.is_verified = True
                        request.user.profile_update = True
                        return render(request,'user_html/bodashboard_v2.html',{'user':request.user})
                    if request.user.role == 'ACCOUNT':
                        request.user.is_verified = True
                        request.user.profile_update = True
                        return render(request,'service_html/service_verify_v2.html')

                    if request.user.profile_update:
                        return redirect('dashboard')
                    else:
                        return redirect('profile')
                else:
                    return redirect('password_change')
        else:
            messages.error(request, 'Error! please enter the correct  Username and Password.')
            return render(request,'user_html/login_v2.html')
    else:
        return render(request,"user_html/login_v2.html")



@login_required(login_url='login')
def mic_dashboard(request):
    x = request.user.role
    managers_dsa_af = ['AF','DSA']
    managers_afm_rm = ['AFM','RM']
    ruser = request.user
    services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager=ruser) | Q(created_by__manager__referred_by=ruser.referral_code),verification_approved=True,other_details_updated=True)
    context = {
        'services':services,
        'count':services.count
        
        }
    return render (request,'service_html/mic_dashboard_v2.html',context)

  
@login_required(login_url='login')
def yourservice(request):
    ruser = request.user
    print(request)
    services = Service.objects.filter(Q(created_by=ruser)|Q(created_by__manager=ruser) |Q(created_by__manager__referred_by=ruser.referral_code),service_update=True).order_by('-id')
    
    count = services.count
    
    page = request.GET.get('page', 1)
    paginator = Paginator(services, 10)
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)

    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')

    # if ruser.role in ['CONNECTOR','AF']:
    #     return render(request,'service_html/your_services_v2.html')

    
    if request.POST.get('proceed'):
        service = Service.objects.get(id=request.POST.get('proceed'))
        return render(request,'service_html/service_process_v2.html',{'service':service})


    if request.POST.get('customer_contact_update'):
        service = Service.objects.get(id=request.POST.get('customer_contact_update'))
        service.customer_contact_updated = True
        service.customer_contacted = request.POST.get('customer_contacted')
        print('ABCD',service.customer_contacted)
        if service.customer_contacted == "on":
            service.customer_contacted = True
            service.customer_contacted_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            service.customer_contacted = False
            service.customer_contacted_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('customer_contact_updated_success'):
        service = Service.objects.get(id=request.POST.get('customer_contact_updated_success'))
        service.customer_contact_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('file_picked_updated'):
        service = Service.objects.get(id=request.POST.get('file_picked_updated'))
        service.file_picked_updated = True 
        service.file_picked = request.POST.get('file_picked')
        print('ABCD',service.file_picked)
        if service.file_picked == "on":
            service.file_picked = True
            service.file_picked_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            service.file_picked = False
            service.file_picked_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('file_picked_updated_success'):
        service = Service.objects.get(id=request.POST.get('file_picked_updated_success'))
        service.file_picked_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('remark_message_updated'):
        service = Service.objects.get(id=request.POST.get('remark_message_updated'))
        service.remark_message_updated = True
        service.remark_message = request.POST.get('remark_message')
        service.remark_message_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('remark_message_updated_success'):
        service = Service.objects.get(id=request.POST.get('remark_message_updated_success'))
        service.remark_message_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('file_pickup_process_completed'):
        service = Service.objects.get(id=request.POST.get('file_pickup_process_completed'))
        service.file_pickup_process_completed = True
        service.file_pickup_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service,'banks':banks})
    
    if request.POST.get('login_bank_updated'):
        service = Service.objects.get(id=request.POST.get('login_bank_updated'))
        service.login_bank_updated = True
        service.login_bank_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        
        if request.POST.get('bank'):
            print(request.POST.get('bank'))
            service.login_bank = LoginBank.objects.get(name=request.POST.get('bank'))
            service.login_bank.save()
            service.save()
            return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('login_bank_updated_success'):
        service = Service.objects.get(id=request.POST.get('login_bank_updated_success'))
        service.login_bank_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service,'banks':banks})

    if request.POST.get('login_bank_process_completed'):
        service = Service.objects.get(id=request.POST.get('login_bank_process_completed'))
        service.login_bank_process_completed = True
        service.login_bank_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('senction_letter_updated'):
        
        service = Service.objects.get(id=request.POST.get('senction_letter_updated'))
        if request.FILES.get('senction_letter',''):
            service.senction_letter = request.FILES.get('senction_letter','')
        else:
            service.senction_letter = ''
        service.senction_letter_updated = True
        service.senction_letter_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('senction_letter_updated_success'):
        service = Service.objects.get(id=request.POST.get('senction_letter_updated_success'))
        service.senction_letter_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('senction_amount_updated'):
        service = Service.objects.get(id=request.POST.get('senction_amount_updated'))
        service.senction_amount = request.POST.get('senction_amount')
        service.senction_amount_updated = True
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    

    if request.POST.get('senction_amount_updated_success'):
        service = Service.objects.get(id=request.POST.get('senction_amount_updated_success'))
        service.senction_amount_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('dsa_code_updated'):
        service = Service.objects.get(id=request.POST.get('dsa_code_updated'))
        service.dsa_code = request.POST.get('dsa_code')
        service.dsa_code_updated = True
        service.dsa_code_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('dsa_code_updated_success'):
        service = Service.objects.get(id=request.POST.get('dsa_code_updated_success'))
        service.dsa_code_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('senction_date_updated'):
        service = Service.objects.get(id=request.POST.get('senction_date_updated'))
        print(request.POST.get('senction_date'))
        service.senction_date = datetime.datetime.strptime(request.POST.get('senction_date'),'%Y-%m-%d')
        service.senction_date_updated = True
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service}) 

    if request.POST.get('senction_date_updated_success'):
        service = Service.objects.get(id=request.POST.get('senction_date_updated_success'))
        service.senction_date_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('senction_process_completed'):
        service = Service.objects.get(id=request.POST.get('senction_process_completed'))
        service.senction_process_completed = True
        service.senction_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        
        service.save()
        return redirect('yourservice')
    
    if request.POST.get('disbursement_updated'):
        service = Service.objects.get(id=request.POST.get('disbursement_updated'))
        service.disbursement_updated = True
        service.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)  
        service.disbursement = request.POST.get('disbursement')
        print('ABCD',service.disbursement)
        if service.disbursement == "on":
            service.disbursement = True
            service.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            service.disbursement = False
            service.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_success'):
        service= Service.objects.get(id=request.POST.get('disbursement_success'))
        service.disbursement_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_proof_updated'):
        service = Service.objects.get(id=request.POST.get('disbursement_proof_updated'))
        service.disbursement_proof = request.FILES.get('disbursement_proof')
        service.disbursement_proof_updated = True
        service.disbursement_proof_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_proof_updated_success'):
        service =Service.objects.get(id=request.POST.get('disbursement_proof_updated_success'))
        service.disbursement_proof_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_amount_updated'):
        service = Service.objects.get(id=request.POST.get('disbursement_amount_updated'))
        service.disbursement_amount = request.POST.get('disbursement_amount')
        service.disbursement_amount_updated = True
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_amount_updated_success'):
        service = Service.objects.get(id=request.POST.get('disbursement_amount_updated_success'))
        service.disbursement_amount_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('disbursement_date_updated'):
        service = Service.objects.get(id=request.POST.get('disbursement_date_updated'))
        print(request.POST.get('disbursement_date'))
       
        service.disbursement_date = datetime.datetime.strptime(request.POST.get('disbursement_date'),'%Y-%m-%d')
        service.disbursement_date_updated = True
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service}) 

    if request.POST.get('disbursement_date_updated_success'):
        service = Service.objects.get(id=request.POST.get('disbursement_date_updated_success'))
        service.disbursement_date_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('payout_updated'):
        service = Service.objects.get(id=request.POST.get('payout_updated'))  
        service.payout = request.POST.get('payout')  
        service.payout_updated = True
        service.payout_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})

    if request.POST.get('payout_updated_success'):
        service = Service.objects.get(id=request.POST.get('payout_updated_success'))
        service.payout_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})


    if request.POST.get('disbursement_rejection_reason_updated'):
        service = Service.objects.get(id=request.POST.get('disbursement_rejection_reason_updated'))
        service.disbursement_rejection_reason = request.POST.get('disbursement_rejection_reason')
        service.disbursement_rejection_reason_updated = True
        service.disbursement_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    if request.POST.get('disbursement_rejection_reason_updated_success'):
        service = Service.objects.get(id=request.POST.get('disbursement_rejection_reason_updated_success'))
        service.disbursement_rejection_reason_updated = False
        service.save()
        return render(request,'service_html/service_process_v2.html',{'service':service})
    
    
    if request.POST.get('disbursement_process_completed'):
        service = Service.objects.get(id=request.POST.get('disbursement_process_completed'))
        service.disbursement_process_completed_approved = True
        service.verification_pending = True
        service.verification_rejected = False
        service.verification_approved = False
        service.disbursement_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return redirect('yourservice')
    
    if request.POST.get('disbursement_process_rejected'):
        service = Service.objects.get(id=request.POST.get('disbursement_process_rejected'))
        service.disbursement_process_completed_rejected = True
        service.disbursement_process_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        service.save()
        return redirect('yourservice')
        
    if request.POST.get('details'):
        service =Service.objects.get(id=request.POST.get('details'))
        context = {'ruser':ruser,'service':service}
        html_string = render_to_string('service_html/pdf.html',context)
        html = HTML(string=html_string,base_url=request.build_absolute_uri())
        pdf = html.write_pdf(presentational_hints=True)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="service.pdf"'
        return response

    if request.POST.get('chat'):
        service =Service.objects.get(id=request.POST.get('chat'))
        comments = Comment.objects.filter(service=service.id).order_by('-id')
        return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
    
    if request.POST.get('service_chat_updated'):
        service = Service.objects.get(id=request.POST.get('service_chat_updated'))
        comments = Comment.objects.filter(service=service.id).order_by('-id')
        print('ABCD')
        if not request.FILES.get('service_attachments') and not request.POST.get('service_chat'):

            messages.error(request,'Message or Attachement is missing')
            return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
        else:
            comment = Comment.objects.create(service= service,message=request.POST.get('service_chat'),user=request.user,attachments=request.FILES.get('service_attachments'))
            comment.save()
            return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
            
    if count==0:
        messages.error(request,'No service is Found')
        return render(request, 'service_html/your_services_v2.html',{'ruser':ruser,'services':services,'count':count})
    else:
        return render(request, 'service_html/your_services_v2.html',{'ruser':ruser,'services':services,'count':count})
    
        services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code)).order_by('-id')
        print(services)

 
@login_required(login_url='login')
def services(request):
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT' :
        return render(request,'user_html/404_page.htm')
        
    # balance_transfer_banks = BalanceTransferBank.objects.all()
    # transfer_banks = TransferBank.objects.all()
    # business_proofs = BusinessProof.objects.all()
    # relationship_applicats = RelationshipApplicant.objects.all()
    # topup_reasons =  TopupReason.objects.all()
    # address_proofs = AddressProof.objects.all()
    # co_applicant_address_proofs = CoApllicantAddressProof.objects.all()
    # company_types = CompanyType.objects.all()
    # businesses = Business.objects.all()
    # khatas = Khata.objects.all()    
    real_states =  RealEstate.objects.all()
    startups =  StartUp.objects.all()
    taxations =  Taxation.objects.all()
    legals = Legal.objects.all()
    tradmarks = Tradmark.objects.all()
    others = Other.objects.all()



    

    print("fadadasdads")
    if request.method == "POST":
        
        ####################################  Select Service Type ##############################################
       
        service_type = request.POST.get('service_type')
            
        if service_type == 'real_estate':
            service_type = 'Real Estate'
            service_sub_type = request.POST.get('real_estate_type')
            if service_sub_type == 'rera':
                service_sub_type = 'RERA'
            if service_sub_type == 'layout_approval':
                service_sub_type = 'Layout Approval'
            if service_sub_type == 'architect':
                service_sub_type = 'Architect & Interiors'
            if service_sub_type == 'documentations':
                service_sub_type = 'Documentations'
            if service_sub_type == 'loans':
                service_sub_type = 'Loans'
            service_amount = request.POST.get('required_service_amount_real_estate')
        
        if service_type == 'startup':
            service_type = 'Start Up'
            service_sub_type = request.POST.get('startup_type')
            if service_sub_type == 'pvt':
                service_sub_type = 'PVT LTD.'
            if service_sub_type == 'llp':
                service_sub_type = 'LLP Co.'
            if service_sub_type == 'one_person_co':
                service_sub_type = 'One Person Co.'
            if service_sub_type == 'partnership_firm':
                service_sub_type = 'Partnership Firm'
            if service_sub_type == 'properietship':
                service_sub_type = 'Properietship'
            service_amount = request.POST.get('required_service_amount_startup')
        
        if service_type == 'taxation':
            service_type = 'Taxation'
            service_sub_type = request.POST.get('taxation_type')
            if service_sub_type == 'income_tax':
                service_sub_type = 'Income Tax'
            if service_sub_type == 'gst':
                service_sub_type = 'GST'
            service_amount = request.POST.get('required_service_amount_taxation')
        
        if service_type == 'legal':
            service_type = 'Legal'
            service_sub_type = request.POST.get('legal_type')
            if service_sub_type == 'land_revenue':
                service_sub_type = 'Land & Revenue'
            
            if service_sub_type == 'criminal_matter':
                service_sub_type = 'Criminal Matter'
            
            if service_sub_type == 'civil_matter':
                service_sub_type = 'Civil Matter'
            
            if service_sub_type == 'divorce':
                service_sub_type = 'Divorce'
            
            if service_sub_type == 'consumer_protaction':
                service_sub_type = 'Consumer Protaction '
            if service_sub_type == 'nia':
                service_sub_type = 'NIA'
            service_amount = request.POST.get('required_service_amount_legal')
        
        if service_type == 'tradmark':
            service_type = 'Tradmark'
            service_sub_type = request.POST.get('tradmark_type')
            if service_sub_type == 'trademark':
                service_sub_type = 'Trademark'
            if service_sub_type == 'patent':
                service_sub_type = 'Patent'
            if service_sub_type == 'copyright':
                service_sub_type = 'Copy Right'
            service_amount = request.POST.get('required_service_amount_tradmark')
        
        if service_type == 'others':
            service_type = 'Others'
            service_sub_type = request.POST.get('others_type')
            if service_sub_type == 'rto':
                service_sub_type = 'RTO'
            if service_sub_type == 'certificate':
                service_sub_type = 'Certificate'
            if service_sub_type == 'deed':
                service_sub_type = 'Deed'
            if service_sub_type == 'registration':
                service_sub_type = 'Registration'
            if service_sub_type == 'passport':
                service_sub_type = 'Passport Services'
            if service_sub_type == 'rti':
                service_sub_type = 'Right To Information'
            service_amount = request.POST.get('required_service_amount_others')

        
        
        service = Service.objects.create(
            service_type = service_type,
            service_amount = service_amount,
            service_sub_type = service_sub_type,
            created_by = request.user,
            service_update = True,
            verification_pending = True,

        )   
        service.save()

        
        print(service)
    
        
        
       
        return redirect('yourservice')

    return render (request,'service_html/services.html')
        
@login_required(login_url='login')
def pipeline(request):
    ruser = request.user
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')

    today = datetime.date.today()
    current_date = datetime.date.today() 
    first = today.replace(day=1)  # first date of current month
    previous_month_date = first - datetime.timedelta(days=1)
    services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code)).filter(login_bank_updated_at__lt=first).exclude(Q(disbursement_process_completed_approved=True)| Q(disbursement_process_completed_rejected=True)).order_by('-id')
    count = services.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(services, 2)
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)
    print(services)
    
    print('ABCDFR',count)

    if request.POST.get('chat'):
        service =Service.objects.get(id=request.POST.get('chat'))
        comments = Comment.objects.filter(service=service.id).order_by('-id')
        return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
        
    if request.POST.get('service_chat_updated'):
        service = Service.objects.get(id=request.POST.get('service_chat_updated'))
        comments = Comment.objects.filter(service=service.id).order_by('-id')
        if not request.FILES.get('service_attachments') and not request.POST.get('service_chat'):
            messages.error(request,'Message or Attachement is missing')
            return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
        else:
            comment = Comment.objects.create(service= service,message=request.POST.get('service_chat'),user=request.user,attachments=request.FILES.get('service_attachments'))
            comment.save()
            return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
    
    print(services)
    if ruser.role not in ['CONNECTOR','AF']:
        if count==0:
            messages.error(request,'No service is Found Greater Than 30 Days')
            print('ABCD') 
            return render(request, 'service_html/pipeline_cases_v2.html',{'ruser':ruser,'services':services,'count':count})
        else:
            return render(request, 'service_html/pipeline_cases_v2.html',{'ruser':ruser,'services':services,'count':count})
    else:
        if count==0:
            messages.error(request,'No service is Found Greater Than 30 Days')
            return render(request, 'service_html/pipeline_cases_v2.html',{'ruser':ruser,'services':services,'count':count})
        else:
            return render(request, 'service_html/pipeline_cases_v2.html',{'ruser':ruser,'services':services,'count':count})


@login_required(login_url='login')
def change_password(request):
    if request.user.is_suspended == True:
        return render(request,'user_html/404_page.htm')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.password_update = True
            user.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            if request.user.profile_update:
                return redirect('dashboard')
            else:
                return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user_html/password_change.htm', {
        'form': form
    })

@login_required(login_url='login')
def usermanagement(request):
    users = User.objects.filter(referred_by=request.user.referral_code).exclude(role='ADMIN')
    count = users.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')
    # print(request.user.referral_code)
    # print(request.user.id)
    # print(users)
    if (request.user.role!='CONNECTOR' and request.user.role!='BO'):
        if request.POST.get('details'):
            referred_user =User.objects.get(id=request.POST.get('details'))
            users = User.objects.filter(referred_by=referred_user.referral_code)
        if request.POST.get('suspend'):
            
            suspend_user = User.objects.get(id=request.POST.get('suspend'))
            print(suspend_user.first_name)
            suspend_user.is_suspended = True
            suspend_user.save()
            current_site = get_current_site(request)
            mail_subject_employee = 'Your Profile is Suspended'
            mail_subject_manager = 'Your Referred User Account has been Suspended'
            print(mail_subject_employee)
            print(mail_subject_manager)
            message_to_employee = render_to_string('email_template/suspension_message.htm', {
                'suspend_user': suspend_user,
                'suspend_user_role': suspend_user.role,
                'suspend_user_manager':suspend_user.manager,
                'suspend_user_manager_phone':suspend_user.manager.phone,
                'admin_user': request.user,
                'domain': current_site.domain,
                })
            print(message_to_employee)
            to_email = suspend_user.email
            email = EmailMessage(
                        mail_subject_employee, message_to_employee, to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            message_to_manager = render_to_string('email_template/suspension_message_to_manager.htm',{
                'suspend_user': suspend_user,
                'suspend_user_role': suspend_user.role,
                'suspend_user_manager':suspend_user.manager,
                'admin_user': request.user,
                'domain': current_site.domain,
                })
            print(message_to_manager)
            to_email = suspend_user.manager.email
            email = EmailMessage(
                        mail_subject_manager, message_to_manager, to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            return render(request,"user_html/usermanagement_v2.html",{'users':users})
        if request.POST.get('active'):
            active_user = User.objects.get(id=request.POST.get('active'))
            active_user.is_suspended = False
            active_user.save()
            current_site = get_current_site(request)
            mail_subject_employee = 'Reactivated Account '
            mail_subject_manager = 'Your Referred User Account has been Reactivated'
            print(mail_subject_employee)
            print(mail_subject_manager)
            message_to_employee = render_to_string('email_template/activate_message.htm', {
                'activate_user': active_user,
                'activate_user_role': active_user.role,
                'activate_user_manager':active_user.manager,
                'admin_user': request.user,
                'domain': current_site.domain,
                })
            print(message_to_employee)
            to_email = active_user.email
            email = EmailMessage(
                        mail_subject_employee, message_to_employee, to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            message_to_manager = render_to_string('email_template/activate_message_to_manager.htm',{
                'activate_user': active_user,
                'activate_user_role': active_user.role,
                'activate_user_manager':active_user.manager,
                'admin_user': request.user,
                'domain': current_site.domain,
                })
            print(message_to_manager)
            to_email = active_user.manager.email
            email = EmailMessage(
                        mail_subject_manager, message_to_manager, to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            return render(request,"user_html/usermanagement_v2.html",{'users':users})
        if request.POST.get('resend'):
            print('hello')
            resend_user = User.objects.get(id=request.POST.get('resend'))
            letters = string.ascii_uppercase
            password_genrate=(''.join(random.choice(letters) for i in range(6)) )
            resend_user.set_password(password_genrate)
            resend_user.save()
            current_site = get_current_site(request)
            mail_subject_employee = 'Activate your .'
            print(mail_subject_employee)
            message = render_to_string('email_template/register_confirm.htm', {
                'user': resend_user,
                'domain': current_site.domain,
                'uid':force_text(urlsafe_base64_encode(force_bytes(resend_user.pk))),
                'token':account_activation_token.make_token(resend_user),
                'password':password_genrate,
            })
            print(message)
            to_email = resend_user.email
            email = EmailMessage(
                        mail_subject_employee, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)
            messages.success(request, 'Activation Email has been Resent for your refferral account')
            resend_user.save()
            return render(request,"user_html/usermanagement_v2.html",{'users':users})
            
        if count==0:
            messages.error(request,'No User is Reffered')
            return render(request,"user_html/usermanagement_v2.html",{'users':users,'count':count})
        else:
            return render(request,"user_html/usermanagement_v2.html",{'users':users,'count':count})           
    else:
        return render(request,'user_html/404_page.htm')


@login_required(login_url='login')
def reports(request):
    if request.user.role == 'ADMIN': 
        print(request.POST.get('download_service'))
        print(request.POST.get('download_user'))
        if request.POST.get('download_service'):
            ruser = request.user
            today = datetime.datetime.today()
            print(today)
            yesterday = today - datetime.timedelta(1)
            tomorrow = today + datetime.timedelta(1)
            next_year = today.year + 1
            next_year_month = today.replace(day=1,month=1,year=next_year)
            first = today.replace(day=1)  # first date of current month
            previous_month_date = first - datetime.timedelta(days=1)  # this will be the last day of previous month
            older_month_date = previous_month_date.replace(day=1) - datetime.timedelta(days=1)# this will be the last day of previous to previous month
            start_date = previous_month_date
            end_date = older_month_date

            
            if request.POST.get('startDate'):
                start_date =  request.POST.get('startDate')

            if request.POST.get('endDate'):
                end_date = request.POST.get('endDate')
            
                
            if request.POST.get('endDate') == '' or request.POST.get('startDate') == '':
                messages.error(request,'Please Select Date Range')
                return render(request,'service_html/reports_v2.html')

            if request.POST.get('startDate') > request.POST.get('endDate'):
                messages.error(request,'Please Select Correct Date Range')
                return render(request,'service_html/reports_v2.html')

            services = Service.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
            services_today = Service.objects.filter(created_at=today)
            services_previous_month = Service.objects.filter(created_at__gte=previous_month_date,created_at__lte=today)
            services_older_months = Service.objects.filter(created_at__gte=older_month_date,created_at__lte=previous_month_date)
            services_overall = Service.objects.all()
            print(services)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="BC_service_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['FIRST NAME','LAST NAME','EMAIL','PHONE','CREATED AT','CREATED BY','LOAN TYPE','PURCHASE TYPE','JOB TYPE','JOB LOCATION','RENTAL INCOME(JOB)','RENTAL INCOME(BUSINESS)','HOW MUCH IN CASH(JOB)','HOW MUCH IN CASH(BUSINESS)','HOW MUCH IN ACCOUNT(JOB)','HOW MUCH IN ACCOUNT(BUSINESS)','TAKE HOME SALARY','DURATION IN PRESENT COMPANY','EXISTING EMI AMOUNT(JOB)','EXISTING EMI AMOUNT(BUSINESS)','BUSINESS LOCATION','DECLARED ITR','HOW MUCH ITR?','HOW MUCH IN ACCOUNT (ITR)','BUSINESS VINTAGE','NATURE OF BUSINESS','GST REGISTERED','KHATA','Property Location','AREA OF EXTENET (IH)','AREA OF EXTENET (SC)','AREA OF EXTENT (PLOT)','AREA OF EXTENT(FLAT)','AREA OF EXTENT(LAP)','Number Of Units','Number of Floors','Number of Units LAP','Number of Floor LAP','Bulding Age IH','Building Age LAP','PROJECT NAME','OC & CC RECIEVED','PLAN AVAILABLE(SC)','PLAN TYPE','PLAN AVAILABLE(IH)','PLAN AVAIALABLE(LAP)'])
            if request.POST.get('startDate') and request.POST.get('endDate'):
                for service in services:
                    writer.writerow(
                        [
                            service.first_name, 
                            service.last_name, 
                            service.email,
                            service.phone,
                            service.created_at.date(),
                            service.created_by.first_name + '' + service.created_by.last_name,
                            service.get_loan_type_display(),
                            service.get_purchase_type_display(),
                            service.get_job_type_display(),
                            service.job_location,
                            'YES' if service.rental_income_job else 'NO',
                            'YES' if service.rental_income_bus else 'NO',
                            service.how_much_in_cash_job,
                            service.how_much_in_cash_bus,
                            service.how_much_in_account_job,
                            service.how_much_in_account_bus,
                            service.take_home_salary,
                            service.get_duration_in_present_company_display(),
                            service.existing_emi_amount_job,
                            service.existing_emi_amount_bus,
                            service.business_location,
                            'YES' if service.declared_itr else 'NO',
                            service.how_much_itr,
                            service.how_much_in_account_itr,
                            service.business_vintage,
                            service.nature_of_business,
                            'YES' if service.gst_registered else 'NO',
                            service.khata,
                            service.property_location,
                            service.area_of_extent_ih,
                            service.area_of_extent_sc,
                            service.area_of_extent_plot,
                            service.area_of_extent_flat,
                            service.area_of_extent_lap,
                            service.number_of_unites,
                            service.number_of_floors,
                            service.number_of_units_lap,
                            service.number_of_floors_lap,
                            service.get_building_age_ih_display(),
                            service.get_building_age_lap_display(),
                            service.project_name,
                            service.oc_cc_received,
                            'YES' if service.plan_available_sc else 'NO',
                            service.get_plan_type_display(),
                            'YES' if service.plan_available_ih else 'NO',
                            'YES' if service.plan_available_lap else 'NO',
                            ]
                            )
            if request.POST.get('today'):
                for service in services_today:
                    writer.writerow(
                        [
                            service.first_name, 
                            service.last_name, 
                            service.email,
                            service.phone,
                            service.created_at.date(),
                            service.created_by.first_name + '' + service.created_by.last_name,
                            service.get_loan_type_display(),
                            service.get_purchase_type_display(),
                            service.get_job_type_display(),
                            service.job_location,
                            'YES' if service.rental_income_job else 'NO',
                            'YES' if service.rental_income_bus else 'NO',
                            service.how_much_in_cash_job,
                            service.how_much_in_cash_bus,
                            service.how_much_in_account_job,
                            service.how_much_in_account_bus,
                            service.take_home_salary,
                            service.get_duration_in_present_company_display(),
                            service.existing_emi_amount_job,
                            service.existing_emi_amount_bus,
                            service.business_location,
                            'YES' if service.declared_itr else 'NO',
                            service.how_much_itr,
                            service.how_much_in_account_itr,
                            service.business_vintage,
                            service.nature_of_business,
                            'YES' if service.gst_registered else 'NO',
                            service.khata,
                            service.property_location,
                            service.area_of_extent_ih,
                            service.area_of_extent_sc,
                            service.area_of_extent_plot,
                            service.area_of_extent_flat,
                            service.area_of_extent_lap,
                            service.number_of_unites,
                            service.number_of_floors,
                            service.number_of_units_lap,
                            service.number_of_floors_lap,
                            service.get_building_age_ih_display(),
                            service.get_building_age_lap_display(),
                            service.project_name,
                            service.oc_cc_received,
                            'YES' if service.plan_available_sc else 'NO',
                            service.get_plan_type_display(),
                            'YES' if service.plan_available_ih else 'NO',
                            'YES' if service.plan_available_lap else 'NO',
                            ]
                            )
            if services_previous_month:
                for service in services_previous_month:
                    writer.writerow(
                        [
                            service.first_name, 
                            service.last_name, 
                            service.email,
                            service.phone,
                            service.created_at.date(),
                            service.created_by.first_name + '' + service.created_by.last_name,
                            service.get_loan_type_display(),
                            service.get_purchase_type_display(),
                            service.get_job_type_display(),
                            service.job_location,
                            'YES' if service.rental_income_job else 'NO',
                            'YES' if service.rental_income_bus else 'NO',
                            service.how_much_in_cash_job,
                            service.how_much_in_cash_bus,
                            service.how_much_in_account_job,
                            service.how_much_in_account_bus,
                            service.take_home_salary,
                            service.get_duration_in_present_company_display(),
                            service.existing_emi_amount_job,
                            service.existing_emi_amount_bus,
                            service.business_location,
                            'YES' if service.declared_itr else 'NO',
                            service.how_much_itr,
                            service.how_much_in_account_itr,
                            service.business_vintage,
                            service.nature_of_business,
                            'YES' if service.gst_registered else 'NO',
                            service.khata,
                            service.property_location,
                            service.area_of_extent_ih,
                            service.area_of_extent_sc,
                            service.area_of_extent_plot,
                            service.area_of_extent_flat,
                            service.area_of_extent_lap,
                            service.number_of_unites,
                            service.number_of_floors,
                            service.number_of_units_lap,
                            service.number_of_floors_lap,
                            service.get_building_age_ih_display(),
                            service.get_building_age_lap_display(),
                            service.project_name,
                            service.oc_cc_received,
                            'YES' if service.plan_available_sc else 'NO',
                            service.get_plan_type_display(),
                            'YES' if service.plan_available_ih else 'NO',
                            'YES' if service.plan_available_lap else 'NO',
                            ]
                            )

            if services_older_months:
                for service in services_older_months:
                    writer.writerow(
                        [
                            service.first_name, 
                            service.last_name, 
                            service.email,
                            service.phone,
                            service.created_at.date(),
                            service.created_by.first_name + '' + service.created_by.last_name,
                            service.get_loan_type_display(),
                            service.get_purchase_type_display(),
                            service.get_job_type_display(),
                            service.job_location,
                            'YES' if service.rental_income_job else 'NO',
                            'YES' if service.rental_income_bus else 'NO',
                            service.how_much_in_cash_job,
                            service.how_much_in_cash_bus,
                            service.how_much_in_account_job,
                            service.how_much_in_account_bus,
                            service.take_home_salary,
                            service.get_duration_in_present_company_display(),
                            service.existing_emi_amount_job,
                            service.existing_emi_amount_bus,
                            service.business_location,
                            'YES' if service.declared_itr else 'NO',
                            service.how_much_itr,
                            service.how_much_in_account_itr,
                            service.business_vintage,
                            service.nature_of_business,
                            'YES' if service.gst_registered else 'NO',
                            service.khata,
                            service.property_location,
                            service.area_of_extent_ih,
                            service.area_of_extent_sc,
                            service.area_of_extent_plot,
                            service.area_of_extent_flat,
                            service.area_of_extent_lap,
                            service.number_of_unites,
                            service.number_of_floors,
                            service.number_of_units_lap,
                            service.number_of_floors_lap,
                            service.get_building_age_ih_display(),
                            service.get_building_age_lap_display(),
                            service.project_name,
                            service.oc_cc_received,
                            'YES' if service.plan_available_sc else 'NO',
                            service.get_plan_type_display(),
                            'YES' if service.plan_available_ih else 'NO',
                            'YES' if service.plan_available_lap else 'NO',
                            ]
                            )

            if services_overall:
                for service in services_overall:
                    writer.writerow(
                        [
                            service.first_name, 
                            service.last_name, 
                            service.email,
                            service.phone,
                            service.created_at.date(),
                            service.created_by.first_name + '' + service.created_by.last_name,
                            service.get_loan_type_display(),
                            service.get_purchase_type_display(),
                            service.get_job_type_display(),
                            service.job_location,
                            'YES' if service.rental_income_job else 'NO',
                            'YES' if service.rental_income_bus else 'NO',
                            service.how_much_in_cash_job,
                            service.how_much_in_cash_bus,
                            service.how_much_in_account_job,
                            service.how_much_in_account_bus,
                            service.take_home_salary,
                            service.get_duration_in_present_company_display(),
                            service.existing_emi_amount_job,
                            service.existing_emi_amount_bus,
                            service.business_location,
                            'YES' if service.declared_itr else 'NO',
                            service.how_much_itr,
                            service.how_much_in_account_itr,
                            service.business_vintage,
                            service.nature_of_business,
                            'YES' if service.gst_registered else 'NO',
                            service.khata,
                            service.property_location,
                            service.area_of_extent_ih,
                            service.area_of_extent_sc,
                            service.area_of_extent_plot,
                            service.area_of_extent_flat,
                            service.area_of_extent_lap,
                            service.number_of_unites,
                            service.number_of_floors,
                            service.number_of_units_lap,
                            service.number_of_floors_lap,
                            service.get_building_age_ih_display(),
                            service.get_building_age_lap_display(),
                            service.project_name,
                            service.oc_cc_received,
                            'YES' if service.plan_available_sc else 'NO',
                            service.get_plan_type_display(),
                            'YES' if service.plan_available_ih else 'NO',
                            'YES' if service.plan_available_lap else 'NO',
                            ]
                            )

            return response
        if request.POST.get('download_user'):
            ruser = request.user
            today = datetime.datetime.today()
            print(today)
            yesterday = today - datetime.timedelta(1)
            tomorrow = today + datetime.timedelta(1)
            if request.POST.get('startDate'):
                start_date =  request.POST.get('startDate')

            if request.POST.get('endDate'):
                end_date = request.POST.get('endDate')

            if request.POST.get('endDate') == '' or request.POST.get('startDate') == '':
                messages.error(request,'Please Select Date Range')
                return render(request,'service_html/reports_v2.html')

            if request.POST.get('startDate') > request.POST.get('endDate'):
                messages.error(request,'Please Select Correct Date Range')
                return render(request,'service_html/reports_v2.html')
            users = CustomUser.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
            print(users)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="BC_Users_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['FIRST NAME','LAST NAME','EMAIL','PHONE','CREATED AT','REFERRD BY','REFFERAL CODE','MANAGER NAME','ROLE','PROFESSIONAL OCCUPATION','HOUSING LOAN','MORTGAGE LOAN','VEHICAL LOAN','serviceS' ])
            for user in users:
                writer.writerow(
                    [
                        user.first_name, 
                        user.last_name, 
                        user.email,
                        user.phone,
                        user.created_at.date(),
                        user.referred_by,
                        user.referral_code,
                        user.manager.first_name if not user.role == 'ADMIN' else '',
                        user.role,
                        ','.join( str(occupation) for occupation in  user.professional_occupation.all()),
                        user.housing_loan,
                        user.mortgage_loan,
                        user.vehical_loan,
                        user.service_user.count(),

                        ]
                        )
            return response
        return render(request,'service_html/reports_v2.html')
    else:
        return render(request,'service_html/reports_v2.html')

@login_required(login_url='login')

@login_required(login_url='login')
def dashboard(request):

    if request.user.role == 'BO':
        return redirect('bodashboard')
    if request.user.role == 'CONNECTOR' and request.user.is_verified:
        ruser = request.user    
        today = datetime.date.today()
        jan = today.replace(day=1,month=1)
        feb = today.replace(day=1,month=2)
        mar = today.replace(day=1,month=3)
        apr = today.replace(day=1,month=4)
        may = today.replace(day=1,month=5)
        jun = today.replace(day=1,month=6)
        july = today.replace(day=1,month=7)
        aug = today.replace(day=1,month=8)
        sept = today.replace(day=1,month=9)
        octo = today.replace(day=1,month=10)
        nov = today.replace(day=1,month=11)
        dec = today.replace(day=1,month=12)
        next_year = today.year + 1
        next_year_month = today.replace(day=1,month=1,year=next_year)

        yesterday = today - datetime.timedelta(1)
        tomorrow = today + datetime.timedelta(1)
        first = today.replace(day=1)  # first date of current month
        previous_month_date = first - datetime.timedelta(days=1)  # this will be the last day of previous month
        older_month_date = previous_month_date.replace(day=1) - datetime.timedelta(days=1)# this will be the last day of previous to previous month
        start_date = previous_month_date
        end_date = older_month_date
        if request.POST.get('startDate')!= None:
            custom_start_date =  request.POST.get('startDate')
        else:
            custom_start_date = today
        
        if request.POST.get('endDate')!= None:
            custom_end_date = request.POST.get('endDate')
        else:
            custom_end_date = today

        registered_users = CustomUser.objects.filter(Q(manager=ruser)|Q(referred_by=ruser.referral_code)|Q(manager__referred_by=ruser.referral_code))
        direct_referrals = CustomUser.objects.filter(referred_by=ruser.referral_code,is_active=True).count()
        direct_referrals_previous_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        direct_referrals_current_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lt=today,is_active=True).count()
        direct_referrals_today = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        direct_referrals_yesterday = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        direct_referrals_custom = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=custom_start_date,created_at__lte=custom_end_date,is_active=True).count()

        if direct_referrals_current_month >0:
            direct_referrals_percentage = (direct_referrals_previous_month)*100/direct_referrals_current_month 
        else:
            direct_referrals_percentage = 0
        
        direct_referrals_jan = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        direct_referrals_feb = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        direct_referrals_mar = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        direct_referrals_apr = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        direct_referrals_may = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        direct_referrals_jun = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        direct_referrals_jul = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        direct_referrals_aug = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        direct_referrals_sept = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        direct_referrals_oct = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        direct_referrals_nov = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        direct_referrals_dec = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        indirect_referrals = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,is_active=True).count()
        indirect_referrals_previous_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        indirect_referrals_current_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lte=today,is_active=True).count()
        indirect_referrals_today = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        indirect_referrals_yesterday = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        indirect_referrals_custom = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__lte=custom_start_date,created_at__gte=custom_end_date,is_active=True).count()
        
        if indirect_referrals_current_month>0:
            indirect_referrals_percentage = (indirect_referrals_previous_month)*100/indirect_referrals_current_month 
        else:
            indirect_referrals_percentage = 0
        
        indirect_referrals_jan = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        indirect_referrals_feb = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        indirect_referrals_mar = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        indirect_referrals_apr = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        indirect_referrals_may = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        indirect_referrals_jun = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        indirect_referrals_jul = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        indirect_referrals_aug = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        indirect_referrals_sept = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        indirect_referrals_oct = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        indirect_referrals_nov = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        indirect_referrals_dec = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        
        total_referrals = direct_referrals + indirect_referrals
        total_referrals_previous_month = direct_referrals_previous_month + indirect_referrals_previous_month
        total_referrals_current_month = direct_referrals_current_month + indirect_referrals_current_month
        total_referrals_today = direct_referrals_today + indirect_referrals_today
        total_referrals_yesterday = direct_referrals_yesterday + indirect_referrals_yesterday
        total_referrals_custom = direct_referrals_custom + indirect_referrals_custom

        if total_referrals_current_month>0:
            total_referrals_percentage = (total_referrals_previous_month)*100/total_referrals_current_month
        else:
            total_referrals_percentage = 0
        total_referrals_jan = direct_referrals_jan + indirect_referrals_jan
        total_referrals_feb = direct_referrals_feb + indirect_referrals_feb
        total_referrals_mar = direct_referrals_mar + indirect_referrals_mar
        total_referrals_apr = direct_referrals_apr + indirect_referrals_apr
        total_referrals_may = direct_referrals_may + indirect_referrals_may
        total_referrals_jun = direct_referrals_jun + indirect_referrals_jun
        total_referrals_jul = direct_referrals_jul + indirect_referrals_jul
        total_referrals_aug = direct_referrals_aug + indirect_referrals_aug
        total_referrals_sept = direct_referrals_sept + indirect_referrals_sept
        total_referrals_oct = direct_referrals_oct + indirect_referrals_oct
        total_referrals_nov = direct_referrals_nov + indirect_referrals_nov
        total_referrals_dec = direct_referrals_dec + indirect_referrals_dec
        
        services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_services = Service.objects.filter(created_by=ruser).count()
        direct_services_previous_month = Service.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_services_current_month = Service.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_services_today = Service.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_services_yesterday = Service.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_services_custom = Service.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_services_current_month > 0:
            direct_services_percentage = (direct_services_previous_month)*100/direct_services_current_month
        else:
            direct_services_percentage = 0
        
        direct_services_jan = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_services_feb = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_services_mar = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_services_apr = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_services_may = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_services_jun = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_services_jul = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_services_aug = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_services_sept = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_services_oct = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_services_nov = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_services_dec = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_services_previous_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_services_current_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_services_today = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_services_yesterday = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_services_custom = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_services_current_month>0:
            indirect_services_percentage = (indirect_services_previous_month)*100/indirect_services_current_month
        else:
            indirect_services_percentage = 0
        indirect_services_jan = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_services_feb = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_services_mar = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_services_apr = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_services_may = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_services_jun = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_services_jul = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_services_aug = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_services_sept = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_services_oct = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_services_nov = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_services_dec = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_services = direct_services + indirect_services
        total_services_previous_month = direct_services_previous_month + indirect_services_previous_month
        total_services_current_month = direct_services_current_month + indirect_services_current_month
        total_services_today = direct_services_today + indirect_services_today
        total_services_yesterday = direct_services_yesterday + indirect_services_yesterday
        total_services_custom = direct_services_custom + indirect_services_custom

        if total_services_current_month>0:
            total_services_percentage = (total_services_previous_month)*100/total_services_current_month
        else:
            total_services_percentage = 0

        total_services_jan = direct_services_jan + indirect_services_jan
        total_services_feb = direct_services_feb + indirect_services_feb
        total_services_mar = direct_services_mar + indirect_services_mar
        total_services_apr = direct_services_apr + indirect_services_apr
        total_services_may = direct_services_may + indirect_services_may
        total_services_jun = direct_services_jun + indirect_services_jun
        total_services_jul = direct_services_jul + indirect_services_jul
        total_services_aug = direct_services_aug + indirect_services_aug
        total_services_sept = direct_services_sept + indirect_services_sept
        total_services_oct = direct_services_oct + indirect_services_oct
        total_services_nov = direct_services_nov + indirect_services_nov
        total_services_dec = direct_services_dec + indirect_services_dec
        

        context = {
            'user':ruser,
            'custom_start_date':custom_start_date,
            'custom_end_date':custom_end_date,
            'registered_users':registered_users,
            'direct_referrals':direct_referrals,
            'direct_referrals_today':direct_referrals_today,
            'direct_referrals_yesterday':direct_referrals_yesterday,
            'direct_referrals_custom':direct_referrals_custom,
            'direct_referrals_previous_month':direct_referrals_previous_month,
            'direct_referrals_current_month':direct_referrals_current_month,
            'direct_referrals_percentage':int(direct_referrals_percentage),
            'indirect_referrals':indirect_referrals,
            'indirect_referrals_today':indirect_referrals_today,
            'indirect_referrals_yesterday':indirect_referrals_yesterday,
            'indirect_referrals_custom':indirect_referrals_custom,
            'indirect_referrals_previous_month':indirect_referrals_previous_month,
            'indirect_referrals_current_month':indirect_referrals_current_month,
            'indirect_referrals_percentage':int(indirect_referrals_percentage),
            'total_referrals':total_referrals,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_today':total_referrals_today,
            'total_referrals_yesterday':total_referrals_yesterday,
            'total_referrals_previous_month':total_referrals_previous_month,
            'total_referrals_current_month':total_referrals_current_month,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_percentage':int(total_referrals_percentage),
            'services':services,
            'direct_services':direct_services,
            'direct_services_today':direct_services_today,
            'direct_services_yesterday':direct_services_yesterday,
            'direct_services_custom':direct_services_custom,
            'direct_services_previous_month':direct_services_previous_month,
            'direct_services_current_month':direct_services_current_month,
            'direct_services_percentage':int(direct_services_percentage),
            'indirect_services':indirect_services,
            'indirect_services_today':indirect_services_today,
            'indirect_services_yesterday':indirect_services_yesterday,
            'indirect_services_previous_month':indirect_services_previous_month,
            'indirect_services_current_month':indirect_services_current_month,
            'indirect_services_custom':indirect_services_custom,
            'indirect_services_percentage':int(indirect_services_percentage),
            'total_services':total_services,
            'total_services_today':total_services_today,
            'total_services_yesterday':total_services_yesterday,
            'total_services_custom':total_services_custom,
            'total_services_previous_month':total_services_previous_month,
            'total_services_current_month':total_services_current_month,
            'total_services_percentage':int(total_services_percentage),
            'direct_referrals_jan' : direct_referrals_jan ,
            'direct_referrals_feb' : direct_referrals_feb ,
            'direct_referrals_mar' : direct_referrals_mar ,
            'direct_referrals_apr' : direct_referrals_apr ,
            'direct_referrals_may' : direct_referrals_may ,
            'direct_referrals_jun' : direct_referrals_jun ,
            'direct_referrals_jul' : direct_referrals_jul ,
            'direct_referrals_aug' : direct_referrals_aug ,
            'direct_referrals_sept': direct_referrals_sept,
            'direct_referrals_oct' : direct_referrals_oct ,
            'direct_referrals_nov' : direct_referrals_nov ,
            'direct_referrals_dec' : direct_referrals_dec ,
            'indirect_referrals_jan' : indirect_referrals_jan ,
            'indirect_referrals_feb' : indirect_referrals_feb ,
            'indirect_referrals_mar' : indirect_referrals_mar ,
            'indirect_referrals_apr' : indirect_referrals_apr ,
            'indirect_referrals_may' : indirect_referrals_may ,
            'indirect_referrals_jun' : indirect_referrals_jun ,
            'indirect_referrals_jul' : indirect_referrals_jul ,
            'indirect_referrals_aug' : indirect_referrals_aug ,
            'indirect_referrals_sept': indirect_referrals_sept,
            'indirect_referrals_oct' : indirect_referrals_oct ,
            'indirect_referrals_nov' : indirect_referrals_nov ,
            'indirect_referrals_dec' : indirect_referrals_dec ,
            'direct_services_jan' : direct_services_jan ,
            'direct_services_feb' : direct_services_feb ,
            'direct_services_mar' : direct_services_mar ,
            'direct_services_apr' : direct_services_apr ,
            'direct_services_may' : direct_services_may ,
            'direct_services_jun' : direct_services_jun ,
            'direct_services_jul' : direct_services_jul ,
            'direct_services_aug' : direct_services_aug ,
            'direct_services_sept': direct_services_sept,
            'direct_services_oct' : direct_services_oct ,
            'direct_services_nov' : direct_services_nov ,
            'direct_services_dec' : direct_services_dec ,
            'indirect_services_jan' : indirect_services_jan ,
            'indirect_services_feb' : indirect_services_feb ,
            'indirect_services_mar' : indirect_services_mar ,
            'indirect_services_apr' : indirect_services_apr ,
            'indirect_services_may' : indirect_services_may ,
            'indirect_services_jun' : indirect_services_jun ,
            'indirect_services_jul' : indirect_services_jul ,
            'indirect_services_aug' : indirect_services_aug ,
            'indirect_services_sept': indirect_services_sept,
            'indirect_services_oct' : indirect_services_oct ,
            'indirect_services_nov' : indirect_services_nov ,
            'indirect_services_dec' : indirect_services_dec ,
            'total_referrals_jan': total_referrals_jan ,
            'total_referrals_feb': total_referrals_feb ,
            'total_referrals_mar': total_referrals_mar ,
            'total_referrals_apr': total_referrals_apr ,
            'total_referrals_may': total_referrals_may ,
            'total_referrals_jun': total_referrals_jun ,
            'total_referrals_jul': total_referrals_jul ,
            'total_referrals_aug': total_referrals_aug ,
            'total_referrals_sept': total_referrals_sept,
            'total_referrals_oct': total_referrals_oct ,
            'total_referrals_nov': total_referrals_nov ,
            'total_referrals_dec': total_referrals_dec ,
            'total_services_jan': total_services_jan ,
            'total_services_feb': total_services_feb ,
            'total_services_mar': total_services_mar ,
            'total_services_apr': total_services_apr ,
            'total_services_may': total_services_may ,
            'total_services_jun': total_services_jun ,
            'total_services_jul': total_services_jul ,
            'total_services_aug': total_services_aug ,
            'total_services_sept': total_services_sept,
            'total_services_oct': total_services_oct ,
            'total_services_nov': total_services_nov ,
            'total_services_dec': total_services_dec,
        }
        return render(request,"user_html/con_dashboard_v2.html",context)
    if request.user.role == 'AF' and request.user.is_verified:
        service_notification_count = Notification.objects.filter(notified_user = request.user.id,read_service_notification=True).count()
        ruser = request.user    
        today = datetime.date.today()
        jan = today.replace(day=1,month=1)
        feb = today.replace(day=1,month=2)
        mar = today.replace(day=1,month=3)
        apr = today.replace(day=1,month=4)
        may = today.replace(day=1,month=5)
        jun = today.replace(day=1,month=6)
        july = today.replace(day=1,month=7)
        aug = today.replace(day=1,month=8)
        sept = today.replace(day=1,month=9)
        octo = today.replace(day=1,month=10)
        nov = today.replace(day=1,month=11)
        dec = today.replace(day=1,month=12)
        next_year = today.year + 1
        next_year_month = today.replace(day=1,month=1,year=next_year)

        yesterday = today - datetime.timedelta(1)
        tomorrow = today + datetime.timedelta(1)
        first = today.replace(day=1)  # first date of current month
        previous_month_date = first - datetime.timedelta(days=1)  # this will be the last day of previous month
        older_month_date = previous_month_date.replace(day=1) - datetime.timedelta(days=1)# this will be the last day of previous to previous month
        start_date = previous_month_date
        end_date = older_month_date
        if request.POST.get('startDate')!= None:
            custom_start_date =  request.POST.get('startDate')
        else:
            custom_start_date = today
        
        if request.POST.get('endDate')!= None:
            custom_end_date = request.POST.get('endDate')
        else:
            custom_end_date = today

        registered_users = CustomUser.objects.filter(Q(manager=ruser)|Q(referred_by=ruser.referral_code)|Q(manager__referred_by=ruser.referral_code))
        direct_referrals = CustomUser.objects.filter(referred_by=ruser.referral_code,is_active=True).count()
        direct_referrals_previous_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        direct_referrals_current_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lt=today,is_active=True).count()
        direct_referrals_today = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        direct_referrals_yesterday = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        direct_referrals_custom = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=custom_start_date,created_at__lte=custom_end_date,is_active=True).count()

        if direct_referrals_current_month >0:
            direct_referrals_percentage = (direct_referrals_previous_month)*100/direct_referrals_current_month 
        else:
            direct_referrals_percentage = 0
        
        direct_referrals_jan = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        direct_referrals_feb = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        direct_referrals_mar = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        direct_referrals_apr = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        direct_referrals_may = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        direct_referrals_jun = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        direct_referrals_jul = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        direct_referrals_aug = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        direct_referrals_sept = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        direct_referrals_oct = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        direct_referrals_nov = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        direct_referrals_dec = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        indirect_referrals = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,is_active=True).count()
        indirect_referrals_previous_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        indirect_referrals_current_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lte=today,is_active=True).count()
        indirect_referrals_today = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        indirect_referrals_yesterday = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        indirect_referrals_custom = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__lte=custom_start_date,created_at__gte=custom_end_date,is_active=True).count()
        
        if indirect_referrals_current_month>0:
            indirect_referrals_percentage = (indirect_referrals_previous_month)*100/indirect_referrals_current_month 
        else:
            indirect_referrals_percentage = 0
        
        indirect_referrals_jan = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        indirect_referrals_feb = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        indirect_referrals_mar = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        indirect_referrals_apr = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        indirect_referrals_may = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        indirect_referrals_jun = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        indirect_referrals_jul = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        indirect_referrals_aug = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        indirect_referrals_sept = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        indirect_referrals_oct = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        indirect_referrals_nov = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        indirect_referrals_dec = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        
        total_referrals = direct_referrals + indirect_referrals
        total_referrals_previous_month = direct_referrals_previous_month + indirect_referrals_previous_month
        total_referrals_current_month = direct_referrals_current_month + indirect_referrals_current_month
        total_referrals_today = direct_referrals_today + indirect_referrals_today
        total_referrals_yesterday = direct_referrals_yesterday + indirect_referrals_yesterday
        total_referrals_custom = direct_referrals_custom + indirect_referrals_custom

        if total_referrals_current_month>0:
            total_referrals_percentage = (total_referrals_previous_month)*100/total_referrals_current_month
        else:
            total_referrals_percentage = 0
        total_referrals_jan = direct_referrals_jan + indirect_referrals_jan
        total_referrals_feb = direct_referrals_feb + indirect_referrals_feb
        total_referrals_mar = direct_referrals_mar + indirect_referrals_mar
        total_referrals_apr = direct_referrals_apr + indirect_referrals_apr
        total_referrals_may = direct_referrals_may + indirect_referrals_may
        total_referrals_jun = direct_referrals_jun + indirect_referrals_jun
        total_referrals_jul = direct_referrals_jul + indirect_referrals_jul
        total_referrals_aug = direct_referrals_aug + indirect_referrals_aug
        total_referrals_sept = direct_referrals_sept + indirect_referrals_sept
        total_referrals_oct = direct_referrals_oct + indirect_referrals_oct
        total_referrals_nov = direct_referrals_nov + indirect_referrals_nov
        total_referrals_dec = direct_referrals_dec + indirect_referrals_dec

        
        services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_services = Service.objects.filter(created_by=ruser).count()
        direct_services_previous_month = Service.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_services_current_month = Service.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_services_today = Service.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_services_yesterday = Service.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_services_custom = Service.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_services_current_month > 0:
            direct_services_percentage = (direct_services_previous_month)*100/direct_services_current_month
        else:
            direct_services_percentage = 0
        
        direct_services_jan = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_services_feb = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_services_mar = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_services_apr = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_services_may = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_services_jun = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_services_jul = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_services_aug = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_services_sept = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_services_oct = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_services_nov = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_services_dec = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_services_previous_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_services_current_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_services_today = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_services_yesterday = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_services_custom = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_services_current_month>0:
            indirect_services_percentage = (indirect_services_previous_month)*100/indirect_services_current_month
        else:
            indirect_services_percentage = 0
        indirect_services_jan = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_services_feb = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_services_mar = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_services_apr = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_services_may = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_services_jun = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_services_jul = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_services_aug = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_services_sept = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_services_oct = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_services_nov = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_services_dec = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_services = direct_services + indirect_services
        total_services_previous_month = direct_services_previous_month + indirect_services_previous_month
        total_services_current_month = direct_services_current_month + indirect_services_current_month
        total_services_today = direct_services_today + indirect_services_today
        total_services_yesterday = direct_services_yesterday + indirect_services_yesterday
        total_services_custom = direct_services_custom + indirect_services_custom

        if total_services_current_month>0:
            total_services_percentage = (total_services_previous_month)*100/total_services_current_month
        else:
            total_services_percentage = 0

        total_services_jan = direct_services_jan + indirect_services_jan
        total_services_feb = direct_services_feb + indirect_services_feb
        total_services_mar = direct_services_mar + indirect_services_mar
        total_services_apr = direct_services_apr + indirect_services_apr
        total_services_may = direct_services_may + indirect_services_may
        total_services_jun = direct_services_jun + indirect_services_jun
        total_services_jul = direct_services_jul + indirect_services_jul
        total_services_aug = direct_services_aug + indirect_services_aug
        total_services_sept = direct_services_sept + indirect_services_sept
        total_services_oct = direct_services_oct + indirect_services_oct
        total_services_nov = direct_services_nov + indirect_services_nov
        total_services_dec = direct_services_dec + indirect_services_dec
    

        context = {
            'user':ruser,
            'custom_start_date':custom_start_date,
            'custom_end_date':custom_end_date,
            'registered_users':registered_users,
            'direct_referrals':direct_referrals,
            'direct_referrals_today':direct_referrals_today,
            'direct_referrals_yesterday':direct_referrals_yesterday,
            'direct_referrals_custom':direct_referrals_custom,
            'direct_referrals_previous_month':direct_referrals_previous_month,
            'direct_referrals_current_month':direct_referrals_current_month,
            'direct_referrals_percentage':int(direct_referrals_percentage),
            'indirect_referrals':indirect_referrals,
            'indirect_referrals_today':indirect_referrals_today,
            'indirect_referrals_yesterday':indirect_referrals_yesterday,
            'indirect_referrals_custom':indirect_referrals_custom,
            'indirect_referrals_previous_month':indirect_referrals_previous_month,
            'indirect_referrals_current_month':indirect_referrals_current_month,
            'indirect_referrals_percentage':int(indirect_referrals_percentage),
            'total_referrals':total_referrals,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_today':total_referrals_today,
            'total_referrals_yesterday':total_referrals_yesterday,
            'total_referrals_previous_month':total_referrals_previous_month,
            'total_referrals_current_month':total_referrals_current_month,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_percentage':int(total_referrals_percentage),
            'services':services,
            'direct_services':direct_services,
            'direct_services_today':direct_services_today,
            'direct_services_yesterday':direct_services_yesterday,
            'direct_services_custom':direct_services_custom,
            'direct_services_previous_month':direct_services_previous_month,
            'direct_services_current_month':direct_services_current_month,
            'direct_services_percentage':int(direct_services_percentage),
            'indirect_services':indirect_services,
            'indirect_services_today':indirect_services_today,
            'indirect_services_yesterday':indirect_services_yesterday,
            'indirect_services_previous_month':indirect_services_previous_month,
            'indirect_services_current_month':indirect_services_current_month,
            'indirect_services_custom':indirect_services_custom,
            'indirect_services_percentage':int(indirect_services_percentage),
            'total_services':total_services,
            'total_services_today':total_services_today,
            'total_services_yesterday':total_services_yesterday,
            'total_services_custom':total_services_custom,
            'total_services_previous_month':total_services_previous_month,
            'total_services_current_month':total_services_current_month,
            'total_services_percentage':int(total_services_percentage),
            'direct_referrals_jan' : direct_referrals_jan ,
            'direct_referrals_feb' : direct_referrals_feb ,
            'direct_referrals_mar' : direct_referrals_mar ,
            'direct_referrals_apr' : direct_referrals_apr ,
            'direct_referrals_may' : direct_referrals_may ,
            'direct_referrals_jun' : direct_referrals_jun ,
            'direct_referrals_jul' : direct_referrals_jul ,
            'direct_referrals_aug' : direct_referrals_aug ,
            'direct_referrals_sept': direct_referrals_sept,
            'direct_referrals_oct' : direct_referrals_oct ,
            'direct_referrals_nov' : direct_referrals_nov ,
            'direct_referrals_dec' : direct_referrals_dec ,
            'indirect_referrals_jan' : indirect_referrals_jan ,
            'indirect_referrals_feb' : indirect_referrals_feb ,
            'indirect_referrals_mar' : indirect_referrals_mar ,
            'indirect_referrals_apr' : indirect_referrals_apr ,
            'indirect_referrals_may' : indirect_referrals_may ,
            'indirect_referrals_jun' : indirect_referrals_jun ,
            'indirect_referrals_jul' : indirect_referrals_jul ,
            'indirect_referrals_aug' : indirect_referrals_aug ,
            'indirect_referrals_sept': indirect_referrals_sept,
            'indirect_referrals_oct' : indirect_referrals_oct ,
            'indirect_referrals_nov' : indirect_referrals_nov ,
            'indirect_referrals_dec' : indirect_referrals_dec ,
            'direct_services_jan' : direct_services_jan ,
            'direct_services_feb' : direct_services_feb ,
            'direct_services_mar' : direct_services_mar ,
            'direct_services_apr' : direct_services_apr ,
            'direct_services_may' : direct_services_may ,
            'direct_services_jun' : direct_services_jun ,
            'direct_services_jul' : direct_services_jul ,
            'direct_services_aug' : direct_services_aug ,
            'direct_services_sept': direct_services_sept,
            'direct_services_oct' : direct_services_oct ,
            'direct_services_nov' : direct_services_nov ,
            'direct_services_dec' : direct_services_dec ,
            'indirect_services_jan' : indirect_services_jan ,
            'indirect_services_feb' : indirect_services_feb ,
            'indirect_services_mar' : indirect_services_mar ,
            'indirect_services_apr' : indirect_services_apr ,
            'indirect_services_may' : indirect_services_may ,
            'indirect_services_jun' : indirect_services_jun ,
            'indirect_services_jul' : indirect_services_jul ,
            'indirect_services_aug' : indirect_services_aug ,
            'indirect_services_sept': indirect_services_sept,
            'indirect_services_oct' : indirect_services_oct ,
            'indirect_services_nov' : indirect_services_nov ,
            'indirect_services_dec' : indirect_services_dec ,
            'total_referrals_jan': total_referrals_jan ,
            'total_referrals_feb': total_referrals_feb ,
            'total_referrals_mar': total_referrals_mar ,
            'total_referrals_apr': total_referrals_apr ,
            'total_referrals_may': total_referrals_may ,
            'total_referrals_jun': total_referrals_jun ,
            'total_referrals_jul': total_referrals_jul ,
            'total_referrals_aug': total_referrals_aug ,
            'total_referrals_sept': total_referrals_sept,
            'total_referrals_oct': total_referrals_oct ,
            'total_referrals_nov': total_referrals_nov ,
            'total_referrals_dec': total_referrals_dec ,
            'total_services_jan': total_services_jan ,
            'total_services_feb': total_services_feb ,
            'total_services_mar': total_services_mar ,
            'total_services_apr': total_services_apr ,
            'total_services_may': total_services_may ,
            'total_services_jun': total_services_jun ,
            'total_services_jul': total_services_jul ,
            'total_services_aug': total_services_aug ,
            'total_services_sept': total_services_sept,
            'total_services_oct': total_services_oct ,
            'total_services_nov': total_services_nov ,
            'total_services_dec': total_services_dec,
            
        }
        return render(request,"user_html/af_dashboard_v2.html",context)
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')
    else:

        ruser = request.user    
        today = datetime.date.today()
        jan = today.replace(day=1,month=1)
        feb = today.replace(day=1,month=2)
        mar = today.replace(day=1,month=3)
        apr = today.replace(day=1,month=4)
        may = today.replace(day=1,month=5)
        jun = today.replace(day=1,month=6)
        july = today.replace(day=1,month=7)
        aug = today.replace(day=1,month=8)
        sept = today.replace(day=1,month=9)
        octo = today.replace(day=1,month=10)
        nov = today.replace(day=1,month=11)
        dec = today.replace(day=1,month=12)
        next_year = today.year + 1
        next_year_month = today.replace(day=1,month=1,year=next_year)

        yesterday = today - datetime.timedelta(1)
        tomorrow = today + datetime.timedelta(1)
        first = today.replace(day=1)  # first date of current month
        previous_month_date = first - datetime.timedelta(days=1)  # this will be the last day of previous month
        older_month_date = previous_month_date.replace(day=1) - datetime.timedelta(days=1)# this will be the last day of previous to previous month
        start_date = previous_month_date
        end_date = older_month_date
        if request.POST.get('startDate')!= None:
            custom_start_date =  request.POST.get('startDate')
        else:
            custom_start_date = today
        
        if request.POST.get('endDate')!= None:
            custom_end_date = request.POST.get('endDate')
        else:
            custom_end_date = today

        registered_users = CustomUser.objects.filter(Q(manager=ruser)|Q(referred_by=ruser.referral_code)|Q(manager__referred_by=ruser.referral_code))
        direct_referrals = CustomUser.objects.filter(referred_by=ruser.referral_code,is_active=True).count()
        direct_referrals_previous_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        direct_referrals_current_month = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lt=today,is_active=True).count()
        direct_referrals_today = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        direct_referrals_yesterday = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        direct_referrals_custom = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=custom_start_date,created_at__lte=custom_end_date,is_active=True).count()

        if direct_referrals_current_month >0:
            direct_referrals_percentage = (direct_referrals_previous_month)*100/direct_referrals_current_month 
        else:
            direct_referrals_percentage = 0
        
        direct_referrals_jan = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        direct_referrals_feb = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        direct_referrals_mar = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        direct_referrals_apr = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        direct_referrals_may = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        direct_referrals_jun = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        direct_referrals_jul = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        direct_referrals_aug = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        direct_referrals_sept = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        direct_referrals_oct = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        direct_referrals_nov = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        direct_referrals_dec = CustomUser.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        indirect_referrals = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,is_active=True).count()
        indirect_referrals_previous_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=start_date,created_at__lt=end_date,is_active=True).count()
        indirect_referrals_current_month = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=previous_month_date,created_at__lte=today,is_active=True).count()
        indirect_referrals_today = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gt=yesterday,created_at__lt=tomorrow,is_active=True).count()
        indirect_referrals_yesterday = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at=yesterday,is_active=True).count()
        indirect_referrals_custom = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__lte=custom_start_date,created_at__gte=custom_end_date,is_active=True).count()
        
        if indirect_referrals_current_month>0:
            indirect_referrals_percentage = (indirect_referrals_previous_month)*100/indirect_referrals_current_month 
        else:
            indirect_referrals_percentage = 0
        
        indirect_referrals_jan = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb,is_active=True).count()
        indirect_referrals_feb = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar,is_active=True).count()
        indirect_referrals_mar = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr,is_active=True).count()
        indirect_referrals_apr = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may,is_active=True).count()
        indirect_referrals_may = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun,is_active=True).count()
        indirect_referrals_jun = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july,is_active=True).count()
        indirect_referrals_jul = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug,is_active=True).count()
        indirect_referrals_aug = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept,is_active=True).count()
        indirect_referrals_sept = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo,is_active=True).count()
        indirect_referrals_oct = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov,is_active=True).count()
        indirect_referrals_nov = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec,is_active=True).count()
        indirect_referrals_dec = CustomUser.objects.filter(manager__referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month,is_active=True).count()

        
        total_referrals = direct_referrals + indirect_referrals
        total_referrals_previous_month = direct_referrals_previous_month + indirect_referrals_previous_month
        total_referrals_current_month = direct_referrals_current_month + indirect_referrals_current_month
        total_referrals_today = direct_referrals_today + indirect_referrals_today
        total_referrals_yesterday = direct_referrals_yesterday + indirect_referrals_yesterday
        total_referrals_custom = direct_referrals_custom + indirect_referrals_custom

        if total_referrals_current_month>0:
            total_referrals_percentage = (total_referrals_previous_month)*100/total_referrals_current_month
        else:
            total_referrals_percentage = 0
        total_referrals_jan = direct_referrals_jan + indirect_referrals_jan
        total_referrals_feb = direct_referrals_feb + indirect_referrals_feb
        total_referrals_mar = direct_referrals_mar + indirect_referrals_mar
        total_referrals_apr = direct_referrals_apr + indirect_referrals_apr
        total_referrals_may = direct_referrals_may + indirect_referrals_may
        total_referrals_jun = direct_referrals_jun + indirect_referrals_jun
        total_referrals_jul = direct_referrals_jul + indirect_referrals_jul
        total_referrals_aug = direct_referrals_aug + indirect_referrals_aug
        total_referrals_sept = direct_referrals_sept + indirect_referrals_sept
        total_referrals_oct = direct_referrals_oct + indirect_referrals_oct
        total_referrals_nov = direct_referrals_nov + indirect_referrals_nov
        total_referrals_dec = direct_referrals_dec + indirect_referrals_dec
        
        services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_services = Service.objects.filter(created_by=ruser).count()
        direct_services_previous_month = Service.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_services_current_month = Service.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_services_today = Service.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_services_yesterday = Service.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_services_custom = Service.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_services_current_month > 0:
            direct_services_percentage = (direct_services_previous_month)*100/direct_services_current_month
        else:
            direct_services_percentage = 0
        
        direct_services_jan = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_services_feb = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_services_mar = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_services_apr = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_services_may = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_services_jun = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_services_jul = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_services_aug = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_services_sept = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_services_oct = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_services_nov = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_services_dec = Service.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_services = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_services_previous_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_services_current_month = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_services_today = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_services_yesterday = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_services_custom = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_services_current_month>0:
            indirect_services_percentage = (indirect_services_previous_month)*100/indirect_services_current_month
        else:
            indirect_services_percentage = 0
        indirect_services_jan = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_services_feb = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_services_mar = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_services_apr = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_services_may = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_services_jun = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_services_jul = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_services_aug = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_services_sept = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_services_oct = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_services_nov = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_services_dec = Service.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_services = direct_services + indirect_services
        total_services_previous_month = direct_services_previous_month + indirect_services_previous_month
        total_services_current_month = direct_services_current_month + indirect_services_current_month
        total_services_today = direct_services_today + indirect_services_today
        total_services_yesterday = direct_services_yesterday + indirect_services_yesterday
        total_services_custom = direct_services_custom + indirect_services_custom

        if total_services_current_month>0:
            total_services_percentage = (total_services_previous_month)*100/total_services_current_month
        else:
            total_services_percentage = 0

        total_services_jan = direct_services_jan + indirect_services_jan
        total_services_feb = direct_services_feb + indirect_services_feb
        total_services_mar = direct_services_mar + indirect_services_mar
        total_services_apr = direct_services_apr + indirect_services_apr
        total_services_may = direct_services_may + indirect_services_may
        total_services_jun = direct_services_jun + indirect_services_jun
        total_services_jul = direct_services_jul + indirect_services_jul
        total_services_aug = direct_services_aug + indirect_services_aug
        total_services_sept = direct_services_sept + indirect_services_sept
        total_services_oct = direct_services_oct + indirect_services_oct
        total_services_nov = direct_services_nov + indirect_services_nov
        total_services_dec = direct_services_dec + indirect_services_dec
        

        context = {
            'user':ruser,
            'custom_start_date':custom_start_date,
            'custom_end_date':custom_end_date,
            'registered_users':registered_users,
            'direct_referrals':direct_referrals,
            'direct_referrals_today':direct_referrals_today,
            'direct_referrals_yesterday':direct_referrals_yesterday,
            'direct_referrals_custom':direct_referrals_custom,
            'direct_referrals_previous_month':direct_referrals_previous_month,
            'direct_referrals_current_month':direct_referrals_current_month,
            'direct_referrals_percentage':int(direct_referrals_percentage),
            'indirect_referrals':indirect_referrals,
            'indirect_referrals_today':indirect_referrals_today,
            'indirect_referrals_yesterday':indirect_referrals_yesterday,
            'indirect_referrals_custom':indirect_referrals_custom,
            'indirect_referrals_previous_month':indirect_referrals_previous_month,
            'indirect_referrals_current_month':indirect_referrals_current_month,
            'indirect_referrals_percentage':int(indirect_referrals_percentage),
            'total_referrals':total_referrals,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_today':total_referrals_today,
            'total_referrals_yesterday':total_referrals_yesterday,
            'total_referrals_previous_month':total_referrals_previous_month,
            'total_referrals_current_month':total_referrals_current_month,
            'total_referrals_custom':total_referrals_custom,
            'total_referrals_percentage':int(total_referrals_percentage),
            'services':services,
            'direct_services':direct_services,
            'direct_services_today':direct_services_today,
            'direct_services_yesterday':direct_services_yesterday,
            'direct_services_custom':direct_services_custom,
            'direct_services_previous_month':direct_services_previous_month,
            'direct_services_current_month':direct_services_current_month,
            'direct_services_percentage':int(direct_services_percentage),
            'indirect_services':indirect_services,
            'indirect_services_today':indirect_services_today,
            'indirect_services_yesterday':indirect_services_yesterday,
            'indirect_services_previous_month':indirect_services_previous_month,
            'indirect_services_current_month':indirect_services_current_month,
            'indirect_services_custom':indirect_services_custom,
            'indirect_services_percentage':int(indirect_services_percentage),
            'total_services':total_services,
            'total_services_today':total_services_today,
            'total_services_yesterday':total_services_yesterday,
            'total_services_custom':total_services_custom,
            'total_services_previous_month':total_services_previous_month,
            'total_services_current_month':total_services_current_month,
            'total_services_percentage':int(total_services_percentage),
            'direct_referrals_jan' : direct_referrals_jan ,
            'direct_referrals_feb' : direct_referrals_feb ,
            'direct_referrals_mar' : direct_referrals_mar ,
            'direct_referrals_apr' : direct_referrals_apr ,
            'direct_referrals_may' : direct_referrals_may ,
            'direct_referrals_jun' : direct_referrals_jun ,
            'direct_referrals_jul' : direct_referrals_jul ,
            'direct_referrals_aug' : direct_referrals_aug ,
            'direct_referrals_sept': direct_referrals_sept,
            'direct_referrals_oct' : direct_referrals_oct ,
            'direct_referrals_nov' : direct_referrals_nov ,
            'direct_referrals_dec' : direct_referrals_dec ,
            'indirect_referrals_jan' : indirect_referrals_jan ,
            'indirect_referrals_feb' : indirect_referrals_feb ,
            'indirect_referrals_mar' : indirect_referrals_mar ,
            'indirect_referrals_apr' : indirect_referrals_apr ,
            'indirect_referrals_may' : indirect_referrals_may ,
            'indirect_referrals_jun' : indirect_referrals_jun ,
            'indirect_referrals_jul' : indirect_referrals_jul ,
            'indirect_referrals_aug' : indirect_referrals_aug ,
            'indirect_referrals_sept': indirect_referrals_sept,
            'indirect_referrals_oct' : indirect_referrals_oct ,
            'indirect_referrals_nov' : indirect_referrals_nov ,
            'indirect_referrals_dec' : indirect_referrals_dec ,
            'direct_services_jan' : direct_services_jan ,
            'direct_services_feb' : direct_services_feb ,
            'direct_services_mar' : direct_services_mar ,
            'direct_services_apr' : direct_services_apr ,
            'direct_services_may' : direct_services_may ,
            'direct_services_jun' : direct_services_jun ,
            'direct_services_jul' : direct_services_jul ,
            'direct_services_aug' : direct_services_aug ,
            'direct_services_sept': direct_services_sept,
            'direct_services_oct' : direct_services_oct ,
            'direct_services_nov' : direct_services_nov ,
            'direct_services_dec' : direct_services_dec ,
            'indirect_services_jan' : indirect_services_jan ,
            'indirect_services_feb' : indirect_services_feb ,
            'indirect_services_mar' : indirect_services_mar ,
            'indirect_services_apr' : indirect_services_apr ,
            'indirect_services_may' : indirect_services_may ,
            'indirect_services_jun' : indirect_services_jun ,
            'indirect_services_jul' : indirect_services_jul ,
            'indirect_services_aug' : indirect_services_aug ,
            'indirect_services_sept': indirect_services_sept,
            'indirect_services_oct' : indirect_services_oct ,
            'indirect_services_nov' : indirect_services_nov ,
            'indirect_services_dec' : indirect_services_dec ,
            'total_referrals_jan': total_referrals_jan ,
            'total_referrals_feb': total_referrals_feb ,
            'total_referrals_mar': total_referrals_mar ,
            'total_referrals_apr': total_referrals_apr ,
            'total_referrals_may': total_referrals_may ,
            'total_referrals_jun': total_referrals_jun ,
            'total_referrals_jul': total_referrals_jul ,
            'total_referrals_aug': total_referrals_aug ,
            'total_referrals_sept': total_referrals_sept,
            'total_referrals_oct': total_referrals_oct ,
            'total_referrals_nov': total_referrals_nov ,
            'total_referrals_dec': total_referrals_dec ,
            'total_services_jan': total_services_jan ,
            'total_services_feb': total_services_feb ,
            'total_services_mar': total_services_mar ,
            'total_services_apr': total_services_apr ,
            'total_services_may': total_services_may ,
            'total_services_jun': total_services_jun ,
            'total_services_jul': total_services_jul ,
            'total_services_aug': total_services_aug ,
            'total_services_sept': total_services_sept,
            'total_services_oct': total_services_oct ,
            'total_services_nov': total_services_nov ,
            'total_services_dec': total_services_dec,
            
        }

        return render(request,"user_html/dashboard_v2.html")

def test(request):
    return render(request,'service_html/test.html')

@login_required(login_url='login')
def service_verify(request):
    if request.user.role == 'ACCOUNT' or request.user.role == 'ADMIN' :
        services = Service.objects.filter(verification_pending=True)
        print(services)
        count = services.count()
        page = request.GET.get('page', 1)
        paginator = Paginator(services, 10)
        try:
            services = paginator.page(page)
        except PageNotAnInteger:
            services = paginator.page(1)
        except EmptyPage:
            services = paginator.page(paginator.num_pages)
        if request.method == 'POST':
            if request.POST.get('verification_approve'):
                    verified_service =Service.objects.get(id=request.POST.get('verification_approve'))
                    verified_service.verification_pending = False
                    verified_service.verification_approved = True
                    verified_service.verification_rejected = False
                    print(request)
                    verified_service.verification_approved_by = request.user
                    verified_service.verification_approved_at = datetime.datetime.utcnow().replace(tzinfo=utc)  
                    verified_service.save()
                    return redirect('account')
            
            if request.POST.get('verification_reject'):
                rejected_service = Service.objects.get(id=request.POST.get('verification_reject'))
                rejected_service.verification_pending = False
                rejected_service.verification_rejected = True
                rejected_service.verification_approved = False
                rejected_service.disbursement_process_completed_approved = False
                rejected_service.verification_rejected_by = request.user
                rejected_service.verification_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
                rejected_service.verification_rejection_reason = request.POST.get('verification_rejection_reason')
                rejected_service.save()
                messages.error(request,'service is rejected due to the reason {0}'.format(rejected_service.verification_rejection_reason))
                return render(request,'service_html/service_process_v2.html',{'service':rejected_service})
        
        if request.POST.get('chat'):
            service =Service.objects.get(id=request.POST.get('chat'))
            comments = Comment.objects.filter(service=service.id).order_by('-id')
            return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
        
        if request.POST.get('service_chat_updated'):
            service = Service.objects.get(id=request.POST.get('service_chat_updated'))
            comments = Comment.objects.filter(service=service.id).order_by('-id')
            if not request.FILES.get('service_attachments') and not request.POST.get('service_chat'):
                messages.error(request,'Message or Attachement is missing')
                return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
            else:
                comment = Comment.objects.create(service= service,message=request.POST.get('service_chat'),user=request.user,attachments=request.FILES.get('service_attachments'))
                comment.save()
                return render(request,'chat_html/chat_v2.html',{'service':service,'comments':comments})
        return render(request,'service_html/service_verify_v2.html',{'services':services,'count':count})
    else:
        return render(request,'user_html/404_page.htm')

@login_required(login_url='login')
def accountdashboard(request):
    services = Service.objects.filter(verification_approved=True).order_by('-id')
    if request.POST.get('other'):
        service = Service.objects.get(id=request.POST.get('other'))
        service.save()
        context = {
            'service':service
        }
        return render (request,'service_html/other_details_v2.html',context)
    
    if request.POST.get('other_details'):
        service = Service.objects.get(id=request.POST.get('other_details'))
        service.actual_disbursement = request.POST.get('actual_disbursement')
        service.payout_recieved_percentage = request.POST.get('payout_recieved_percentage')
        service.payout_recieved_date = datetime.datetime.strptime(request.POST.get('payout_recieved_date'),'%Y-%m-%d')
        service.incentives_percentage = request.POST.get('incentives_percentage')
        service.payout_paid = round(float(int(service.actual_disbursement) * int(service.payout))/100,2)
        service.payout_recieved = round(float(service.actual_disbursement) * float(service.payout_recieved_percentage)/100,2)
        service.incentives = round(float(service.actual_disbursement) * float(service.incentives_percentage)/100,2)
        service.net_revenue = round(float(service.payout_recieved) - float(service.payout_paid) + float(service.incentives),2)
        
        service.other_details_updated = True
        service.save()
        context = {
            'service':service
        }
        return redirect('account')
    
    if request.POST.get('completed'):
        service = Service.objects.get(id=request.POST.get('completed'))
        return render (request,'service_html/mic_dashboard_v2.html',{'service':service})
    

    return render(request,'service_html/accounts_v2.html',{'services':services})
@login_required(login_url='login')
def bodashboard(request):
    users = User.objects.filter(profile_update=True,is_verified=False,is_rejected=False,manager__isnull=False).exclude(role__in=[request.user.role,'ADMIN'])
    count = users.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 10)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    if request.user.is_suspended == True:
        return render(request,'user_html/404_page.htm')

    if request.user.role == 'BO' or request.user.role == 'ADMIN' :
        # request.user.is_verified = True
        # request.user.profile_update = True
        # request.user.save()
        users = User.objects.filter(profile_update=True,is_verified=False,is_rejected=False,manager__isnull=False).exclude(role__in=[request.user.role,'ADMIN'])
        if request.method == 'POST':
            if request.POST.get('verify'):
                verified_user =User.objects.get(id=request.POST.get('verify'))
                verified_user.is_verified = True
                verified_user.verified_by = request.user
                verified_user.verified_at = datetime.datetime.utcnow().replace(tzinfo=utc)  
                verified_user.save()
                current_site = get_current_site(request)
                mail_subject_employee = 'Hurray! Your Account is verified successfully'
                mail_subject_manager = 'Your Referred User Account has been Verified '
                print(mail_subject_employee)
                print(mail_subject_manager)
                message_to_employee = render_to_string('email_template/verified_message.htm', {
                    'verified_user': verified_user,
                    'verified_user_role':verified_user.role,
                    'verified_user_manager':verified_user.manager,
                    'verified_at':verified_user.verified_at,
                    'domain': current_site.domain,
                    })

                print(message_to_employee)
                to_email = verified_user.email
                email = EmailMessage(
                            mail_subject_employee, message_to_employee, to=[to_email]
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)
                message_to_manager = render_to_string('email_template/verified_message_to_manager.htm', {
                    'verified_user': verified_user,
                    'verified_user_role':verified_user.role,
                    'verified_user_manager':verified_user.manager,
                    'verified_at':verified_user.verified_at,
                    'domain': current_site.domain,
                    })
                print(message_to_manager)
                to_email = verified_user.manager.email
                email = EmailMessage(
                            mail_subject_manager, message_to_manager, to=[to_email]
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)
                return redirect('bodashboard')
                
            if request.POST.get('reject'):
                form = UserRejectionForm(request.POST)
                rejected_user = User.objects.get(id=request.POST.get('reject'))
                rejected_user.is_rejected = True
                rejected_user.rejected_by = request.user
                rejected_user.rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
                rejected_user.rejection_reason = request.POST.get('rejection_reason')
                rejected_user.profile_update = False
                rejected_user.housing_loan = ''
                rejected_user.professional_occupation = ''
                rejected_user.mortgage_loan = ''
                rejected_user.vehical_loan = ''
                rejected_user.personal_loan = ''
                rejected_user.account_number = ''
                rejected_user.account_name = ''
                rejected_user.ifsc_code = ''
                rejected_user.adhaar_image = ''
                rejected_user.pancard_image = ''
                rejected_user.cancelled_cheque_image = ''
                rejected_user.terms_condition = False
                rejected_user.save()
                current_site = get_current_site(request)
                mail_subject_employee = 'Sorry! Your Profile is Rejected'
                mail_subject_manager = 'Your Referred User Account has been Rejected '
                print(mail_subject_employee)
                print(mail_subject_manager)
                message_to_employee = render_to_string('email_template/reject_message.htm', {
                    'rejected_user': rejected_user,
                    'rejected_user_role': rejected_user.role,
                    'rejection_reason': rejected_user.rejection_reason,
                    'rejected_user_manager':rejected_user.manager,
                    'rejected_at':rejected_user.rejected_at,
                    'domain': current_site.domain,
                    })
                print(message_to_employee)
                to_email = rejected_user.email
                email = EmailMessage(
                            mail_subject_employee, message_to_employee, to=[to_email]
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)
                message_to_manager = render_to_string('email_template/rejection_message_to_manager.htm',{
                    'rejected_user': rejected_user,
                    'rejected_user_role': rejected_user.role,
                    'rejection_reason': rejected_user.rejection_reason,
                    'rejected_user_manager':rejected_user.manager,
                    'rejected_at':rejected_user.rejected_at,
                    'domain': current_site.domain,
                    })
                print(message_to_manager)
                to_email = rejected_user.manager.email
                email = EmailMessage(
                            mail_subject_manager, message_to_manager, to=[to_email]
                )
                email.content_subtype = "html"
                email.send(fail_silently=False)
                return render(request,"user_html/bodashboard_v2.html",{'users':users})
            else:
                return render(request,"user_html/bodashboard_v2.html",{'users':users})
        # 
        if count==0:
            messages.error(request,'No User Found')
            return render(request,"user_html/bodashboard_v2.html",{'users':users,'count':count})  
        else:
            return render(request,"user_html/bodashboard_v2.html",{'users':users,'count':count})        
    
    else:
        return render(request,'user_html/404_page.htm')
    return redirect('bodashboard')

@login_required(login_url='login')
@admin_only
def home(request):
    return render(request,"user_html/home.html")

@login_required(login_url='login')
def profile(request):
    profile = request.user
    
    if request.user.is_suspended == True:
        return render(request,'user_html/404_page.htm')

    if request.method == 'POST': 
        if request.POST.get('first_name'):
            profile.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            profile.last_name = request.POST.get('last_name')
        if request.POST.get('father_name'):
            profile.father_name = request.POST.get('father_name')
        if request.POST.get('professional_occupation'):
            profile.professional_occupation = request.POST.get('professional_occupation')
        if request.POST.get('phone'):
            profile.phone = request.POST.get('phone')
        if request.POST.get('email'):
            profile.email = request.POST.get('email')
        if request.POST.get('account_number'):
            profile.account_number = request.POST.get('account_number')
        if request.POST.get('account_name'):
            profile.account_name = request.POST.get('account_name')
        if request.POST.get('ifsc_code'):
            profile.ifsc_code = request.POST.get('ifsc_code')
        
        if request.FILES.get('gst_proof_image',''):
            profile.gst_proof_image = request.FILES['gst_proof_image']
        else:
            profile.gst_proof_image = ''
        if request.FILES.get('adhaar_image',''):
            profile.adhaar_image = request.FILES['adhaar_image']
        else:
            profile.adhaar_image = ''
        if request.FILES.get('pancard_image',''):
            profile.pancard_image = request.FILES['pancard_image']
        else:
            profile.pancard_image = ''
        if request.FILES.get('pancard_image',''):
            profile.pancard_image = request.FILES['pancard_image']
        else:
            profile.pancard_image = ''
        if request.FILES.get('cancelled_cheque_image',''):
            profile.cancelled_cheque_image = request.FILES['cancelled_cheque_image']
        else:
            profile.cancelled_cheque_image = ''
        profile.profile_update = True
        if profile.is_rejected == True:
            profile.is_rejected = False
        profile.save()
        context = {
            'user':profile,
            
        }
        
        current_site = get_current_site(request)
        mail_subject = 'Your Profile is updated Successfully'
        
        message = render_to_string('email_template/profile_success_message.htm', {
            'profile_update': profile.profile_update,
            'domain': current_site.domain,
            'user':profile
        })
        to_email = profile.email
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)
        context = {
            'user':profile,
           
        }
        return render(request,'user_html/dashboard_v2.html',context)
    else:
        context = {
            'user':profile,
            
        }
        return render (request,'user_html/profile_v2.html',context)

def enquiry(request):
    enquiry = request.user
    if request.user.is_suspended == True:
        return render(request,'user_html/404_page.htm')

    if request.method == 'POST': 
        pass
    else:      
        context = {
                'user':enquiry,
            }
        return render (request,'user_html/enquiry.html',context)

@property
def image_url(self):
    """
    Return self.photo.url if self.photo is not None, 
    'url' exist and has a value, else, return None.
    """
    if self.image:
        return getattr(self.photo, 'url', None)
    return None
    


    

@login_required(login_url='login')
def register(request):
    form = UserAdminCreationForm(request=request) 
    
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')
    
    if request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')
    
    if request.user.is_verified and (request.user.role!='CONNECTOR' and request.user.role!='BO'):
        if request.method == 'POST':
            
            form = UserAdminCreationForm(request.POST,request=request)
            try:
                if form.is_valid():
                    
                    # print(type(request.user.role))
                    user = form.save(commit=False)
                    user.is_active = False
                    user.referral_code = user.first_name[:3] + str(random.randint(1111,9999))
                    print(user.referral_code)  
                    user.referred_by = request.user.referral_code
                    user.manager = request.user
                    letters = string.ascii_uppercase
                    password_genrate=(''.join(random.choice(letters) for i in range(6)) )
                    user.set_password(password_genrate)
                    user.save()
                    # msg = 'https://2factor.in/API/V1/3571de9f-a2a6-11eb-80ea-0200cd936042/SMS/+91{0}/{1}'.format(user.phone,password_genrate
                    import http.client
                    sms = 'Please verify your email first at {0} your password is {1}'.format(user.email,password_genrate)
                    conn = http.client.HTTPSConnection("www.smsgateway.center")
                    payload = "userId=sumit050890&password=A123a123a&senderId=SMSGAT&sendMethod=simpleMsg&msgType=text&mobile={0}&msg={1}SMSGateway.Center&duplicateCheck=true&format=json".format(user.phone,sms)

                    headers = {
                        'apikey': "6826822981205575928",
                        'content-type': "application/x-www-form-urlencoded",
                        'cache-control': "no-cache"
                        }

                    conn.request("POST", "/SMSApi/rest/send", payload, headers)

                    res = conn.getresponse()
                    data = res.read()

                    
                    
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your Matput Account.'
                    
                    
                    message = render_to_string('email_template/register_confirm.htm', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':force_text(urlsafe_base64_encode(force_bytes(user.pk))),
                        'token':account_activation_token.make_token(user),
                        'password':password_genrate,
                    })
                    
                    to_email = request.POST['email']
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    messages.success(request, 'Your Referred User Account is Registered successfully. Check email for further information')
                    return render (request,'user_html/dashboard_v2.html')
                else:
                    messages.error(request,'Some Error Occured')
            except IntegrityError as e:
                messages.error(request, 'ERROR: User already exists!')
        else:
            form = UserAdminCreationForm(request=request)
    
    return render(request,"user_html/register_v2.html",{'form':form})

                
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        # if (self._num_days(self._today()) - ts) > 1: # 1 day = 24 hours
        #     return False
        user.is_active = True
        user.activate_user = True
        user.save()
        login(request)
        # return redirect('home')
        return render(request,'user_html/activation_success.htm')
        # HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        if user is not None and user.is_active:
            return render(request,'user_html/already_activated.html')
        if user is None:
            return render(request,'user_html/activation_failure.htm')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return render(request,'user_html/logout.htm')


def password_reset_request(request):
    if request.method == "POST":
        domain = request.headers['Host']
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            # You can use more than one way like this for resetting the password.
            # ...filter(Q(email=data) | Q(username=data))
            # but with this you may need to change the password_reset form as well.
            if associated_users.exists():
                for user in associated_users:
                    try:
                        mail_subject = "Password Reset Requested"
                        email_template_name = "email_template/password_reset_email.html"
                        c = {
                            "email": user.email,
                            'domain': domain,
                            'site_name': 'Interface',
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "user": user,
                            'token': default_token_generator.make_token(user),
                            'protocol': 'http',
                        }
                        to_email = request.POST['email']
                        message = render_to_string(email_template_name, c)
                        email = EmailMessage(
                                    mail_subject, message, to=[to_email]
                        )
                        email.content_subtype = "html"
                        email.send(fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="email_template/password_reset.htm",
                  context={"form": password_reset_form})






