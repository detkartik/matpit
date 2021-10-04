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
from .models import CustomUser,Category, LoginBank, Comment,BalanceTransferBank,TransferBank,TopupReason,RelationshipApplicant,BusinessProof,Business,CoApllicantAddressProof,CompanyType,AddressProof,Khata,SalaryAccountBank,City,Notification
import random
import string
import copy
import datetime
from django.utils.timezone import utc
from django.db import IntegrityError
from .models import Lead
from django.conf import settings
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML,CSS
from weasyprint.fonts import FontConfiguration
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

# from djangopwa import version

# import logging
# import random
# import time
# from django.http import Http404
# from django.shortcuts import render
# from django.templatetags.static import static
# from django.urls import reverse
# from django.utils import timezone
# from django.views.decorators.cache import never_cache



# logger = logging.getLogger('djpwa.pwa.views')


# def offline(request):
#     return render(request, 'pwa/offline.html')


# def my_page(request):
#     routes = {
#         'Home': reverse('home'),
#         'Say hi': reverse('say_something', kwargs={'key': 'hi'}),
#         'Say bye': reverse('say_something', kwargs={'key': 'bye'}),
#         'Say something invalid': reverse('say_something', kwargs={'key': 'invalid'}),
#         'Response in random time': reverse('random_response'),
#         'Fill dynamic cache': reverse('fill_dynamic_cache', kwargs={'id': 1}),
#         'Must not cache': reverse('must_not_cache'),
#     }

#     return render(request, 'pwa/my_page.html', context={'routes': routes})


# def say_something(request, key):
#     things_to_say = {
#         'hi': 'Hello world',
#         'bye': 'Have a nice day',
#     }

#     if key not in things_to_say:
#         raise Http404(f'{key} is not a valid thing to say')

#     return render(request, 'pwa/say_something.html', context={'thing': things_to_say[key]})


# def random_response(request):
#     response_time_ms = random.choice((0, 10, 50, 100, 1_000, 10_000))
#     response_time = response_time_ms / 1_000
#     print(f'Selected response time {response_time}')
#     time.sleep(response_time)
#     return render(request, 'pwa/random_response.html', context={'response_time': response_time})


# def fill_dynamic_cache(request, id):
#     return render(request, 'pwa/fill_dynamic_cache.html', context={'id': id})


# @never_cache
# def must_not_cache(request):
#     return render(request, 'pwa/must_not_cache.html', context={'requested_at': timezone.now()})


# class ServiceWorkerView(TemplateView):
#     template_name = 'sw.js'
#     content_type = 'application/javascript'
#     name = 'sw.js'

#     def get_context_data(self, **kwargs):
#         return {
#             'version': version,
#             'icon_url': static('icons/aurss.512x512.png'),
#             'manifest_url': static('manifest.json'),
#             'style_url': static('style.css'),
#             'home_url': reverse('home'),
#             'offline_url': reverse('offline'),
#         }




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
                        return render(request,'lead_html/lead_verify_v2.html')

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
    leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager=ruser) | Q(created_by__manager__referred_by=ruser.referral_code),verification_approved=True,other_details_updated=True)
    context = {
        'leads':leads,
        'count':leads.count
        
        }
    return render (request,'lead_html/mic_dashboard_v2.html',context)

@login_required(login_url='login')
def commercial_vehicle_loans(request):
    return render (request,'lead_html/commercial_vehicle_loans_v2.html')

@login_required(login_url='login')
def car_loans(request):
    return render (request,'lead_html/car_loans_v2.html')

@login_required(login_url='login')
def personal_loans(request):
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT' :
        return render(request,'user_html/404_page.htm')
    cities = City.objects.all()
    salary_account_banks = SalaryAccountBank.objects.all()
    

    ################################### Personal Loan Details ############################################
    if request.method == 'POST':
        
        personal_loan_phone = request.POST.get('personal_loan_phone')
        personal_loan_required_loan_amount = request.POST.get('personal_loan_required_loan_amount')
        personal_loan_take_home_salary = request.POST.get('personal_loan_take_home_salary')
        personal_loan_living_city = request.POST.get('personal_loan_living_city')
        personal_loan_salary_account_bank = request.POST.get('personal_loan_salary_account_bank')
        personal_loan_first_name = request.POST.get('personal_loan_first_name')
        personal_loan_last_name = request.POST.get('personal_loan_last_name')
        personal_loan_residence_pin_code = request.POST.get('personal_loan_pin_code')
        personal_loan_email = request.POST.get('personal_loan_email')
        personal_loan_existing_emi = request.POST.get('personal_loan_existing_emi')
        oneyear_experience = request.POST.get('oneyear_experience')
        if oneyear_experience == "on":
            oneyear_experience = True
        else:
            oneyear_experience = False

    ################################  Image Upload ############################################################
        if request.FILES.get('personal_loan_pancard',''):
            personal_loan_pancard_image = request.FILES['personal_loan_pancard']
        else:
            personal_loan_pancard_image = ''
        if request.FILES.get('personal_loan_adhaarcard',''):
            personal_loan_adhaar_image = request.FILES['personal_loan_adhaarcard']
        else:
            personal_loan_adhaar_image = ''
        if request.FILES.get('personal_loan_current_address_proof',''):
            personal_loan_current_address_proof_image = request.FILES['personal_loan_current_address_proof']
        else:
            personal_loan_current_address_proof_image = ''
        if request.FILES.get('personal_loan_bank_statement',''):
            personal_loan_bank_statement = request.FILES['personal_loan_bank_statement']
        else:
            personal_loan_bank_statement = ''
        if request.FILES.get('personal_loan_payslip',''):
            personal_loan_payslip = request.FILES['personal_loan_payslip']
        else:
            personal_loan_payslip = ''
        if request.FILES.get('personal_loan_form16_image',''):
            personal_loan_form16_image = request.FILES['personal_loan_form16_image']
        else:
            personal_loan_form16_image = ''
        if request.FILES.get('personal_loan_stamp_size_photo',''):
            personal_loan_stamp_size_image = request.FILES['personal_loan_stamp_size_photo']
        else:
            personal_loan_stamp_size_image = ''
        
        if oneyear_experience == True and request.FILES.get('personal_loan_job_offer_letter',''): 
            personal_loan_job_offer_letter_image = request.FILES['personal_loan_job_offer_letter']
        else:
            personal_loan_job_offer_letter_image = ''


        lead = Lead.objects.create(
            personal_loan_phone = personal_loan_phone,
            personal_loan_required_loan_amount = personal_loan_required_loan_amount,
            personal_loan_monthly_take_home_salary = personal_loan_take_home_salary,
            personal_loan_living_city = personal_loan_living_city,
            personal_loan_salary_account_bank = personal_loan_salary_account_bank,
            personal_loan_first_name = personal_loan_first_name,
            personal_loan_last_name = personal_loan_last_name,
            personal_loan_residence_pin_code = personal_loan_residence_pin_code,
            personal_loan_email = personal_loan_email,
            personal_loan_existing_emi = personal_loan_existing_emi,
            personal_loan_pancard_image = personal_loan_pancard_image,
            personal_loan_adhaar_image = personal_loan_adhaar_image,
            personal_loan_current_address_proof_image = personal_loan_current_address_proof_image,
            personal_loan_bank_statement_image = personal_loan_bank_statement,
            personal_loan_payslip_image = personal_loan_payslip,
            personal_loan_form16_image = personal_loan_form16_image,
            personal_loan_stamp_size_image = personal_loan_stamp_size_image,
            personal_loan_job_offer_letter_image = personal_loan_job_offer_letter_image,
            created_by = request.user,
            lead_update = True
        )
        try:
            lead.save()
        except:
            print('error')
        list_managers_id =  [
        request.user.manager.id,
        request.user.manager.manager.id,
        request.user.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.id,
        request.user.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.manager.id,
        ]
        notification_manager_list =  list(set(list_managers_id))
    
        
        print(lead.id)  

        for i in notification_manager_list:
            notification =  Notification.objects.create(
                lead = lead,
                notified_user = i,
                read_lead_notification = True,
                read_chat_notification = False
                
            )
            notification.save()
            print(notification)
            

        print(lead.personal_loan_phone)
        print(lead.personal_loan_first_name)
        print(lead.personal_loan_required_loan_amount)
        return redirect('yourlead')
    return render (request,'lead_html/personal_loans_v2.html',{'cities':cities,'salary_account_banks':salary_account_banks})

@login_required(login_url='login')
def credit_cards(request):
    return render (request,'lead_html/credit_cards_v2.html')

@login_required(login_url='login')
def hl_lap(request):
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT' :
        return render(request,'user_html/404_page.htm')
        
    balance_transfer_banks = BalanceTransferBank.objects.all()
    transfer_banks = TransferBank.objects.all()
    business_proofs = BusinessProof.objects.all()
    relationship_applicats = RelationshipApplicant.objects.all()
    topup_reasons =  TopupReason.objects.all()
    address_proofs = AddressProof.objects.all()
    co_applicant_address_proofs = CoApllicantAddressProof.objects.all()
    company_types = CompanyType.objects.all()
    businesses = Business.objects.all()
    khatas = Khata.objects.all()    


    

    print("fadadasdads")
    if request.method == "POST":
        
        print("kartikey")
        loan_type = request.POST.get('loan_type')
        if loan_type == 'fresh_loan':
            loan_type = 'FL'
        if loan_type == 'balance':
            loan_type = 'BT'
        
        ############# FRESH LOAN ###########################
        fresh_loan_type = request.POST.get('fresh_loan_type')
        if fresh_loan_type == 'construction':
            fresh_loan_type = 'SC'
        if fresh_loan_type == 'purchase':
            fresh_loan_type = 'P'
        if fresh_loan_type == 'lap':
            fresh_loan_type = 'LAP'      
         
        required_loan_amount = request.POST.get('required_loan_amount')
       
        purchase_type = request.POST.get('purchase_type')
        if purchase_type == 'plot':
            purchase_type = 'Pl'
        if purchase_type == 'ih':
            purchase_type = 'IH'
        if purchase_type == 'flat':
            purchase_type = 'F' 
        
        
        ############## Balance Transfer ####################

        balance_transfer_type = request.POST.get('balance_transfer')
        if balance_transfer_type == 'house_loan':
            balance_transfer_type = 'HL'
        if balance_transfer_type == 'h_lap':
            balance_transfer_type = 'HLAP'
        if balance_transfer_type == 'plot_loan':
            balance_transfer_type = 'PLOAN'
        
       
        ############# Balance Transfer Bank #############################

        balance_transfer_bank = request.POST.get('balance_transfer_bank')


        loan_amount1 = request.POST.get('loan1')
        transfer_bank1 = request.POST.get('transfer_bank1')

        loan_amount2 = request.POST.get('loan2')
        transfer_bank2 = request.POST.get('transfer_bank2')
        
        loan_amount3 = request.POST.get('loan3')
        transfer_bank3 = request.POST.get('transfer_bank3')
      
        loan_amount4 = request.POST.get('loan4')
        transfer_bank4 = request.POST.get('transfer_bank4')
        
        loan_amount5 = request.POST.get('loan5')
        transfer_bank5 = request.POST.get('transfer_bank5')
        
        
        apply_topup = request.POST.get('apply_topup')

        if apply_topup == "on":
            apply_topup = True
            
        else:
            apply_topup = False
            

        required_topup = request.POST.get('required_topup')
    
        reason_for_topup = request.POST.get('reason_for_topup')
        

        reason_for_topup_other = request.POST.get('other_reason_topup') 

        ######################### KYC ##################################
        
        applicant = request.POST.get('kyc_select_applicant')

        if applicant == 'Individual':
            applicant = 'Individual'
        if applicant == 'NRI':
            applicant = 'NRI'
        if applicant == 'COMPANY':
            applicant = 'COMPANY'


        ############### KYC Individual/NRI ######################
        applicant_first_name = request.POST.get('applicant_first_name')
        applicant_last_name = request.POST.get('applicant_last_name')
        applicant_official_email = request.POST.get('applicant_official_email')
        applicant_personal_email = request.POST.get('applicant_personal_email')
        applicant_phone = request.POST.get('applicant_phone')
        applicant_current_address_proof = request.POST.get('applicant_current_address_proof')
    
        company_name = request.POST.get('company_name')
        point_of_contact_name = request.POST.get('poc_name')
        point_of_contact_phone = request.POST.get('poc_phone')
        company_type = request.POST.get('company_type')

        nature_of_business = request.POST.get('nature_of_business')
        business_proof = request.POST.get('kyc_business_proof')
        
        ################## CO APPLICANTS ########################################
        is_co_applicant = request.POST.get('co_applicant_yes')
        if is_co_applicant == "on":
            is_co_applicant = True
        else:
            is_co_applicant = False
        relationship_co_applicant = request.POST.get('kyc_select_co_applicant_relation')
        
        co_applicant = request.POST.get('kyc_select_co_applicant')
        if co_applicant == 'Individual':
            co_applicant = 'Individual'
        if co_applicant == 'NRI':
            co_applicant = 'NRI'
        if co_applicant == 'COMPANY':
            co_applicant = 'COMPANY'
        
        co_applicant_first_name = request.POST.get('co_applicant_first_name')
        co_applicant_last_name = request.POST.get('co_applicant_last_name')
        co_applicant_official_email = request.POST.get('co_applicant_official_email')
        co_applicant_personal_email = request.POST.get('co_applicant_personal_email')
        co_applicant_phone = request.POST.get('co_applicant_phone')

        co_applicant_current_address_proof = request.POST.get('co_applicant_kyc_address_proof')
        co_applicant_company_name = request.POST.get('co_applicant_company_name')
        co_applicant_point_of_contact_name = request.POST.get('co_applicant_poc_name')
        co_applicant_point_of_contact_phone = request.POST.get('co_applicant_poc_phone')
        co_applicant_company_type = request.POST.get('co_applicant_company_type')
        co_applicant_nature_of_business = request.POST.get('co_applicant_nature_of_business')
        co_applicant_business_proof = request.POST.get('kyc_co_applicant_business_proof')
 
         ############## Images ############################
        if request.FILES.get('applicant_adhaar_image',''):
            applicant_adhaar_image = request.FILES.get('applicant_adhaar_image','')
            print('applicant_adhaar_image',applicant_adhaar_image)
        else:
            applicant_adhaar_image = ''
            # applicant_adhaar_image.save()
        if request.FILES.get('applicant_pancard_image',''):
            applicant_pancard_image = request.FILES.get('applicant_pancard_image','')
            print('applicant_pancard_image',applicant_pancard_image) 
        else:
            applicant_pancard_image = ''
            # applicant_pancard_image.save()
        if request.FILES.get('kyc_address_proof_image',''):
            applicant_current_address_proof_image = request.FILES.get('kyc_address_proof_image','')
            print('applicant_current_address_proof_image',applicant_current_address_proof_image)
        else:
            applicant_current_address_proof_image = ''
            # applicant_current_address_proof_image.save()
        if request.FILES.get('co_applicant_adhaar_image',''):
            co_applicant_adhaar_image = request.FILES.get('co_applicant_adhaar_image','')
            print('co_applicant_adhaar_image',co_applicant_adhaar_image)
        else:
            co_applicant_adhaar_image = ''
            # co_applicant_adhaar_image.save()
        if request.FILES.get('co_applicant_pancard_image',''):
            co_applicant_pancard_image = request.FILES.get('co_applicant_pancard_image','')
            print('co_applicant_pancard_image',co_applicant_pancard_image)
        else:
            co_applicant_pancard_image = ''
            # co_applicant_pancard_image.save()
        if request.FILES.get('co_applicant_kyc_address_proof_image',''):
            co_applicant_address_proof_image = request.FILES.get('co_applicant_kyc_address_proof_image','')
            print('co_applicant_address_proof_image',co_applicant_address_proof_image)
        else:
            co_applicant_address_proof_image = ''
            # co_applicant_address_proof_image.save()
        
        if request.FILES.get('business_proof_image',''):
            business_proof_image = request.FILES.get('business_proof_image','')
            print('business_proof_image',business_proof_image)
        else:
            business_proof_image = ''
            # business_proof_image.save()

        if request.FILES.get('co_applicant_business_proof_image',''):
            co_applicant_business_proof_image = request.FILES.get('co_applicant_business_proof_image','')
            print('co_applicant_business_proof_image',co_applicant_business_proof_image)
        else:
            co_applicant_business_proof_image = ''
            # co_applicant_business_proof_image.save()
        if request.FILES.get('co_applicant_company_pancard_image'):
            co_applicant_company_pancard_image = request.FILES.get('co_applicant_company_pancard_image')
            print('co_applicant_company_pancard_image',co_applicant_company_pancard_image)
        else:
            co_applicant_company_pancard_image = ''
        if request.FILES.get('company_pancard_image'):
            company_pancard_image = request.FILES.get('company_pancard_image')
            print('company_pancard_image',company_pancard_image)
        else:
            company_pancard_image = ''


        # else:
        #     applicant_adhaar_image = ''
        #     applicant_pancard_image = ''
        #     applicant_current_address_proof_image = ''
        #     business_proof_image = ''
        #     co_applicant_adhaar_image = ''
        #     co_applicant_pancard_image = ''
        #     co_applicant_address_proof_image = ''
        #     co_applicant_business_proof_image = ''
        #     co_applicant_business_proof_image = ''
        
        print('applicant_adhaar_image',applicant_adhaar_image)
        print('applicant_pancard_image',applicant_pancard_image) 
        print('applicant_current_address_proof_image',applicant_current_address_proof_image)
        print('co_applicant_address_proof_image',co_applicant_address_proof_image)
        print('co_applicant_company_pancard_image',co_applicant_company_pancard_image)
        print('company_pancard_image',company_pancard_image)

        lead = Lead.objects.create(
            loan_type=loan_type,
            purchase_type=purchase_type,
            fresh_loan_type=fresh_loan_type,
            balance_transfer_type=balance_transfer_type,
            required_loan_amount=required_loan_amount,
            balance_transfer_bank =balance_transfer_bank, 
            loan_amount1=loan_amount1,
            transfer_bank1=transfer_bank1,
            loan_amount2=loan_amount2,
            transfer_bank2=transfer_bank2,
            loan_amount3=loan_amount3,
            transfer_bank3=transfer_bank3,
            loan_amount4=loan_amount4,
            transfer_bank4=transfer_bank4,
            loan_amount5=loan_amount5,
            transfer_bank5=transfer_bank5,
            apply_topup=apply_topup, 
            required_topup=required_topup,
            reason_for_topup=reason_for_topup,
            reason_for_topup_other=reason_for_topup_other,
            applicant = applicant,
            applicant_first_name=applicant_first_name,
            applicant_last_name=applicant_last_name,
            applicant_official_email=applicant_official_email,
            applicant_personal_email=applicant_personal_email,
            applicant_phone=applicant_phone,
            applicant_current_address_proof=applicant_current_address_proof,
            company_name=company_name,
            point_of_contact_name=point_of_contact_name,
            point_of_contact_phone=point_of_contact_phone,
            company_type=company_type,
            nature_of_business=nature_of_business,
            business_proof=business_proof,
            is_co_applicant=is_co_applicant,
            relationship_co_applicant=relationship_co_applicant,
            co_applicant=co_applicant,
            co_applicant_first_name=co_applicant_first_name,
            co_applicant_last_name=co_applicant_last_name,
            co_applicant_official_email=co_applicant_official_email,
            co_applicant_personal_email=co_applicant_personal_email,
            co_applicant_phone=co_applicant_phone,
            co_applicant_current_address_proof=co_applicant_current_address_proof,
            co_applicant_company_name=co_applicant_company_name,
            co_applicant_point_of_contact_name=co_applicant_point_of_contact_name,
            co_applicant_point_of_contact_phone=co_applicant_point_of_contact_phone,
            co_applicant_company_type=co_applicant_company_type,
            co_applicant_nature_of_business=co_applicant_nature_of_business,
            co_applicant_business_proof=co_applicant_business_proof,
            applicant_adhaar_image  = applicant_adhaar_image, 
            applicant_pancard_image  = applicant_pancard_image, 
            applicant_current_address_proof_image  = applicant_current_address_proof_image, 
            business_proof_image  = business_proof_image, 
            co_applicant_adhaar_image  = co_applicant_adhaar_image, 
            co_applicant_pancard_image  = co_applicant_pancard_image, 
            co_applicant_address_proof_image  = co_applicant_address_proof_image, 
            co_applicant_business_proof_image  = co_applicant_business_proof_image,
            co_applicant_company_pancard_image = co_applicant_company_pancard_image,
            company_pancard_image = company_pancard_image,
            created_by = request.user
            
        )   
        lead.save()

        
        print(lead)
        
        
        # lead.save()
        
        # print('applicant_adhaar_image',lead.applicant_adhaar_image)
        # print('applicant_pancard_image',lead.applicant_pancard_image) 
        # print('applicant_current_address_proof_image',lead.applicant_current_address_proof_image)
        # print('co_applicant_address_proof_image',lead.co_applicant_address_proof_image)
        
        
       
        return redirect('incomplete_lead')
    
    context = {
        'balance_transfer_banks':balance_transfer_banks,
        'transfer_banks':transfer_banks,
        'business_proofs':business_proofs,
        'relationship_applicats':relationship_applicats,
        'topup_reasons':topup_reasons,
        'address_proofs':address_proofs,
        'co_applicant_address_proofs':co_applicant_address_proofs,
        'company_types':company_types,
        'businesses':businesses
    }
    return render (request,'lead_html/hl_lap_v2.html',context)
        
@login_required(login_url='login')
def incomplete_lead(request):
    ruser = request.user
    leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)|Q(created_by__manager=ruser) |Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code),lead_update=False).order_by('-id')
    count = leads.count()
    balance_transfer_banks = BalanceTransferBank.objects.all()
    transfer_banks = TransferBank.objects.all()
    business_proofs = BusinessProof.objects.all()
    relationship_applicats = RelationshipApplicant.objects.all()
    topup_reasons =  TopupReason.objects.all()
    address_proofs = AddressProof.objects.all()
    co_applicant_address_proofs = CoApllicantAddressProof.objects.all()
    company_types = CompanyType.objects.all()
    businesses = Business.objects.all()
    khatas = Khata.objects.all()
    context = {
        'leads':leads,
        'balance_transfer_banks':balance_transfer_banks,
        'transfer_banks':transfer_banks,
        'business_proofs':business_proofs,
        'relationship_applicats':relationship_applicats,
        'topup_reasons':topup_reasons,
        'address_proofs':address_proofs,
        'co_applicant_address_proofs':co_applicant_address_proofs,
        'company_types':company_types,
        'businesses':businesses,
        'khatas':khatas,
        'count':count

    }
    if request.POST.get('proceed'):
        lead = Lead.objects.get(id=request.POST.get('proceed'))
        ctx = {
        'balance_transfer_banks':balance_transfer_banks,
        'transfer_banks':transfer_banks,
        'business_proofs':business_proofs,
        'relationship_applicats':relationship_applicats,
        'topup_reasons':topup_reasons,
        'address_proofs':address_proofs,
        'co_applicant_address_proofs':co_applicant_address_proofs,
        'company_types':company_types,
        'businesses':businesses,
        'khatas':khatas,
        'lead':lead
        }
        
        if lead.is_finance_completed == False:
            return render(request,'lead_html/lead_finance_process_v2.html',ctx)
        
        if lead.is_finance_completed == True and lead.is_property_details_process_completed == False:
            return render(request,'lead_html/lead_property_process_v2.html',ctx)

        if lead.is_property_details_process_completed == True:
            return render(request,'lead_html/lead_technical_process_v2.html',ctx)
        
        if lead.is_technical_details_process_completed == True:
            return redirect('yourlead')
        
        if lead.lead_update == True:
            return redirect('yourlead')

    
    ############################################### Finance Details Process ################################################################
    
    if request.POST.get('finance_completed'):
        lead = Lead.objects.get(id=request.POST.get('finance_completed'))
        lead.applicant_job_type = request.POST.get('applicant_job_type')  
        ################### Applicant - Job Type : Salaried ######################  
           
        lead.applicant_job_location = request.POST.get('applicant_job_location')
        lead.applicant_take_home_salary = request.POST.get('applicant_take_home_salary')
        lead.applicant_how_much_in_cash_job = request.POST.get('applicant_how_much_in_cash_job')
        lead.applicant_how_much_in_account_job = request.POST.get('applicant_how_much_in_account_job')
        lead.applicant_duration_in_present_company = request.POST.get('applicant_duration_in_present_company')
        if lead.applicant_duration_in_present_company == 'lessthantwoyears':
            lead.applicant_duration_in_present_company = 'l2'
        if lead.applicant_duration_in_present_company == 'morethantwoyears':
            lead.applicant_duration_in_present_company = 'm2'
        lead.applicant_company_name = request.POST.get('applicant_company_name')

        ################## Applicant - Job Type : Self Employeed #####################
        lead.applicant_business_location = request.POST.get('applicant_business_location')
        
        lead.applicant_how_much_in_cash_bus = request.POST.get('applicant_how_much_in_cash_bus')
        lead.applicant_how_much_in_account_bus = request.POST.get('applicant_how_much_in_account_bus')
        
        lead.applicant_how_much_itr = request.POST.get('applicant_how_much_itr')
        lead.applicant_business_vintage = request.POST.get('applicant_business_vintage')
        lead.applicant_nature_business = request.POST.get('applicant_nature_business')
        
        lead.applicant_business_proof_inr = request.POST.get('applicant_business_proof_inr')

        ##################### Applicant - Job Type : Company ################################
        lead.applicant_company_business_location = request.POST.get('applicant_company_business_location')
        
        
        lead.applicant_company_how_much_itr = request.POST.get('applicant_company_how_much_itr')
        lead.applicant_no_of_years_business = request.POST.get('applicant_no_of_years_business')
        lead.applicant_company_nature_business = request.POST.get('applicant_company_nature_business')
        
        
        lead.co_applicant_job_type = request.POST.get('co_applicant_job_type')  
        ############## CO Applicant - Job Type : Salaried ######################       
        lead.co_applicant_job_location = request.POST.get('co_applicant_job_location')
        lead.co_applicant_take_home_salary = request.POST.get('co_applicant_take_home_salary')
        
        lead.co_applicant_how_much_in_cash_job = request.POST.get('co_applicant_how_much_in_cash_job')
        lead.co_applicant_how_much_in_account_job = request.POST.get('co_applicant_how_much_in_account_job')
        lead.co_applicant_duration_in_present_company = request.POST.get('co_applicant_duration_in_present_company')
        if lead.co_applicant_duration_in_present_company == 'lessthantwoyears':
            lead.co_applicant_duration_in_present_company = 'l2'
        if lead.co_applicant_duration_in_present_company == 'morethantwoyears':
            lead.co_applicant_duration_in_present_company = 'm2'
        lead.co_applicant_company_name = request.POST.get('co_applicant_company_name')

        ################## CO Applicant  - Job Type : Self Employeed #####################
        lead.co_applicant_business_location = request.POST.get('co_applicant_business_location')
        
        lead.co_applicant_how_much_in_cash_bus = request.POST.get('co_applicant_how_much_in_cash_bus')
        lead.co_applicant_how_much_in_account_bus = request.POST.get('co_applicant_how_much_in_account_bus')
        
        lead.co_applicant_how_much_itr = request.POST.get('co_applicant_how_much_itr')
        lead.co_applicant_business_vintage = request.POST.get('co_applicant_business_vintage')
        lead.co_applicant_nature_business = request.POST.get('co_applicant_nature_business')
        
        lead.co_applicant_business_proof_inr = request.POST.get('co_applicant_business_proof_inr')

        ##################### CO Applicant  - Job Type : Company ################################
        lead.co_applicant_company_business_location = request.POST.get('co_applicant_company_business_location')
        lead.co_applicant_company_how_much_itr = request.POST.get('co_applicant_company_how_much_itr')
        lead.co_applicant_no_of_years_business = request.POST.get('co_applicant_no_of_years_business')
        lead.co_applicant_company_nature_business = request.POST.get('co_applicant_company_nature_business')

        lead.is_finance_completed = True
        lead.save()
        lead.applicant_rental_income_job = request.POST.get('applicant_rental_income_job')
        if lead.applicant_rental_income_job == "on":
            lead.applicant_rental_income_job = True
        else:
            lead.applicant_rental_income_job = False

        applicant_rental_income_bus = request.POST.get('applicant_rental_income_bus')
        if applicant_rental_income_bus == "on":
            lead.applicant_rental_income_bus = True
        else:
            lead.applicant_rental_income_bus = False

        applicant_declared_itr = request.POST.get('applicant_declared_itr')
        if applicant_declared_itr == "on":
            lead.applicant_declared_itr = True
        else:
            lead.applicant_declared_itr = False

        applicant_gst_registered = request.POST.get('applicant_gst_registered')
        if applicant_gst_registered == "on":
            lead.applicant_gst_registered = True
        else:
            lead.applicant_gst_registered = False

        applicant_company_declared_itr = request.POST.get('applicant_company_declared_itr')
        if applicant_company_declared_itr == "on":
            lead.applicant_company_declared_itr = True
        else:
            lead.applicant_company_declared_itr = False

        applicant_company_gst_registered = request.POST.get('applicant_company_gst_registered')
        if applicant_company_gst_registered == "on":
            lead.applicant_company_gst_registered = True
        else:
            lead.applicant_company_gst_registered = False

        applicant_audit_report_company = request.POST.get('applicant_audit_report_company')
        if applicant_audit_report_company == "on":
            lead.applicant_audit_report_company = True
        else:
            lead.applicant_audit_report_company = False

        co_applicant_rental_income_job = request.POST.get('co_applicant_rental_income_job')
        if co_applicant_rental_income_job == "on":
            lead.co_applicant_rental_income_job = True
        else:
            lead.co_applicant_rental_income_job = False

        co_applicant_rental_income_bus = request.POST.get('co_applicant_rental_income_bus')
        if co_applicant_rental_income_bus == "on":
            lead.co_applicant_rental_income_bus = True
        else:
            lead.co_applicant_rental_income_bus = False

        co_applicant_declared_itr = request.POST.get('co_applicant_declared_itr')
        if co_applicant_declared_itr == "on":
            lead.co_applicant_declared_itr = True
        else:
            lead.co_applicant_declared_itr = False

        co_applicant_gst_registered = request.POST.get('co_applicant_gst_registered')
        if co_applicant_gst_registered == "on":
            lead.co_applicant_gst_registered = True
        else:
            lead.co_applicant_gst_registered = False

        co_applicant_company_declared_itr = request.POST.get('co_applicant_company_declared_itr')
        if co_applicant_company_declared_itr == "on":
            lead.co_applicant_company_declared_itr = True
        else:
            lead.co_applicant_company_declared_itr = False

        co_applicant_company_gst_registered = request.POST.get('co_applicant_company_gst_registered')
        if  co_applicant_company_gst_registered =="on":
            lead.co_applicant_company_gst_registered = True
        else:
            lead.co_applicant_company_gst_registered = False

        co_applicant_audit_report_company = request.POST.get('co_applicant_audit_report_company')
        if co_applicant_audit_report_company =="on":
            lead.co_applicant_audit_report_company = True
        else:
            lead.co_applicant_audit_report_company = False
        
        lead.save()
        
        return redirect('incomplete_lead')

     
    #####################################################  Property Details Process ######################################################################

    if request.POST.get('property_process_completed'):
        lead = Lead.objects.get(id=request.POST.get('property_process_completed'))
        if request.POST.get('khata'):
            lead.khata = request.POST.get('khata')
        lead.property_location = request.POST.get('property_location')
        lead.is_property_details_process_completed = True
        lead.save()
        return redirect('incomplete_lead')
    

    ########################################################### Technical Details Process #################################################################
    if request.POST.get('technical_process_completed'):
        
        lead = Lead.objects.get(id=request.POST.get('technical_process_completed'))
        lead.plan_type = request.POST.get('plan_type')
        if lead.plan_type == 'govt':
            lead.plan_type = 'ABG'
        else:
            lead.plan_type = 'Normal'
        lead.plan_available_sc =  request.POST.get('plan_available_sc')
        if lead.plan_available_sc == "on":
            lead.plan_available_sc = True
        else:
            lead.plan_available_sc = False

        lead.area_of_extent_sc = request.POST.get('area_of_extent_sc')        
        lead.purchase_type = request.POST.get('purchase_type')
        if lead.purchase_type == 'plot':
            lead.purchase_type = 'Pl'

        lead.area_of_extent_plot = request.POST.get('area_of_extent_plot')        
        if lead.purchase_type == 'ih':
            lead.purchase_type = 'IH'

        lead.number_of_unites = request.POST.get('number_of_unites')
        lead.number_of_floors = request.POST.get('number_of_floors')
        lead.area_of_extent_ih = request.POST.get('area_of_extent_ih')

        lead.building_age_ih = request.POST.get('building_age_ih')
        if lead.building_age_ih == 'lessthantenyearsih':
            lead.building_age_ih = 'l10_ih'
        if lead.building_age_ih == 'morethantenyearsih':
            lead.building_age_ih = 'm10_ih'

        lead.plan_available_ih = request.POST.get('plan_available_ih')
        if lead.plan_available_ih == "on":
            lead.plan_available_ih = True
        else:
            lead.plan_available_ih = False

        lead.purchase_type = request.POST.get('purchase_type')
        if lead.purchase_type == 'flat':
            lead.purchase_type = 'F'

        lead.project_name = request.POST.get('project_name')
        lead.oc_cc_received = request.POST.get('oc_cc_received')
        lead.area_of_extent_flat = request.POST.get('area_of_extent_flat')
        lead.number_of_units_lap = request.POST.get('number_of_units_lap')
        lead.number_of_floors_lap = request.POST.get('number_of_floors_lap')
        lead.area_of_extent_lap = request.POST.get('area_of_extent_lap')

        lead.building_age_lap = request.POST.get('building_age_lap')
        if lead.building_age_lap == 'lessthantenyears':
            lead.building_age_lap = 'l10_lap'
        if lead.building_age_lap == 'morethantenyears':
            lead.building_age_lap = 'm10_lap'

        lead.plan_available_lap = request.POST.get('plan_available_lap')
        if lead.plan_available_lap == "on":
            lead.plan_available_lap = True
        else:
            lead.plan_available_lap = False    

        lead.is_technical_details_process_completed = True
        lead.lead_update = True
        lead.save()
        return redirect('yourlead')
    
    return render(request,'lead_html/incomplete_lead_v2.html',context)






@login_required(login_url='login')
def yourlead(request):
    ruser = request.user
    print(request)
    leads = Lead.objects.filter(Q(created_by=ruser)|Q(created_by__manager=ruser) |Q(created_by__manager__referred_by=ruser.referral_code)|Q(loan_type='PL'),lead_update=True).order_by('-id')
    

    count = leads.count
    banks = LoginBank.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(leads, 10)
    try:
        leads = paginator.page(page)
    except PageNotAnInteger:
        leads = paginator.page(1)
    except EmptyPage:
        leads = paginator.page(paginator.num_pages)

    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')

    # if ruser.role in ['CONNECTOR','AF']:
    #     return render(request,'lead_html/your_leads_v2.html')

    
    if request.POST.get('proceed'):
        lead = Lead.objects.get(id=request.POST.get('proceed'))
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead,'banks':banks})


    if request.POST.get('customer_contact_update'):
        lead = Lead.objects.get(id=request.POST.get('customer_contact_update'))
        lead.customer_contact_updated = True
        lead.customer_contacted = request.POST.get('customer_contacted')
        print('ABCD',lead.customer_contacted)
        if lead.customer_contacted == "on":
            lead.customer_contacted = True
            lead.customer_contacted_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            lead.customer_contacted = False
            lead.customer_contacted_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('customer_contact_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('customer_contact_updated_success'))
        lead.customer_contact_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('file_picked_updated'):
        lead = Lead.objects.get(id=request.POST.get('file_picked_updated'))
        lead.file_picked_updated = True 
        lead.file_picked = request.POST.get('file_picked')
        print('ABCD',lead.file_picked)
        if lead.file_picked == "on":
            lead.file_picked = True
            lead.file_picked_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            lead.file_picked = False
            lead.file_picked_time = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('file_picked_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('file_picked_updated_success'))
        lead.file_picked_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('remark_message_updated'):
        lead = Lead.objects.get(id=request.POST.get('remark_message_updated'))
        lead.remark_message_updated = True
        lead.remark_message = request.POST.get('remark_message')
        lead.remark_message_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('remark_message_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('remark_message_updated_success'))
        lead.remark_message_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('file_pickup_process_completed'):
        lead = Lead.objects.get(id=request.POST.get('file_pickup_process_completed'))
        lead.file_pickup_process_completed = True
        lead.file_pickup_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead,'banks':banks})
    
    if request.POST.get('login_bank_updated'):
        lead = Lead.objects.get(id=request.POST.get('login_bank_updated'))
        lead.login_bank_updated = True
        lead.login_bank_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        
        if request.POST.get('bank'):
            print(request.POST.get('bank'))
            lead.login_bank = LoginBank.objects.get(name=request.POST.get('bank'))
            lead.login_bank.save()
            lead.save()
            return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('login_bank_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('login_bank_updated_success'))
        lead.login_bank_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead,'banks':banks})

    if request.POST.get('login_bank_process_completed'):
        lead = Lead.objects.get(id=request.POST.get('login_bank_process_completed'))
        lead.login_bank_process_completed = True
        lead.login_bank_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('senction_letter_updated'):
        
        lead = Lead.objects.get(id=request.POST.get('senction_letter_updated'))
        if request.FILES.get('senction_letter',''):
            lead.senction_letter = request.FILES.get('senction_letter','')
        else:
            lead.senction_letter = ''
        lead.senction_letter_updated = True
        lead.senction_letter_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('senction_letter_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('senction_letter_updated_success'))
        lead.senction_letter_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('senction_amount_updated'):
        lead = Lead.objects.get(id=request.POST.get('senction_amount_updated'))
        lead.senction_amount = request.POST.get('senction_amount')
        lead.senction_amount_updated = True
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    

    if request.POST.get('senction_amount_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('senction_amount_updated_success'))
        lead.senction_amount_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('dsa_code_updated'):
        lead = Lead.objects.get(id=request.POST.get('dsa_code_updated'))
        lead.dsa_code = request.POST.get('dsa_code')
        lead.dsa_code_updated = True
        lead.dsa_code_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('dsa_code_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('dsa_code_updated_success'))
        lead.dsa_code_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('senction_date_updated'):
        lead = Lead.objects.get(id=request.POST.get('senction_date_updated'))
        print(request.POST.get('senction_date'))
        lead.senction_date = datetime.datetime.strptime(request.POST.get('senction_date'),'%Y-%m-%d')
        lead.senction_date_updated = True
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead}) 

    if request.POST.get('senction_date_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('senction_date_updated_success'))
        lead.senction_date_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('senction_process_completed'):
        lead = Lead.objects.get(id=request.POST.get('senction_process_completed'))
        lead.senction_process_completed = True
        lead.senction_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        
        lead.save()
        return redirect('yourlead')
    
    if request.POST.get('disbursement_updated'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_updated'))
        lead.disbursement_updated = True
        lead.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)  
        lead.disbursement = request.POST.get('disbursement')
        print('ABCD',lead.disbursement)
        if lead.disbursement == "on":
            lead.disbursement = True
            lead.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        else:
            lead.disbursement = False
            lead.disbursement_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc) 
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_success'):
        lead= Lead.objects.get(id=request.POST.get('disbursement_success'))
        lead.disbursement_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_proof_updated'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_proof_updated'))
        lead.disbursement_proof = request.FILES.get('disbursement_proof')
        lead.disbursement_proof_updated = True
        lead.disbursement_proof_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_proof_updated_success'):
        lead =Lead.objects.get(id=request.POST.get('disbursement_proof_updated_success'))
        lead.disbursement_proof_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_amount_updated'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_amount_updated'))
        lead.disbursement_amount = request.POST.get('disbursement_amount')
        lead.disbursement_amount_updated = True
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_amount_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_amount_updated_success'))
        lead.disbursement_amount_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('disbursement_date_updated'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_date_updated'))
        print(request.POST.get('disbursement_date'))
        # import pdb
        # pdb.set_trace()
        lead.disbursement_date = datetime.datetime.strptime(request.POST.get('disbursement_date'),'%Y-%m-%d')
        lead.disbursement_date_updated = True
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead}) 

    if request.POST.get('disbursement_date_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_date_updated_success'))
        lead.disbursement_date_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('payout_updated'):
        lead = Lead.objects.get(id=request.POST.get('payout_updated'))  
        lead.payout = request.POST.get('payout')  
        lead.payout_updated = True
        lead.payout_updated_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})

    if request.POST.get('payout_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('payout_updated_success'))
        lead.payout_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})


    if request.POST.get('disbursement_rejection_reason_updated'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_rejection_reason_updated'))
        lead.disbursement_rejection_reason = request.POST.get('disbursement_rejection_reason')
        lead.disbursement_rejection_reason_updated = True
        lead.disbursement_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    if request.POST.get('disbursement_rejection_reason_updated_success'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_rejection_reason_updated_success'))
        lead.disbursement_rejection_reason_updated = False
        lead.save()
        return render(request,'lead_html/lead_process_v2.html',{'lead':lead})
    
    
    if request.POST.get('disbursement_process_completed'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_process_completed'))
        lead.disbursement_process_completed_approved = True
        lead.verification_pending = True
        lead.verification_rejected = False
        lead.verification_approved = False
        lead.disbursement_process_completed_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return redirect('yourlead')
    
    if request.POST.get('disbursement_process_rejected'):
        lead = Lead.objects.get(id=request.POST.get('disbursement_process_rejected'))
        lead.disbursement_process_completed_rejected = True
        lead.disbursement_process_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
        lead.save()
        return redirect('yourlead')
        
    if request.POST.get('details'):
        lead =Lead.objects.get(id=request.POST.get('details'))
        context = {'ruser':ruser,'lead':lead}
        html_string = render_to_string('lead_html/pdf.html',context)
        html = HTML(string=html_string,base_url=request.build_absolute_uri())
        pdf = html.write_pdf(presentational_hints=True)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="lead.pdf"'
        return response

    if request.POST.get('chat'):
        lead =Lead.objects.get(id=request.POST.get('chat'))
        comments = Comment.objects.filter(lead=lead.id).order_by('-id')
        return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
    
    if request.POST.get('lead_chat_updated'):
        lead = Lead.objects.get(id=request.POST.get('lead_chat_updated'))
        comments = Comment.objects.filter(lead=lead.id).order_by('-id')
        print('ABCD')
        if not request.FILES.get('lead_attachments') and not request.POST.get('lead_chat'):

            messages.error(request,'Message or Attachement is missing')
            return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
        else:
            comment = Comment.objects.create(lead= lead,message=request.POST.get('lead_chat'),user=request.user,attachments=request.FILES.get('lead_attachments'))
            comment.save()
            return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
            
    if count==0:
        messages.error(request,'No Lead is Found')
        return render(request, 'lead_html/your_leads_v2.html',{'ruser':ruser,'leads':leads,'count':count})
    else:
        return render(request, 'lead_html/your_leads_v2.html',{'ruser':ruser,'leads':leads,'count':count})
    
    return render(request, 'lead_html/your_leads_v2.html',{'ruser':ruser,'leads':leads,'count':count})
        # leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code)).order_by('-id')
        # print(leads)

 

@login_required(login_url='login')
def pipeline(request):
    ruser = request.user
    if request.user.is_suspended == True or request.user.role == 'BO' or request.user.role == 'ACCOUNT':
        return render(request,'user_html/404_page.htm')

    today = datetime.date.today()
    current_date = datetime.date.today() 
    first = today.replace(day=1)  # first date of current month
    previous_month_date = first - datetime.timedelta(days=1)
    leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code)).filter(login_bank_updated_at__lt=first).exclude(Q(disbursement_process_completed_approved=True)| Q(disbursement_process_completed_rejected=True)).order_by('-id')
    count = leads.count()
    page = request.GET.get('page', 1)
    paginator = Paginator(leads, 2)
    try:
        leads = paginator.page(page)
    except PageNotAnInteger:
        leads = paginator.page(1)
    except EmptyPage:
        leads = paginator.page(paginator.num_pages)
    print(leads)
    
    print('ABCDFR',count)

    if request.POST.get('chat'):
        lead =Lead.objects.get(id=request.POST.get('chat'))
        comments = Comment.objects.filter(lead=lead.id).order_by('-id')
        return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
        
    if request.POST.get('lead_chat_updated'):
        lead = Lead.objects.get(id=request.POST.get('lead_chat_updated'))
        comments = Comment.objects.filter(lead=lead.id).order_by('-id')
        if not request.FILES.get('lead_attachments') and not request.POST.get('lead_chat'):
            messages.error(request,'Message or Attachement is missing')
            return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
        else:
            comment = Comment.objects.create(lead= lead,message=request.POST.get('lead_chat'),user=request.user,attachments=request.FILES.get('lead_attachments'))
            comment.save()
            return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
    
    print(leads)
    if ruser.role not in ['CONNECTOR','AF']:
        if count==0:
            messages.error(request,'No Lead is Found Greater Than 30 Days')
            print('ABCD') 
            return render(request, 'lead_html/pipeline_cases_v2.html',{'ruser':ruser,'leads':leads,'count':count})
        else:
            return render(request, 'lead_html/pipeline_cases_v2.html',{'ruser':ruser,'leads':leads,'count':count})
    else:
        if count==0:
            messages.error(request,'No Lead is Found Greater Than 30 Days')
            return render(request, 'lead_html/pipeline_cases_v2.html',{'ruser':ruser,'leads':leads,'count':count})
        else:
            return render(request, 'lead_html/pipeline_cases_v2.html',{'ruser':ruser,'leads':leads,'count':count})


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
            mail_subject_employee = 'Activate your Matpit Account.'
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
        print(request.POST.get('download_lead'))
        print(request.POST.get('download_user'))
        if request.POST.get('download_lead'):
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
                return render(request,'lead_html/reports_v2.html')

            if request.POST.get('startDate') > request.POST.get('endDate'):
                messages.error(request,'Please Select Correct Date Range')
                return render(request,'lead_html/reports_v2.html')

            leads = Lead.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
            leads_today = Lead.objects.filter(created_at=today)
            leads_previous_month = Lead.objects.filter(created_at__gte=previous_month_date,created_at__lte=today)
            leads_older_months = Lead.objects.filter(created_at__gte=older_month_date,created_at__lte=previous_month_date)
            leads_overall = Lead.objects.all()
            print(leads)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="BC_lead_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['FIRST NAME','LAST NAME','EMAIL','PHONE','CREATED AT','CREATED BY','LOAN TYPE','PURCHASE TYPE','JOB TYPE','JOB LOCATION','RENTAL INCOME(JOB)','RENTAL INCOME(BUSINESS)','HOW MUCH IN CASH(JOB)','HOW MUCH IN CASH(BUSINESS)','HOW MUCH IN ACCOUNT(JOB)','HOW MUCH IN ACCOUNT(BUSINESS)','TAKE HOME SALARY','DURATION IN PRESENT COMPANY','EXISTING EMI AMOUNT(JOB)','EXISTING EMI AMOUNT(BUSINESS)','BUSINESS LOCATION','DECLARED ITR','HOW MUCH ITR?','HOW MUCH IN ACCOUNT (ITR)','BUSINESS VINTAGE','NATURE OF BUSINESS','GST REGISTERED','KHATA','Property Location','AREA OF EXTENET (IH)','AREA OF EXTENET (SC)','AREA OF EXTENT (PLOT)','AREA OF EXTENT(FLAT)','AREA OF EXTENT(LAP)','Number Of Units','Number of Floors','Number of Units LAP','Number of Floor LAP','Bulding Age IH','Building Age LAP','PROJECT NAME','OC & CC RECIEVED','PLAN AVAILABLE(SC)','PLAN TYPE','PLAN AVAILABLE(IH)','PLAN AVAIALABLE(LAP)'])
            if request.POST.get('startDate') and request.POST.get('endDate'):
                for lead in leads:
                    writer.writerow(
                        [
                            lead.first_name, 
                            lead.last_name, 
                            lead.email,
                            lead.phone,
                            lead.created_at.date(),
                            lead.created_by.first_name + '' + lead.created_by.last_name,
                            lead.get_loan_type_display(),
                            lead.get_purchase_type_display(),
                            lead.get_job_type_display(),
                            lead.job_location,
                            'YES' if lead.rental_income_job else 'NO',
                            'YES' if lead.rental_income_bus else 'NO',
                            lead.how_much_in_cash_job,
                            lead.how_much_in_cash_bus,
                            lead.how_much_in_account_job,
                            lead.how_much_in_account_bus,
                            lead.take_home_salary,
                            lead.get_duration_in_present_company_display(),
                            lead.existing_emi_amount_job,
                            lead.existing_emi_amount_bus,
                            lead.business_location,
                            'YES' if lead.declared_itr else 'NO',
                            lead.how_much_itr,
                            lead.how_much_in_account_itr,
                            lead.business_vintage,
                            lead.nature_of_business,
                            'YES' if lead.gst_registered else 'NO',
                            lead.khata,
                            lead.property_location,
                            lead.area_of_extent_ih,
                            lead.area_of_extent_sc,
                            lead.area_of_extent_plot,
                            lead.area_of_extent_flat,
                            lead.area_of_extent_lap,
                            lead.number_of_unites,
                            lead.number_of_floors,
                            lead.number_of_units_lap,
                            lead.number_of_floors_lap,
                            lead.get_building_age_ih_display(),
                            lead.get_building_age_lap_display(),
                            lead.project_name,
                            lead.oc_cc_received,
                            'YES' if lead.plan_available_sc else 'NO',
                            lead.get_plan_type_display(),
                            'YES' if lead.plan_available_ih else 'NO',
                            'YES' if lead.plan_available_lap else 'NO',
                            ]
                            )
            if request.POST.get('today'):
                for lead in leads_today:
                    writer.writerow(
                        [
                            lead.first_name, 
                            lead.last_name, 
                            lead.email,
                            lead.phone,
                            lead.created_at.date(),
                            lead.created_by.first_name + '' + lead.created_by.last_name,
                            lead.get_loan_type_display(),
                            lead.get_purchase_type_display(),
                            lead.get_job_type_display(),
                            lead.job_location,
                            'YES' if lead.rental_income_job else 'NO',
                            'YES' if lead.rental_income_bus else 'NO',
                            lead.how_much_in_cash_job,
                            lead.how_much_in_cash_bus,
                            lead.how_much_in_account_job,
                            lead.how_much_in_account_bus,
                            lead.take_home_salary,
                            lead.get_duration_in_present_company_display(),
                            lead.existing_emi_amount_job,
                            lead.existing_emi_amount_bus,
                            lead.business_location,
                            'YES' if lead.declared_itr else 'NO',
                            lead.how_much_itr,
                            lead.how_much_in_account_itr,
                            lead.business_vintage,
                            lead.nature_of_business,
                            'YES' if lead.gst_registered else 'NO',
                            lead.khata,
                            lead.property_location,
                            lead.area_of_extent_ih,
                            lead.area_of_extent_sc,
                            lead.area_of_extent_plot,
                            lead.area_of_extent_flat,
                            lead.area_of_extent_lap,
                            lead.number_of_unites,
                            lead.number_of_floors,
                            lead.number_of_units_lap,
                            lead.number_of_floors_lap,
                            lead.get_building_age_ih_display(),
                            lead.get_building_age_lap_display(),
                            lead.project_name,
                            lead.oc_cc_received,
                            'YES' if lead.plan_available_sc else 'NO',
                            lead.get_plan_type_display(),
                            'YES' if lead.plan_available_ih else 'NO',
                            'YES' if lead.plan_available_lap else 'NO',
                            ]
                            )
            if leads_previous_month:
                for lead in leads_previous_month:
                    writer.writerow(
                        [
                            lead.first_name, 
                            lead.last_name, 
                            lead.email,
                            lead.phone,
                            lead.created_at.date(),
                            lead.created_by.first_name + '' + lead.created_by.last_name,
                            lead.get_loan_type_display(),
                            lead.get_purchase_type_display(),
                            lead.get_job_type_display(),
                            lead.job_location,
                            'YES' if lead.rental_income_job else 'NO',
                            'YES' if lead.rental_income_bus else 'NO',
                            lead.how_much_in_cash_job,
                            lead.how_much_in_cash_bus,
                            lead.how_much_in_account_job,
                            lead.how_much_in_account_bus,
                            lead.take_home_salary,
                            lead.get_duration_in_present_company_display(),
                            lead.existing_emi_amount_job,
                            lead.existing_emi_amount_bus,
                            lead.business_location,
                            'YES' if lead.declared_itr else 'NO',
                            lead.how_much_itr,
                            lead.how_much_in_account_itr,
                            lead.business_vintage,
                            lead.nature_of_business,
                            'YES' if lead.gst_registered else 'NO',
                            lead.khata,
                            lead.property_location,
                            lead.area_of_extent_ih,
                            lead.area_of_extent_sc,
                            lead.area_of_extent_plot,
                            lead.area_of_extent_flat,
                            lead.area_of_extent_lap,
                            lead.number_of_unites,
                            lead.number_of_floors,
                            lead.number_of_units_lap,
                            lead.number_of_floors_lap,
                            lead.get_building_age_ih_display(),
                            lead.get_building_age_lap_display(),
                            lead.project_name,
                            lead.oc_cc_received,
                            'YES' if lead.plan_available_sc else 'NO',
                            lead.get_plan_type_display(),
                            'YES' if lead.plan_available_ih else 'NO',
                            'YES' if lead.plan_available_lap else 'NO',
                            ]
                            )

            if leads_older_months:
                for lead in leads_older_months:
                    writer.writerow(
                        [
                            lead.first_name, 
                            lead.last_name, 
                            lead.email,
                            lead.phone,
                            lead.created_at.date(),
                            lead.created_by.first_name + '' + lead.created_by.last_name,
                            lead.get_loan_type_display(),
                            lead.get_purchase_type_display(),
                            lead.get_job_type_display(),
                            lead.job_location,
                            'YES' if lead.rental_income_job else 'NO',
                            'YES' if lead.rental_income_bus else 'NO',
                            lead.how_much_in_cash_job,
                            lead.how_much_in_cash_bus,
                            lead.how_much_in_account_job,
                            lead.how_much_in_account_bus,
                            lead.take_home_salary,
                            lead.get_duration_in_present_company_display(),
                            lead.existing_emi_amount_job,
                            lead.existing_emi_amount_bus,
                            lead.business_location,
                            'YES' if lead.declared_itr else 'NO',
                            lead.how_much_itr,
                            lead.how_much_in_account_itr,
                            lead.business_vintage,
                            lead.nature_of_business,
                            'YES' if lead.gst_registered else 'NO',
                            lead.khata,
                            lead.property_location,
                            lead.area_of_extent_ih,
                            lead.area_of_extent_sc,
                            lead.area_of_extent_plot,
                            lead.area_of_extent_flat,
                            lead.area_of_extent_lap,
                            lead.number_of_unites,
                            lead.number_of_floors,
                            lead.number_of_units_lap,
                            lead.number_of_floors_lap,
                            lead.get_building_age_ih_display(),
                            lead.get_building_age_lap_display(),
                            lead.project_name,
                            lead.oc_cc_received,
                            'YES' if lead.plan_available_sc else 'NO',
                            lead.get_plan_type_display(),
                            'YES' if lead.plan_available_ih else 'NO',
                            'YES' if lead.plan_available_lap else 'NO',
                            ]
                            )

            if leads_overall:
                for lead in leads_overall:
                    writer.writerow(
                        [
                            lead.first_name, 
                            lead.last_name, 
                            lead.email,
                            lead.phone,
                            lead.created_at.date(),
                            lead.created_by.first_name + '' + lead.created_by.last_name,
                            lead.get_loan_type_display(),
                            lead.get_purchase_type_display(),
                            lead.get_job_type_display(),
                            lead.job_location,
                            'YES' if lead.rental_income_job else 'NO',
                            'YES' if lead.rental_income_bus else 'NO',
                            lead.how_much_in_cash_job,
                            lead.how_much_in_cash_bus,
                            lead.how_much_in_account_job,
                            lead.how_much_in_account_bus,
                            lead.take_home_salary,
                            lead.get_duration_in_present_company_display(),
                            lead.existing_emi_amount_job,
                            lead.existing_emi_amount_bus,
                            lead.business_location,
                            'YES' if lead.declared_itr else 'NO',
                            lead.how_much_itr,
                            lead.how_much_in_account_itr,
                            lead.business_vintage,
                            lead.nature_of_business,
                            'YES' if lead.gst_registered else 'NO',
                            lead.khata,
                            lead.property_location,
                            lead.area_of_extent_ih,
                            lead.area_of_extent_sc,
                            lead.area_of_extent_plot,
                            lead.area_of_extent_flat,
                            lead.area_of_extent_lap,
                            lead.number_of_unites,
                            lead.number_of_floors,
                            lead.number_of_units_lap,
                            lead.number_of_floors_lap,
                            lead.get_building_age_ih_display(),
                            lead.get_building_age_lap_display(),
                            lead.project_name,
                            lead.oc_cc_received,
                            'YES' if lead.plan_available_sc else 'NO',
                            lead.get_plan_type_display(),
                            'YES' if lead.plan_available_ih else 'NO',
                            'YES' if lead.plan_available_lap else 'NO',
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
                return render(request,'lead_html/reports_v2.html')

            if request.POST.get('startDate') > request.POST.get('endDate'):
                messages.error(request,'Please Select Correct Date Range')
                return render(request,'lead_html/reports_v2.html')
            users = CustomUser.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
            print(users)

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="BC_Users_report.csv"'
            writer = csv.writer(response)
            writer.writerow(['FIRST NAME','LAST NAME','EMAIL','PHONE','CREATED AT','REFERRD BY','REFFERAL CODE','MANAGER NAME','ROLE','PROFESSIONAL OCCUPATION','HOUSING LOAN','MORTGAGE LOAN','VEHICAL LOAN','LEADS' ])
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
                        user.lead_user.count(),

                        ]
                        )
            return response
        return render(request,'lead_html/reports_v2.html')
    else:
        return render(request,'lead_html/reports_v2.html')

@login_required(login_url='login')
def upload_lead(request):
    print('abcd')
    if request.POST.get('upload'):
        
        csv_file = request.FILES('file')

        if not csv_file.name.endswith('.csv'):
            messages.error(request,'This is not a CSV File')
        
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string)
        for column in csv.reader(io_string,delimiter=',',quotechar="|"):
            first_name = column[0]    
            last_name = column[1]    
            email = column[2]
            phone = column[3]
            loan_type = column[4]
            if loan_type == 'construction':
                loan_type = 'SC'
            if loan_type == 'purchase':
                loan_type = 'P'
            if loan_type == 'lap':
                loan_type = 'LAP'
            

            plan_type = column[4]
            if plan_type == 'govt':
                plan_type = 'ABG'
            else:
                plan_type = 'Normal'

            plan_available_sc =  column[5]
            if plan_available_sc == "on":
                plan_available_sc = True
            else:
                plan_available_sc = False
            
            area_of_extent_sc = column[6]
                    
            purchase_type = column[7]
            
            if purchase_type == 'plot':
                purchase_type = 'Pl'
            
            area_of_extent_plot = column[8]
                    
            if purchase_type == 'ih':
                purchase_type = 'IH'
            
            number_of_unites = column[9]
            number_of_floors = column[10]
            area_of_extent_ih = column[11]
            
            building_age_ih = column[12]
            if building_age_ih == 'lessthantenyearsih':
                building_age_ih = 'l10_ih'
            if building_age_ih == 'morethantenyearsih':
                building_age_ih = 'm10_ih'
            
            plan_available_ih = column[13]
            if plan_available_ih == "on":
                plan_available_ih = True
            else:
                plan_available_ih = False
            
            purchase_type = column[14]
            if purchase_type == 'flat':
                purchase_type = 'F'
            
            project_name = column[15]
            oc_cc_received = column[16]
            area_of_extent_flat = column[17]
            number_of_units_lap = column[18]
            number_of_floors_lap = column[19]
            area_of_extent_lap = column[20]
            
            building_age_lap = column[21]
            if building_age_lap == 'lessthantenyears':
                building_age_lap = 'l10_lap'
            if building_age_lap == 'morethantenyears':
                building_age_lap = 'm10_lap'

            plan_available_lap = column[22]
            if plan_available_lap == "on":
                plan_available_lap = True
            else:
                plan_available_lap = False    

            
            #     pancard_image.save()
            # if request.FILES['cancelled_cheque_image']:
            #     cancelled_cheque_image = request.FILES['cancelled_cheque_image']
            

            job_type = column[23]
            if job_type == '2':
                job_type = 'Sal'
            if job_type == '3':
                job_type ='SE'

            job_location = column[24]
            rental_income_job = column[25]
            if rental_income_job == "on":
                rental_income_job = True
            else:
                rental_income_job = False

            take_home_salary = column[26]
            duration_in_present_company = column[27]
            if duration_in_present_company == 'lessthantwoyears':
                duration_in_present_company = 'l2'
            else:
                duration_in_present_company = 'm2'
            
            how_much_in_cash_job = column[28]
            how_much_in_account_job = column[29]           
            existing_emi_amount_job = column[30]           
            business_location = column[31]
            
            rental_income_bus = column[32]
            if rental_income_bus == "on":
                rental_income_bus = True
            else:
                rental_income_bus = False
            
            how_much_in_cash_bus = column[33]
            how_much_in_account_bus = column[34]  
            
            declared_itr = column[35]
            if declared_itr =="on":
                declared_itr = True
            else:
                declared_itr = False
            
            how_much_itr = column[36]
            
            business_vintage = column[37]
            nature_of_business = column[38]
            
            if nature_of_business == 'NONE':
                nature_of_business = 'NONE'
            else:
                nature_of_business = 'NONE'
            
            gst_registered = column[39]
            if gst_registered == "on":
                gst_registered = True
            else:
                gst_registered = False
            
            existing_emi_amount_bus = column[40]
        
            khata = column[41]
            if khata == 'akhata':
                khata = 'A'
            if khata == 'bda':
                khata = 'BDAYR'
            if khata == 'bmrda':
                khata = 'BMRDA'
            if khata == 'bcon':
                khata = 'BCON'
            if khata == 'bncon':
                khata = 'BNCON'
            if khata == 'cmc':
                khata = 'CMC'
            if khata == 'manual':
                khata = 'Manual'

            property_location = column[42]

            lead_update = True

            leads = Lead.objects.update_or_create(
                first_name=first_name,
                last_name = last_name,
                created_by = request.user,
                referral_code = request.user.referral_code,
                referred_by = request.user.referred_by,
                email = email,
                phone = phone,
                adhaar_image = adhaar_image,
                pancard_image = pancard_image,
                loan_type=loan_type,
                purchase_type=purchase_type,
                job_type=job_type,
                job_location=job_location,
                rental_income_job=rental_income_job,
                how_much_in_cash_job=how_much_in_cash_job,
                how_much_in_account_job=how_much_in_account_job,
                take_home_salary=take_home_salary,
                duration_in_present_company=duration_in_present_company,
                existing_emi_amount_job=existing_emi_amount_job,
                rental_income_bus=rental_income_bus,
                how_much_in_cash_bus=how_much_in_cash_bus,
                how_much_in_account_bus=how_much_in_account_bus,
                existing_emi_amount_bus=existing_emi_amount_bus,
                business_location=business_location,
                declared_itr=declared_itr,
                how_much_itr = how_much_itr,
                business_vintage=business_vintage,
                nature_of_business=nature_of_business,
                gst_registered=gst_registered,
                khata=khata,
                property_location=property_location,
                area_of_extent_ih=area_of_extent_ih,
                area_of_extent_sc=area_of_extent_sc,
                area_of_extent_plot=area_of_extent_plot,
                area_of_extent_flat=area_of_extent_flat,
                area_of_extent_lap=area_of_extent_lap,
                number_of_unites=number_of_unites,
                number_of_floors=number_of_floors,
                building_age_ih=building_age_ih,
                building_age_lap=building_age_lap,
                project_name=project_name,
                oc_cc_received=oc_cc_received,
                plan_available_sc=plan_available_sc,
                plan_available_ih=plan_available_ih,
                plan_available_lap=plan_available_lap,
                plan_type = plan_type,
                lead_update=lead_update
            )
        lead.save()
        return render(request,'lead_html/test.html')

@login_required(login_url='login')
def dashboard(request):

    ############################## Lead Notification ###############################

    lead_notification_count = Notification.objects.filter(notified_user = request.user.id,read_lead_notification=True).count()
    lead_notification_first_name = Notification.objects.filter(notified_user = request.user.id,read_lead_notification=True).values_list('lead__created_by__first_name')
    lead_notification_last_name = Notification.objects.filter(notified_user = request.user.id,read_lead_notification=True).values_list('lead__created_by__first_name')
    

    
    
    

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

        
        leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_leads = Lead.objects.filter(created_by=ruser).count()
        direct_leads_previous_month = Lead.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_leads_current_month = Lead.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_leads_today = Lead.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_leads_yesterday = Lead.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_leads_custom = Lead.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_leads_current_month > 0:
            direct_leads_percentage = (direct_leads_previous_month)*100/direct_leads_current_month
        else:
            direct_leads_percentage = 0
        
        direct_leads_jan = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_leads_feb = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_leads_mar = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_leads_apr = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_leads_may = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_leads_jun = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_leads_jul = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_leads_aug = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_leads_sept = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_leads_oct = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_leads_nov = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_leads_dec = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_leads_previous_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_leads_current_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_leads_today = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_leads_yesterday = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_leads_custom = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_leads_current_month>0:
            indirect_leads_percentage = (indirect_leads_previous_month)*100/indirect_leads_current_month
        else:
            indirect_leads_percentage = 0
        indirect_leads_jan = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_leads_feb = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_leads_mar = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_leads_apr = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_leads_may = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_leads_jun = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_leads_jul = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_leads_aug = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_leads_sept = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_leads_oct = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_leads_nov = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_leads_dec = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_leads = direct_leads + indirect_leads
        total_leads_previous_month = direct_leads_previous_month + indirect_leads_previous_month
        total_leads_current_month = direct_leads_current_month + indirect_leads_current_month
        total_leads_today = direct_leads_today + indirect_leads_today
        total_leads_yesterday = direct_leads_yesterday + indirect_leads_yesterday
        total_leads_custom = direct_leads_custom + indirect_leads_custom

        if total_leads_current_month>0:
            total_leads_percentage = (total_leads_previous_month)*100/total_leads_current_month
        else:
            total_leads_percentage = 0

        total_leads_jan = direct_leads_jan + indirect_leads_jan
        total_leads_feb = direct_leads_feb + indirect_leads_feb
        total_leads_mar = direct_leads_mar + indirect_leads_mar
        total_leads_apr = direct_leads_apr + indirect_leads_apr
        total_leads_may = direct_leads_may + indirect_leads_may
        total_leads_jun = direct_leads_jun + indirect_leads_jun
        total_leads_jul = direct_leads_jul + indirect_leads_jul
        total_leads_aug = direct_leads_aug + indirect_leads_aug
        total_leads_sept = direct_leads_sept + indirect_leads_sept
        total_leads_oct = direct_leads_oct + indirect_leads_oct
        total_leads_nov = direct_leads_nov + indirect_leads_nov
        total_leads_dec = direct_leads_dec + indirect_leads_dec
        
        monthly_housing_loan = ruser.housing_loan
        monthly_mortgage_loan = ruser.mortgage_loan
        monthly_vehical_loan = ruser.vehical_loan
        monthly_personal_loan = ruser.personal_loan

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
            'leads':leads,
            'direct_leads':direct_leads,
            'direct_leads_today':direct_leads_today,
            'direct_leads_yesterday':direct_leads_yesterday,
            'direct_leads_custom':direct_leads_custom,
            'direct_leads_previous_month':direct_leads_previous_month,
            'direct_leads_current_month':direct_leads_current_month,
            'direct_leads_percentage':int(direct_leads_percentage),
            'indirect_leads':indirect_leads,
            'indirect_leads_today':indirect_leads_today,
            'indirect_leads_yesterday':indirect_leads_yesterday,
            'indirect_leads_previous_month':indirect_leads_previous_month,
            'indirect_leads_current_month':indirect_leads_current_month,
            'indirect_leads_custom':indirect_leads_custom,
            'indirect_leads_percentage':int(indirect_leads_percentage),
            'total_leads':total_leads,
            'total_leads_today':total_leads_today,
            'total_leads_yesterday':total_leads_yesterday,
            'total_leads_custom':total_leads_custom,
            'total_leads_previous_month':total_leads_previous_month,
            'total_leads_current_month':total_leads_current_month,
            'total_leads_percentage':int(total_leads_percentage),
            'monthly_housing_loan':monthly_housing_loan,
            'monthly_mortgage_loan':monthly_mortgage_loan,
            'monthly_vehical_loan':monthly_vehical_loan,
            'monthly_personal_loan':monthly_personal_loan,
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
            'direct_leads_jan' : direct_leads_jan ,
            'direct_leads_feb' : direct_leads_feb ,
            'direct_leads_mar' : direct_leads_mar ,
            'direct_leads_apr' : direct_leads_apr ,
            'direct_leads_may' : direct_leads_may ,
            'direct_leads_jun' : direct_leads_jun ,
            'direct_leads_jul' : direct_leads_jul ,
            'direct_leads_aug' : direct_leads_aug ,
            'direct_leads_sept': direct_leads_sept,
            'direct_leads_oct' : direct_leads_oct ,
            'direct_leads_nov' : direct_leads_nov ,
            'direct_leads_dec' : direct_leads_dec ,
            'indirect_leads_jan' : indirect_leads_jan ,
            'indirect_leads_feb' : indirect_leads_feb ,
            'indirect_leads_mar' : indirect_leads_mar ,
            'indirect_leads_apr' : indirect_leads_apr ,
            'indirect_leads_may' : indirect_leads_may ,
            'indirect_leads_jun' : indirect_leads_jun ,
            'indirect_leads_jul' : indirect_leads_jul ,
            'indirect_leads_aug' : indirect_leads_aug ,
            'indirect_leads_sept': indirect_leads_sept,
            'indirect_leads_oct' : indirect_leads_oct ,
            'indirect_leads_nov' : indirect_leads_nov ,
            'indirect_leads_dec' : indirect_leads_dec ,
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
            'total_leads_jan': total_leads_jan ,
            'total_leads_feb': total_leads_feb ,
            'total_leads_mar': total_leads_mar ,
            'total_leads_apr': total_leads_apr ,
            'total_leads_may': total_leads_may ,
            'total_leads_jun': total_leads_jun ,
            'total_leads_jul': total_leads_jul ,
            'total_leads_aug': total_leads_aug ,
            'total_leads_sept': total_leads_sept,
            'total_leads_oct': total_leads_oct ,
            'total_leads_nov': total_leads_nov ,
            'total_leads_dec': total_leads_dec,
            'lead_notification_count':lead_notification_count,
            'lead_notification_first_name':lead_notification_first_name,
            'lead_notification_last_name':lead_notification_last_name,
        }
        return render(request,"user_html/con_dashboard_v2.html",context)
    if request.user.role == 'AF' and request.user.is_verified:
        lead_notification_count = Notification.objects.filter(notified_user = request.user.id,read_lead_notification=True).count()
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

        
        leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_leads = Lead.objects.filter(created_by=ruser).count()
        direct_leads_previous_month = Lead.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_leads_current_month = Lead.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_leads_today = Lead.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_leads_yesterday = Lead.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_leads_custom = Lead.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_leads_current_month > 0:
            direct_leads_percentage = (direct_leads_previous_month)*100/direct_leads_current_month
        else:
            direct_leads_percentage = 0
        
        direct_leads_jan = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_leads_feb = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_leads_mar = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_leads_apr = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_leads_may = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_leads_jun = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_leads_jul = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_leads_aug = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_leads_sept = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_leads_oct = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_leads_nov = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_leads_dec = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_leads_previous_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_leads_current_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_leads_today = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_leads_yesterday = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_leads_custom = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_leads_current_month>0:
            indirect_leads_percentage = (indirect_leads_previous_month)*100/indirect_leads_current_month
        else:
            indirect_leads_percentage = 0
        indirect_leads_jan = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_leads_feb = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_leads_mar = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_leads_apr = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_leads_may = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_leads_jun = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_leads_jul = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_leads_aug = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_leads_sept = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_leads_oct = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_leads_nov = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_leads_dec = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_leads = direct_leads + indirect_leads
        total_leads_previous_month = direct_leads_previous_month + indirect_leads_previous_month
        total_leads_current_month = direct_leads_current_month + indirect_leads_current_month
        total_leads_today = direct_leads_today + indirect_leads_today
        total_leads_yesterday = direct_leads_yesterday + indirect_leads_yesterday
        total_leads_custom = direct_leads_custom + indirect_leads_custom

        if total_leads_current_month>0:
            total_leads_percentage = (total_leads_previous_month)*100/total_leads_current_month
        else:
            total_leads_percentage = 0

        total_leads_jan = direct_leads_jan + indirect_leads_jan
        total_leads_feb = direct_leads_feb + indirect_leads_feb
        total_leads_mar = direct_leads_mar + indirect_leads_mar
        total_leads_apr = direct_leads_apr + indirect_leads_apr
        total_leads_may = direct_leads_may + indirect_leads_may
        total_leads_jun = direct_leads_jun + indirect_leads_jun
        total_leads_jul = direct_leads_jul + indirect_leads_jul
        total_leads_aug = direct_leads_aug + indirect_leads_aug
        total_leads_sept = direct_leads_sept + indirect_leads_sept
        total_leads_oct = direct_leads_oct + indirect_leads_oct
        total_leads_nov = direct_leads_nov + indirect_leads_nov
        total_leads_dec = direct_leads_dec + indirect_leads_dec
        
        monthly_housing_loan = ruser.housing_loan
        monthly_mortgage_loan = ruser.mortgage_loan
        monthly_vehical_loan = ruser.vehical_loan
        monthly_personal_loan = ruser.personal_loan

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
            'leads':leads,
            'direct_leads':direct_leads,
            'direct_leads_today':direct_leads_today,
            'direct_leads_yesterday':direct_leads_yesterday,
            'direct_leads_custom':direct_leads_custom,
            'direct_leads_previous_month':direct_leads_previous_month,
            'direct_leads_current_month':direct_leads_current_month,
            'direct_leads_percentage':int(direct_leads_percentage),
            'indirect_leads':indirect_leads,
            'indirect_leads_today':indirect_leads_today,
            'indirect_leads_yesterday':indirect_leads_yesterday,
            'indirect_leads_previous_month':indirect_leads_previous_month,
            'indirect_leads_current_month':indirect_leads_current_month,
            'indirect_leads_custom':indirect_leads_custom,
            'indirect_leads_percentage':int(indirect_leads_percentage),
            'total_leads':total_leads,
            'total_leads_today':total_leads_today,
            'total_leads_yesterday':total_leads_yesterday,
            'total_leads_custom':total_leads_custom,
            'total_leads_previous_month':total_leads_previous_month,
            'total_leads_current_month':total_leads_current_month,
            'total_leads_percentage':int(total_leads_percentage),
            'monthly_housing_loan':monthly_housing_loan,
            'monthly_mortgage_loan':monthly_mortgage_loan,
            'monthly_vehical_loan':monthly_vehical_loan,
            'monthly_personal_loan':monthly_personal_loan,
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
            'direct_leads_jan' : direct_leads_jan ,
            'direct_leads_feb' : direct_leads_feb ,
            'direct_leads_mar' : direct_leads_mar ,
            'direct_leads_apr' : direct_leads_apr ,
            'direct_leads_may' : direct_leads_may ,
            'direct_leads_jun' : direct_leads_jun ,
            'direct_leads_jul' : direct_leads_jul ,
            'direct_leads_aug' : direct_leads_aug ,
            'direct_leads_sept': direct_leads_sept,
            'direct_leads_oct' : direct_leads_oct ,
            'direct_leads_nov' : direct_leads_nov ,
            'direct_leads_dec' : direct_leads_dec ,
            'indirect_leads_jan' : indirect_leads_jan ,
            'indirect_leads_feb' : indirect_leads_feb ,
            'indirect_leads_mar' : indirect_leads_mar ,
            'indirect_leads_apr' : indirect_leads_apr ,
            'indirect_leads_may' : indirect_leads_may ,
            'indirect_leads_jun' : indirect_leads_jun ,
            'indirect_leads_jul' : indirect_leads_jul ,
            'indirect_leads_aug' : indirect_leads_aug ,
            'indirect_leads_sept': indirect_leads_sept,
            'indirect_leads_oct' : indirect_leads_oct ,
            'indirect_leads_nov' : indirect_leads_nov ,
            'indirect_leads_dec' : indirect_leads_dec ,
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
            'total_leads_jan': total_leads_jan ,
            'total_leads_feb': total_leads_feb ,
            'total_leads_mar': total_leads_mar ,
            'total_leads_apr': total_leads_apr ,
            'total_leads_may': total_leads_may ,
            'total_leads_jun': total_leads_jun ,
            'total_leads_jul': total_leads_jul ,
            'total_leads_aug': total_leads_aug ,
            'total_leads_sept': total_leads_sept,
            'total_leads_oct': total_leads_oct ,
            'total_leads_nov': total_leads_nov ,
            'total_leads_dec': total_leads_dec,
            'lead_notification_count':lead_notification_count,
            'lead_notification_first_name':lead_notification_first_name,
            'lead_notification_last_name':lead_notification_last_name,
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

        
        leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by=ruser)| Q(created_by__manager__referred_by=ruser.referral_code))
        
        direct_leads = Lead.objects.filter(created_by=ruser).count()
        direct_leads_previous_month = Lead.objects.filter(created_by=ruser,created_at__gte=start_date,created_at__lt=end_date).count()
        direct_leads_current_month = Lead.objects.filter(created_by=ruser,created_at__gte=previous_month_date,created_at__lt=today).count()
        direct_leads_today = Lead.objects.filter(created_by=ruser,created_at__gt=yesterday,created_at__lt=tomorrow).count()
        direct_leads_yesterday = Lead.objects.filter(created_by=ruser,created_at=yesterday).count()
        direct_leads_custom = Lead.objects.filter(created_by=ruser,created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        
        if direct_leads_current_month > 0:
            direct_leads_percentage = (direct_leads_previous_month)*100/direct_leads_current_month
        else:
            direct_leads_percentage = 0
        
        direct_leads_jan = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jan,created_at__lt=feb).count()
        direct_leads_feb = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=feb,created_at__lt=mar).count()
        direct_leads_mar = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=mar,created_at__lt=apr).count()
        direct_leads_apr = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=apr,created_at__lt=may).count()
        direct_leads_may = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=may,created_at__lt=jun).count()
        direct_leads_jun = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=jun,created_at__lt=july).count()
        direct_leads_jul = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=july,created_at__lt=aug).count()
        direct_leads_aug = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=aug,created_at__lt=sept).count()
        direct_leads_sept = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=sept,created_at__lt=octo).count()
        direct_leads_oct = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=octo,created_at__lt=nov).count()
        direct_leads_nov = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=nov,created_at__lt=dec).count()
        direct_leads_dec = Lead.objects.filter(referred_by=ruser.referral_code,created_at__gte=dec,created_at__lt=next_year_month).count()
        
        indirect_leads = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code)).count() 
        indirect_leads_previous_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=start_date,created_at__lt=end_date).count() 
        indirect_leads_current_month = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=previous_month_date,created_at__lt=today).count() 
        indirect_leads_today = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gt=yesterday,created_at__lt=tomorrow).count()
        indirect_leads_yesterday = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at=yesterday).count()
        indirect_leads_custom = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=custom_start_date,created_at__lte=custom_end_date).count()
        if indirect_leads_current_month>0:
            indirect_leads_percentage = (indirect_leads_previous_month)*100/indirect_leads_current_month
        else:
            indirect_leads_percentage = 0
        indirect_leads_jan = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jan,created_at__lte=feb).count()
        indirect_leads_feb = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=feb,created_at__lte=mar).count()
        indirect_leads_mar = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=mar,created_at__lte=apr).count()
        indirect_leads_apr = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=apr,created_at__lte=may).count()
        indirect_leads_may = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=may,created_at__lte=jun).count()
        indirect_leads_jun = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=jun,created_at__lte=july).count()
        indirect_leads_jul = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=july,created_at__lte=aug).count()
        indirect_leads_aug = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=aug,created_at__lte=sept).count()
        indirect_leads_sept = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=sept,created_at__lte=octo).count()
        indirect_leads_oct = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=octo,created_at__lte=nov).count()
        indirect_leads_nov = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=nov,created_at__lte=dec).count()
        indirect_leads_dec = Lead.objects.filter(Q(referred_by=ruser.referral_code)| Q(created_by__manager__referred_by=ruser.referral_code),created_at__gte=dec,created_at__lt=next_year_month).count()


        total_leads = direct_leads + indirect_leads
        total_leads_previous_month = direct_leads_previous_month + indirect_leads_previous_month
        total_leads_current_month = direct_leads_current_month + indirect_leads_current_month
        total_leads_today = direct_leads_today + indirect_leads_today
        total_leads_yesterday = direct_leads_yesterday + indirect_leads_yesterday
        total_leads_custom = direct_leads_custom + indirect_leads_custom

        if total_leads_current_month>0:
            total_leads_percentage = (total_leads_previous_month)*100/total_leads_current_month
        else:
            total_leads_percentage = 0

        total_leads_jan = direct_leads_jan + indirect_leads_jan
        total_leads_feb = direct_leads_feb + indirect_leads_feb
        total_leads_mar = direct_leads_mar + indirect_leads_mar
        total_leads_apr = direct_leads_apr + indirect_leads_apr
        total_leads_may = direct_leads_may + indirect_leads_may
        total_leads_jun = direct_leads_jun + indirect_leads_jun
        total_leads_jul = direct_leads_jul + indirect_leads_jul
        total_leads_aug = direct_leads_aug + indirect_leads_aug
        total_leads_sept = direct_leads_sept + indirect_leads_sept
        total_leads_oct = direct_leads_oct + indirect_leads_oct
        total_leads_nov = direct_leads_nov + indirect_leads_nov
        total_leads_dec = direct_leads_dec + indirect_leads_dec
        
        monthly_housing_loan = ruser.housing_loan
        monthly_mortgage_loan = ruser.mortgage_loan
        monthly_vehical_loan = ruser.vehical_loan
        monthly_personal_loan = ruser.personal_loan

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
            'leads':leads,
            'direct_leads':direct_leads,
            'direct_leads_today':direct_leads_today,
            'direct_leads_yesterday':direct_leads_yesterday,
            'direct_leads_custom':direct_leads_custom,
            'direct_leads_previous_month':direct_leads_previous_month,
            'direct_leads_current_month':direct_leads_current_month,
            'direct_leads_percentage':int(direct_leads_percentage),
            'indirect_leads':indirect_leads,
            'indirect_leads_today':indirect_leads_today,
            'indirect_leads_yesterday':indirect_leads_yesterday,
            'indirect_leads_previous_month':indirect_leads_previous_month,
            'indirect_leads_current_month':indirect_leads_current_month,
            'indirect_leads_custom':indirect_leads_custom,
            'indirect_leads_percentage':int(indirect_leads_percentage),
            'total_leads':total_leads,
            'total_leads_today':total_leads_today,
            'total_leads_yesterday':total_leads_yesterday,
            'total_leads_custom':total_leads_custom,
            'total_leads_previous_month':total_leads_previous_month,
            'total_leads_current_month':total_leads_current_month,
            'total_leads_percentage':int(total_leads_percentage),
            'monthly_housing_loan':monthly_housing_loan,
            'monthly_mortgage_loan':monthly_mortgage_loan,
            'monthly_vehical_loan':monthly_vehical_loan,
            'monthly_personal_loan':monthly_personal_loan,
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
            'direct_leads_jan' : direct_leads_jan ,
            'direct_leads_feb' : direct_leads_feb ,
            'direct_leads_mar' : direct_leads_mar ,
            'direct_leads_apr' : direct_leads_apr ,
            'direct_leads_may' : direct_leads_may ,
            'direct_leads_jun' : direct_leads_jun ,
            'direct_leads_jul' : direct_leads_jul ,
            'direct_leads_aug' : direct_leads_aug ,
            'direct_leads_sept': direct_leads_sept,
            'direct_leads_oct' : direct_leads_oct ,
            'direct_leads_nov' : direct_leads_nov ,
            'direct_leads_dec' : direct_leads_dec ,
            'indirect_leads_jan' : indirect_leads_jan ,
            'indirect_leads_feb' : indirect_leads_feb ,
            'indirect_leads_mar' : indirect_leads_mar ,
            'indirect_leads_apr' : indirect_leads_apr ,
            'indirect_leads_may' : indirect_leads_may ,
            'indirect_leads_jun' : indirect_leads_jun ,
            'indirect_leads_jul' : indirect_leads_jul ,
            'indirect_leads_aug' : indirect_leads_aug ,
            'indirect_leads_sept': indirect_leads_sept,
            'indirect_leads_oct' : indirect_leads_oct ,
            'indirect_leads_nov' : indirect_leads_nov ,
            'indirect_leads_dec' : indirect_leads_dec ,
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
            'total_leads_jan': total_leads_jan ,
            'total_leads_feb': total_leads_feb ,
            'total_leads_mar': total_leads_mar ,
            'total_leads_apr': total_leads_apr ,
            'total_leads_may': total_leads_may ,
            'total_leads_jun': total_leads_jun ,
            'total_leads_jul': total_leads_jul ,
            'total_leads_aug': total_leads_aug ,
            'total_leads_sept': total_leads_sept,
            'total_leads_oct': total_leads_oct ,
            'total_leads_nov': total_leads_nov ,
            'total_leads_dec': total_leads_dec,
            'lead_notification_count':lead_notification_count,
            'lead_notification_first_name':lead_notification_first_name,
            'lead_notification_last_name':lead_notification_last_name,
        }

        return render(request,"user_html/dashboard_v2.html",context)

def test(request):
    return render(request,'lead_html/test.html')

@login_required(login_url='login')
def lead_verify(request):
    if request.user.role == 'ACCOUNT' or request.user.role == 'ADMIN' :
        leads = Lead.objects.filter(disbursement_process_completed_approved=True,verification_pending=True)
        print(leads)
        count = leads.count()
        page = request.GET.get('page', 1)
        paginator = Paginator(leads, 10)
        try:
            leads = paginator.page(page)
        except PageNotAnInteger:
            leads = paginator.page(1)
        except EmptyPage:
            leads = paginator.page(paginator.num_pages)
        if request.method == 'POST':
            if request.POST.get('verification_approve'):
                    verified_lead =Lead.objects.get(id=request.POST.get('verification_approve'))
                    verified_lead.verification_pending = False
                    verified_lead.verification_approved = True
                    verified_lead.verification_rejected = False
                    print(request)
                    verified_lead.verification_approved_by = request.user
                    verified_lead.verification_approved_at = datetime.datetime.utcnow().replace(tzinfo=utc)  
                    verified_lead.save()
                    return redirect('account')
            
            if request.POST.get('verification_reject'):
                rejected_lead = Lead.objects.get(id=request.POST.get('verification_reject'))
                rejected_lead.verification_pending = False
                rejected_lead.verification_rejected = True
                rejected_lead.verification_approved = False
                rejected_lead.disbursement_process_completed_approved = False
                rejected_lead.verification_rejected_by = request.user
                rejected_lead.verification_rejected_at = datetime.datetime.utcnow().replace(tzinfo=utc)
                rejected_lead.verification_rejection_reason = request.POST.get('verification_rejection_reason')
                rejected_lead.save()
                messages.error(request,'Lead is rejected due to the reason {0}'.format(rejected_lead.verification_rejection_reason))
                return render(request,'lead_html/lead_process_v2.html',{'lead':rejected_lead})
        
        if request.POST.get('chat'):
            lead =Lead.objects.get(id=request.POST.get('chat'))
            comments = Comment.objects.filter(lead=lead.id).order_by('-id')
            return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
        
        if request.POST.get('lead_chat_updated'):
            lead = Lead.objects.get(id=request.POST.get('lead_chat_updated'))
            comments = Comment.objects.filter(lead=lead.id).order_by('-id')
            if not request.FILES.get('lead_attachments') and not request.POST.get('lead_chat'):
                messages.error(request,'Message or Attachement is missing')
                return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
            else:
                comment = Comment.objects.create(lead= lead,message=request.POST.get('lead_chat'),user=request.user,attachments=request.FILES.get('lead_attachments'))
                comment.save()
                return render(request,'chat_html/chat_v2.html',{'lead':lead,'comments':comments})
        return render(request,'lead_html/lead_verify_v2.html',{'leads':leads,'count':count})
    else:
        return render(request,'user_html/404_page.htm')

@login_required(login_url='login')
def accountdashboard(request):
    leads = Lead.objects.filter(verification_approved=True).order_by('-id')
    if request.POST.get('other'):
        lead = Lead.objects.get(id=request.POST.get('other'))
        lead.save()
        context = {
            'lead':lead
        }
        return render (request,'lead_html/other_details_v2.html',context)
    
    if request.POST.get('other_details'):
        lead = Lead.objects.get(id=request.POST.get('other_details'))
        lead.actual_disbursement = request.POST.get('actual_disbursement')
        lead.payout_recieved_percentage = request.POST.get('payout_recieved_percentage')
        lead.payout_recieved_date = datetime.datetime.strptime(request.POST.get('payout_recieved_date'),'%Y-%m-%d')
        lead.incentives_percentage = request.POST.get('incentives_percentage')
        lead.payout_paid = round(float(int(lead.actual_disbursement) * int(lead.payout))/100,2)
        lead.payout_recieved = round(float(lead.actual_disbursement) * float(lead.payout_recieved_percentage)/100,2)
        lead.incentives = round(float(lead.actual_disbursement) * float(lead.incentives_percentage)/100,2)
        lead.net_revenue = round(float(lead.payout_recieved) - float(lead.payout_paid) + float(lead.incentives),2)
        
        lead.other_details_updated = True
        lead.save()
        context = {
            'lead':lead
        }
        return redirect('account')
    
    if request.POST.get('completed'):
        lead = Lead.objects.get(id=request.POST.get('completed'))
        return render (request,'lead_html/mic_dashboard_v2.html',{'lead':lead})
    

    return render(request,'lead_html/accounts_v2.html',{'leads':leads})
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
    categories = Category.objects.all()
    if request.user.is_suspended == True:
        return render(request,'user_html/404_page.htm')

    if request.method == 'POST': 
        
        categories_list = Category.objects.filter(name__in=request.POST.getlist('professional_occupation'))
        print(categories_list)
        profile.professional_occupation = ',\n'.join([str(cat) for cat in categories_list])
        print(profile.professional_occupation)
        profile.housing_loan = request.POST.get('housing_loan')
        profile.mortgage_loan = request.POST.get('mortgage_loan')
        profile.vehical_loan = request.POST.get('vehical_loan')
        profile.personal_loan = request.POST.get('personal_loan')
        profile.account_number = request.POST.get('account_number')
        profile.account_name = request.POST.get('account_name')
        profile.ifsc_code = request.POST.get('ifsc_code')
        profile.is_gst = request.POST.get('is_gst')
        if profile.is_gst == 'on':
            profile.is_gst = True
        else:
            profile.is_gst = False
        profile.gstin = request.POST.get('gstin')
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
            'categories':categories,
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
            'categories':categories,
        }
        return render(request,'user_html/dashboard_v2.html',context)
    else:
        context = {
            'user':profile,
            'categories':categories,
        }
        return render (request,'user_html/profile_v2.html',context)

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
                    mail_subject = 'Activate your Matpit Account.'
                    
                    
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



# class ServiceWorkerView(TemplateView):
#     template_name = 'serviceworker.js'
#     content_type = 'application/javascript'
#     name = 'sw.js'

#     def get_context_data(self, **kwargs):
#         return {
#             'version': version,
#             'icon_url': static('icons/aurss.512x512.png'),
#             'manifest_url': static('manifest.json'),
#             'style_url': static('style.css'),
#             'home_url': reverse('home'),
#             'offline_url': reverse('offline'),
#         }
        
# def service_worker(request):
#     response = render(request, app_settings.PWA_SERVICE_WORKER_PATH, content_type='application/javascript')
#     return response

# def getdata(request):
# 	results=CustomUser.objects.all()
# 	jsondata = serializers.serialize('json',results)
# 	return HttpResponse(jsondata)

# def base_layout(request):
# 	template='user_html/login_v2.htmll'
# 	return render(request,template)

