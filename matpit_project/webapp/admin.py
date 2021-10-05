from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .models import Category, Service, CustomUser,Comment,Notification,ServiceType,RealEstate,StartUp,Taxation,Legal,Tradmark,Other
# class CustomUserAdmin(UserAdmin):
#     """Define admin model for custom User model with no user field."""
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('phone', 'first_name','last_name','role','pancard_image','adhaar_image','cancelled_cheque_image','password_update','profile_update','is_verified','is_rejected','rejection_reason','is_suspended','referral_code','referred_by','housing_loan','mortgage_loan','vehical_loan','personal_loan')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('phone', 'email','referral_code','role','account_number','account_name','ifsc_code','professional_occupation','state','pincode','password1', 'password2'),
#         }),
#     )
#     list_display = ( 'phone','email' ,'first_name', 'last_name','role','referral_code','referred_by','is_verified' ,'is_rejected','is_suspended','profile_update','password_update')
#     search_fields = ('email', 'phone', 'first_name','last_name')
#     ordering = ('phone',)


# admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Service)
admin.site.register(ServiceType)
admin.site.register(RealEstate)
admin.site.register(StartUp)
admin.site.register(Taxation)
admin.site.register(Legal)
admin.site.register(Tradmark)
admin.site.register(Other)
admin.site.register(Comment)
admin.site.register(Notification)

