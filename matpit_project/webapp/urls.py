from django.urls import path ,include
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('',views.login,name="login"),
    path('register/',views.register,name="register"),
    path('password_change/', views.change_password,name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),{'template_name': '/password_change_done.htm' ,'post_change_redirect': 'password_change_done'}, name='password_change_done'),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('bodashboard/',views.bodashboard,name="bodashboard"),
    path("profile/",views.profile,name="profile"),
    path('yourlead/',views.yourlead,name='yourlead'),
    path('MIC/',views.mic_dashboard,name='micdashboard'),
    path('rera/',views.rera_consultancy,name="rera"),
    path('reports/',views.reports,name='reports'),
    path('lead_verification/',views.lead_verify,name='verify_lead'),
    path('account/',views.accountdashboard,name='account'),
    path('logout/',views.logout,name="logout"),
    path("reset_password/", views.password_reset_request, name="reset_password"),
    path('reset_password_sent/',
    auth_views.PasswordResetDoneView.as_view(template_name='email_template/password_rest_sent.htm'),
    name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name = 'email_template/password_reset_form.htm'),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='email_template/password_reset_done.htm'),name="password_reset_complete"),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('usermanager/',views.usermanagement,name='usermanager'),
    path('service-worker.js',TemplateView.as_view(template_name="serviceworker.js",content_type='application/javascript',), name='service-worker.js'),

] 
