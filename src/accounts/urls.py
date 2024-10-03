from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.email_request_view, name='register'),  # Adjusted to use email_request_view
    path('email-request/', views.email_request_view, name='email_request'),
    path('login-with-email/', views.login_with_email_view, name='login_with_email'),
    path('complete-registration/', views.complete_registration_view, name='complete_registration'),
    path('verify-email/<uuid:token>/', views.verify_email_token_view, name='verify_email_token'),
    path('email-verification-sent/', views.email_verification_sent_view, name='email_verification_sent'),
    path('profile/', views.profile, name='profile'),
]