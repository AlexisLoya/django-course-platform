from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from courses.models import Course, Enrollment
from emails.forms import EmailForm
from django.contrib.auth import get_user_model, authenticate, login
from emails import services as email_services

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Tu cuenta ha sido creada exitosamente, {user.username}!")
            return redirect('profile')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "¡Tu perfil ha sido actualizado!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def course_detail_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    context = {
        'course': course,
        'enrolled': enrolled
    }
    return render(request, 'courses/course_detail.html', context)


def email_request_view(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email_val = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email_val)
                # Existing user, redirect to login
                request.session['email'] = email_val  # Store email for login view
                return redirect('login_with_email')
            except User.DoesNotExist:
                # New user, start verification
                email_obj, sent = email_services.start_verification_event(email_val)
                request.session['email_verification'] = email_val
                messages.success(request, f"Check your email {email_val} to verify your account!")
                return redirect('email_verification_sent')
    else:
        form = EmailForm()
    return render(request, 'accounts/email_request.html', {'form': form})



def verify_email_token_view(request, token):
    did_verify, msg, email_obj = email_services.verify_token(token)
    if not did_verify:
        messages.error(request, msg)
        return redirect('email_request')
    email = email_obj.email
    # Store email in session for registration
    request.session['registration_email'] = email
    messages.success(request, "Your email has been verified. Please complete your registration.")
    return redirect('complete_registration')


def complete_registration_view(request):
    email = request.session.get('registration_email')
    if not email:
        return redirect('email_request')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, initial={'email': email})
        if form.is_valid():
            user = form.save()
            del request.session['registration_email']
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('profile')
    else:
        form = UserRegisterForm(initial={'email': email})
    return render(request, 'accounts/complete_registration.html', {'form': form})


def set_password_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('email_request')
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            login(request, user)
            del request.session['user_id']
            messages.success(request, "Tu contraseña ha sido establecida. Has iniciado sesión.")
            return redirect('home')  # Redirige a donde corresponda
    else:
        form = SetPasswordForm(user)
    return render(request, 'accounts/set_password.html', {'form': form})


def login_with_email_view(request):
    email = request.session.get('email')
    if not email:
        return redirect('email_request')
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            del request.session['email']
            messages.success(request, "Successfully logged in.")
            return redirect('home')
        else:
            messages.error(request, "Incorrect password. Please try again.")
    return render(request, 'accounts/login_with_email.html', {'email': email})


def email_verification_sent_view(request):
    email = request.session.get('email_verification')
    if not email:
        return redirect('email_request')
    return render(request, 'accounts/email_verification_sent.html', {'email': email})