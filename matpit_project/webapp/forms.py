from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import FormActions,AppendedText, PrependedText, FormActions
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category
from django.forms import Select


from django import forms
import os
User = get_user_model()
import copy



class UserAdminCreationForm(forms.ModelForm):
    # ROLE = (('ADMIN','ADMIN'), ('BH', 'BH'),('AFM','AFM'),('AF','AF') ,('AM', 'AM'), ('BO', 'BO'), ('ZSM', 'ZSM'), ('RSM', 'RSM'), ('ASM', 'ASM'), ('SM', 'SM'), ('RM', 'RM'), ('DSA', 'DSA'), ('C', 'CONNECTOR'), )
    
    helper = FormHelper()
    helper.form_method == 'POST'
    
    helper.layout = Layout()
    
    first_name = forms.CharField(max_length=100,
                           widget= forms.TextInput
                           (attrs={'placeholder':'First Name'}))
    last_name = forms.CharField(max_length=100,
                           widget= forms.TextInput
                           (attrs={'placeholder':'Last Name'}))
    phone = forms.CharField(max_length=12,
                           widget= forms.NumberInput
                           (attrs={'placeholder':'Phone Number'}))
    email = forms.EmailField(max_length=36,
                           widget= forms.EmailInput
                           (attrs={'placeholder':'Email Field'}))
    role = forms.ChoiceField(widget=forms.Select())
    
    helper.form_show_labels = False
    
    
    def __init__(self,*args, **kwargs):  
        # import pdb; pdb.set_trace()      
        self.request = kwargs.pop('request',None)
        x = self.request.user.role
        print(x)
        count = 0
        dropdown_list = []
        if x =='ADMIN':
            dropdown_list = ['ADMIN','ACCOUNT','BO','ZSM','RSM','ASM','SM','RM','DSA','CONNECTOR','BH','AFM','AF']
        if x in ['BH','AFM','AF']:
            dropdown_list = ['BH','AFM','AF']
        if x in ['ZSM','RSM','ASM','SM','RM','DSA','CONNECTOR']:
            dropdown_list = ['ZSM','RSM','ASM','SM','RM','DSA','CONNECTOR']
        dropdown_list = dropdown_list[::-1]
        # print(dropdown_list)
        for i in range(0,len(dropdown_list)):
            if x==dropdown_list[i]:
                count = count+i
        # print(count)
        dropdown = []
        for i in range(0,count):
            dropdown.append(dropdown_list[i])
        dropdown.reverse()
        print(dropdown)
        dropdown2 = copy.deepcopy(dropdown)
        print(dropdown2)
        ROLE = tuple(zip(dropdown,dropdown2))
        print(ROLE)

        

        super(UserAdminCreationForm, self).__init__(*args, **kwargs)
        self.fields['role'].choices = tuple(zip(dropdown,dropdown2))
        

    
    def clean(self):
        print(self.request.user.role)
        
    class Meta:
        model = User
        fields = ['first_name','last_name','email','phone','role']
      
    # def save(self, commit=True):
    #     self.request.user.role = self.cleaned_data['role']
    #     if commit:
    #         self.user.save()
    #     return self.user


class UserProfileCreationForm(forms.ModelForm): 

    helper = FormHelper()
    professional_occupation = forms.ModelMultipleChoiceField(queryset=Category.objects.all(),widget=forms.CheckboxSelectMultiple,required=False)
    # housing_loan  = forms.CharField(max_length=100,
    #                        widget= forms.NumberInput
    #                        (attrs={'placeholder':'Housing Loan'}))
    # mortgage_loan = forms.CharField(max_length=100,
    #                        widget= forms.NumberInput
    #                        (attrs={'placeholder':'Mortgage Loan'})) 
    # vehical_loan = forms.CharField(max_length=100,
    #                        widget= forms.NumberInput
    #                        (attrs={'placeholder':'Vehical Loan'})) 
    # personal_loan = forms.CharField(max_length=100,
    #                        widget= forms.NumberInput
    #                        (attrs={'placeholder':'Personal Loan'}))
    

    class Meta:
        model = User
        fields = [ 'professional_occupation']
        # widget = {
        #     'account_number' : forms.TextInput(attrs={'class':'form-control','type':'text','id':'account_numberid'}),
        #     'account_name' : forms.TextInput(attrs={'class':'form-control','type':'text','id':'account_nameid'}),
        #     'ifsc_code' : forms.TextInput(attrs={'class':'form-control', 'type':'text', 'id':'ifsc_codeid'}),
        #     'terms_condition' : forms.CheckboxInput(attrs={'class': 'required checkbox form-control'}),   

        #     }

# class ImageUploadForm(forms.ModelForm):

#     class Meta:
#         model = Lead
#         fields = ['pancard_image','adhaar_image']

# class YourLeadUploadImageForm(forms.ModelForm):
#     class Meta:
#         model = Lead
#         fields = ['senction_letter']

class UserVerificationForm(forms.ModelForm):
    # is_verified = forms.BooleanField(required=True,initial=False,label='Verify')
    class Meta:
        model = User
        fields = ['phone','is_verified']




class UserRejectionForm(forms.ModelForm):
   
    class Meta:
        model = User
        fields = ['is_rejected','rejection_reason']
        widget = {
            'is_rejected':  forms.CheckboxInput(attrs={'class': 'required checkbox form-control'}),
            'rejection_reason': forms.TextInput(attrs={'class':'form-control','type':'text','id':'rejection_reasonid'})
            }


