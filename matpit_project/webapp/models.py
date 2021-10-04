from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group
from django.db.models.deletion import CASCADE
from django.db.models.fields import related
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator,MinValueValidator,MaxLengthValidator,RegexValidator
import uuid 
import base64
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, phone,email, password=None, **extra_fields):
        """Create and save a User with the given phone and password."""
        if not phone:
            raise ValueError('The given phone must be set')
        user = self.model(phone=phone, **extra_fields)
        # group = Group.objects.all()
        # user.groups.add(group)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,phone,  email,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self,phone,  email,password=None, **extra_fields):
        """Create and save a SuperUser with the given phone and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone,email,password, **extra_fields)
 
class Category(models.Model):
    '''
    Creating a new model to assign Category to category fields in the Content
    '''
    name = models.CharField(max_length=200,unique=True)
    def __str__(self):
        return self.name




class CustomUser(AbstractUser):
    ROLE = (('ADMIN','ADMIN'), ('BH', 'BH'),('AFM','AFM'),('AF','AF') ,('AM', 'AM'),('ACCOUNT','ACCOUNT') ,('BO', 'BO'), ('ZSM', 'ZSM'), ('RSM', 'RSM'), ('ASM', 'ASM'), ('SM', 'SM'), ('RM', 'RM'), ('DSA', 'DSA'), ('CONNECTOR', 'CONNECTOR'), )
    username = None 
    first_name =models.CharField(max_length=100,blank=True,null=True) 
    last_name = models.CharField(max_length=100,blank=True,null=True) 
    email = models.EmailField(max_length=250,unique=False, default='')
    father_name = models.CharField(max_length=100,blank=True,null=True) 
    phone = models.CharField(max_length=10,validators=[RegexValidator(r'^\d{1,10}$')],unique=True, default='') 
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 
    referral_code = models.CharField(max_length=32, blank=True, null=True ) 
    referred_by = models.CharField(max_length=100,null=True,blank=True,unique=False) 
    manager = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE,related_name='refer')
    role = models.CharField(max_length=10,choices=ROLE)
    password_update = models.BooleanField(default=False)  
    profile_update = models.BooleanField(default=False)
    profile_created = models.DateTimeField(auto_now=True,blank=True,null=True) 
    is_verified = models.BooleanField(default=False) 
    verified_by = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE,related_name='verify')
    rejected_by = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE,related_name='reject')
    verified_at = models.DateTimeField(auto_now=True,blank=True,null=True) 
    is_suspended = models.BooleanField(default=False) 
    suspended_at = models.DateTimeField(auto_now=True,blank=True,null=True)  
    is_rejected = models.BooleanField(default=False) 
    rejected_at = models.DateTimeField(auto_now=True,blank=True,null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    account_number = models.CharField(max_length=100,blank=True,null=True,unique=True)
    account_name = models.CharField(max_length=100,blank=True,null=True)
    ifsc_code = models.CharField(max_length=32, unique=True, blank=True,null=True)
    image = models.ImageField(upload_to='images/',default='images/demouser_jUEee1U.jpeg',blank=True,null=True)
    adhaar_image = models.ImageField(upload_to='aadhar_pics/',blank=True,null=True)
    pancard_image = models.ImageField(upload_to='pancard_pics/',blank=True,null=True)
    cancelled_cheque_image = models.ImageField(upload_to='cheque_pics/',blank=True,null=True)
    professional_occupation = models.TextField(blank=True,null=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=6, validators=[RegexValidator(r'^\d{1,10}$')],null=True, blank=True)
    terms_condition = models.BooleanField(default=False)
    active_user = models.BooleanField(
        help_text='Whether the user is active or not',
        default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()


class ServiceType(models.Model):
    name = models.CharField(max_length=200,unique=True)
    def __str__(self):
        return self.name

class RealEstate(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return self.name

class StartUp(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return self.name
class Taxation(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True)  
    def __str__(self):
        return self.name
class Legal(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return self.name

class Tradmark(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return self.name

class Other(models.Model):
    name = models.CharField(max_length=200,unique=True)
    created = models.DateTimeField(auto_now_add=True) 
    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=200,unique=True)
    def __str__(self):
        return self.name




class Service(models.Model):
    
    ######################## Service #############################################
    service_type = models.CharField(max_length=100,blank=True,null=True)
    service_sub_type = models.CharField(max_length=100,blank=True,null=True)
    service_amount = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True) 
    created_by = models.ForeignKey(CustomUser,related_name='service_user',null=True, blank=True,on_delete=models.CASCADE)

    ############################## service Updated ################################
    service_update = models.BooleanField(default=False)

    ########################## For the Account and MIS Report #######################################################
    payout = models.CharField(max_length=100,blank=True,null=True)
    payout_recieved_percentage = models.CharField(max_length=100,blank=True,null=True)
    payout_paid = models.CharField(max_length=100,blank=True,null=True)
    payout_recieved_date = models.DateTimeField(null=True,blank=True)
    payout_recieved = models.CharField(max_length=100,blank=True,null=True)
    incentives = models.CharField(max_length=100,blank=True,null=True)
    net_revenue = models.CharField(max_length=100,blank=True,null=True)
    incentives_percentage = models.CharField(max_length=100,blank=True,null=True)
    #######################  Verification Process #########################################################
    verification_pending = models.BooleanField(default=False)
    verification_approved = models.BooleanField(default=False)
    verification_rejected = models.BooleanField(default=False)
    verification_rejection_reason = models.TextField(blank=True, null=True)
    verification_approved_by = models.ForeignKey(CustomUser, null=True, blank=True,on_delete=models.CASCADE,related_name='verification_approve')
    verification_rejected_by = models.ForeignKey(CustomUser, null=True, blank=True,on_delete=models.CASCADE,related_name='verification_reject')
    verification_approved_at = models.DateTimeField(auto_now=True,blank=True,null=True) 
    verification_rejected_at = models.DateTimeField(auto_now=True,blank=True,null=True) 

    def __str__(self):
        return str(self.id)

class Notification(models.Model):
    service = models.ForeignKey(Service,related_name='notify_service',on_delete=CASCADE)
    notified_user = models.CharField(max_length=100,blank=True,null=True)
    read_chat_notification = models.BooleanField(default=False)
    read_service_notification = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.notified_user)
    


class Comment(models.Model):
    service = models.ForeignKey(Service,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='customer')
    message = models.TextField() 
    attachments = models.FileField(upload_to='attachments/',blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True) 
    updated = models.DateTimeField(auto_now=True) 

    class Meta: 
        ordering = ('created',) 

    def __str__(self): 
        return 'Comment by {} on {}'.format(self.user.first_name, self.service)