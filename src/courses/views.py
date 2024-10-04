import helpers
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import PublishStatus, LessonType
from .models import Course, Lesson, Enrollment, Progress
from . import services

def course_list_view(request):
    queryset = services.get_publish_courses()
    context = {
        "object_list": queryset
    }
    template_name = "courses/list.html"
    if request.htmx:
        template_name = "courses/snippets/list-display.html"
        context['queryset'] = queryset[:3]
    return render(request, template_name, context)


def course_detail_view(request, course_id=None, *args, **kwarg):
    course_obj = services.get_course_detail(course_id=course_id)
    if course_obj is None:
        raise Http404
    lessons_queryset = services.get_course_lessons(course_obj)
    enrolled = None
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user, course=course_obj).exists()
    context = {
        "object": course_obj,
        "course": course_obj,
        "lessons_queryset": lessons_queryset,
        "enrolled": enrolled,
    }
    return render(request, "courses/detail.html", context)

def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    course = get_object_or_404(Course, public_id=course_id)
    
    # Si no se proporciona lesson_id, redirigir a la última lección vista o a la primera lección
    if lesson_id is None:
        if request.user.is_authenticated:
            # Obtener la última lección completada por el usuario
            last_progress = Progress.objects.filter(
                user=request.user, 
                lesson__course=course, 
                completed=True
            ).order_by('-timestamp').first()
            if last_progress:
                return redirect('lesson_detail', course_id=course_id, lesson_id=last_progress.lesson.public_id)
            else:
                # Redirigir a la primera lección del curso
                first_lesson = Lesson.objects.filter(course=course).order_by('order').first()
                if first_lesson:
                    return redirect('lesson_detail', course_id=course_id, lesson_id=first_lesson.public_id)
                else:
                    raise Http404("No se encontraron lecciones para este curso.")
        else:
            # Usuario no autenticado, redirigir al inicio de sesión
            messages.info(request, "Debes iniciar sesión para acceder a las lecciones.")
            request.session['next_url'] = request.path
            return redirect('login')

    # Obtener el objeto de la lección
    lesson_obj = services.get_lesson_detail(
        course_id=course_id,
        lesson_id=lesson_id
    )
    if lesson_obj is None:
        raise Http404

    # Verificar si la lección requiere autenticación
    if lesson_obj.requires_email and not request.user.is_authenticated:
        messages.info(request, "Debes iniciar sesión para acceder a esta lección.")
        request.session['next_url'] = request.path
        return redirect('login')

    # Obtener todas las lecciones del curso
    lessons = Lesson.objects.filter(course=lesson_obj.course).order_by('order')

    # Obtener las lecciones completadas por el usuario
    if request.user.is_authenticated:
        completed_lessons = Progress.objects.filter(
            user=request.user,
            lesson__in=lessons, 
            completed=True
        ).values_list('lesson_id', flat=True)
    else:
        completed_lessons = []

    context = {
        "object": lesson_obj,
        "lessons": lessons,
        "completed_lessons": completed_lessons,
    }

    # Determinar el template a utilizar
    template_name = "courses/lesson.html"
    if not lesson_obj.is_coming_soon and lesson_obj.status == PublishStatus.PUBLISHED:
        if lesson_obj.lesson_type == LessonType.VIDEO:
            if lesson_obj.has_video:
                video_embed_html = helpers.get_cloudinary_video_object(
                    lesson_obj,
                    field_name='video',
                    as_html=True,
                    width=1250
                )
                context['video_embed'] = video_embed_html
            else:
                template_name = "courses/lesson-coming-soon.html"
        elif lesson_obj.lesson_type == LessonType.BLOG:
            pass  # No es necesario cambiar el template
        else:
            template_name = "courses/lesson-coming-soon.html"
    else:
        template_name = "courses/lesson-coming-soon.html"

    # Marcar la lección como completada por el usuario
    if request.user.is_authenticated:
        lesson_obj.mark_as_completed(request.user)

    return render(request, template_name, context)

@login_required
def enroll_in_course(request, course_id=None, *args, **kwargs):
    course = get_object_or_404(Course, public_id=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"Te has inscrito en {course.title}")
    return redirect('course_detail', course_id=course.public_id)
