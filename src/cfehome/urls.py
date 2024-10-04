from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from emails.views import verify_email_token_view, email_token_login_view, logout_btn_hx_view
from . import views
from accounts.forms import EmailAuthenticationForm

urlpatterns = [
    path("", views.home_view),
    path("login/", auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=EmailAuthenticationForm
        ), name='login'),
    path("logout/", auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('hx/login/', email_token_login_view),
    path('hx/logout/', logout_btn_hx_view),
    path('verify/<uuid:token>/', verify_email_token_view),
    path("courses/", include("courses.urls")),
    path("admin/", admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
    path('accounts/', include('accounts.urls')),
    path('exams/', include('exams.urls', namespace='exams')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
