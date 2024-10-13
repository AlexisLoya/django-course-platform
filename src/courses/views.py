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

def get_last_completed_lesson(user, course):
    return Progress.get_last_completed_lesson(user=user, course=course)

def get_first_lesson(course):
    return Lesson.objects.filter(course=course).order_by('order').first()

def redirect_to_lesson(course_id, lesson):
    if lesson:
        return redirect('lesson_detail', course_id=course_id, lesson_id=lesson.public_id)
    else:
        raise Http404("No se encontraron lecciones para este curso.")

def handle_authentication(request):
    if not request.user.is_authenticated:
        messages.info(request, "Debes iniciar sesión para acceder a las lecciones.")
        request.session['next_url'] = request.path
        return redirect('login')

def get_completed_lessons(user, lessons):
    if user.is_authenticated:
        return Progress.objects.filter(user=user, lesson__in=lessons, completed=True).values_list('lesson_id', flat=True)
    return []

def get_template_name(lesson_obj):
    if not lesson_obj.is_coming_soon and lesson_obj.status == PublishStatus.PUBLISHED:
        if lesson_obj.lesson_type == LessonType.VIDEO:
            if lesson_obj.has_video:
                return "courses/lesson.html"
            else:
                return "courses/lesson-coming-soon.html"
        elif lesson_obj.lesson_type == LessonType.BLOG:
            return "courses/lesson.html"
        else:
            return "courses/lesson-coming-soon.html"
    return "courses/lesson-coming-soon.html"


def lesson_detail_view(request, course_id=None, lesson_id=None, *args, **kwargs):
    course = get_object_or_404(Course, public_id=course_id)
    
    if lesson_id is None:
        if request.user.is_authenticated:
            last_progress = get_last_completed_lesson(request.user, course)
            if last_progress:
                return redirect_to_lesson(course_id, last_progress.lesson)
            else:
                first_lesson = get_first_lesson(course)
                return redirect_to_lesson(course_id, first_lesson)
        else:
            return handle_authentication(request)

    lesson_obj = services.get_lesson_detail(course_id=course_id, lesson_id=lesson_id)
    if lesson_obj is None:
        raise Http404

    if lesson_obj.requires_email and not request.user.is_authenticated:
        return handle_authentication(request)

    lessons = Lesson.objects.filter(course=lesson_obj.course).order_by('order')
    completed_lessons = get_completed_lessons(request.user, lessons)

    context = {
        "object": lesson_obj,
        "lessons": lessons,
        "completed_lessons": completed_lessons,
    }

    template_name = get_template_name(lesson_obj)
    if template_name == "courses/lesson.html" and lesson_obj.lesson_type == LessonType.VIDEO and lesson_obj.has_video:
        video_embed_html = helpers.get_cloudinary_video_object(
            lesson_obj,
            field_name='video',
            as_html=True,
            width=1250
        )
        context['video_embed'] = video_embed_html

    if request.user.is_authenticated:
        lesson_obj.mark_as_completed(request.user)
        enrollment, _ = Enrollment.objects.get_or_create(user=request.user, course=course)
        enrollment.progress = enrollment.calculate_course_progress()
        enrollment.save()

    return render(request, template_name, context)

@login_required
def enroll_in_course(request, course_id=None, *args, **kwargs):
    course = get_object_or_404(Course, public_id=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"Te has inscrito en {course.title}")
    return redirect('courses:course_detail', course_id=course.public_id)
