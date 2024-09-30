from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from courses.models import Course, Enrollment

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