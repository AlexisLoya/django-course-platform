import helpers
from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Lesson, Enrollment, Progress, Exam, Question, Choice, ExamAttempt, StudentAnswer
from .forms import LessonInlineForm

class LessonInline(admin.StackedInline):
    model = Lesson
    form = LessonInlineForm
    readonly_fields = [
        'public_id', 
        'updated', 
        'display_image',
        'display_video',
    ]
    extra = 0
    
    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/jquery.init.js',
            'js/lesson_inline.js',
        )
        
    def display_image(self, obj):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='thumbnail',
            width=200
        )
        return format_html(f'<img src="{url}" />')

    display_image.short_description = "Current Image"

    def display_video(self, obj):
        video_embed_html = helpers.get_cloudinary_video_object(
            obj, 
            field_name='video',
            as_html=True,
            width=550
        )
        return video_embed_html

    display_video.short_description = "Current Video"

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ['user', 'course', 'enrolled_at']

class ProgressInline(admin.TabularInline):
    model = Progress
    extra = 0
    readonly_fields = ['user', 'lesson', 'completed', 'timestamp']

    def progress_percentage(self, obj):
        total_lessons = Lesson.objects.filter(course=obj.lesson.course).count()
        completed_lessons = Progress.objects.filter(user=obj.user, lesson__course=obj.lesson.course, completed=True).count()
        return f"{(completed_lessons / total_lessons) * 100:.2f}%"

    progress_percentage.short_description = "Progress"

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, EnrollmentInline]
    list_display = ['title', 'status', 'access', 'enrollment_count']
    list_filter = ['status', 'access']
    fields = ['public_id', 'title', 'description', 'status', 'image', 'access', 'display_image']
    readonly_fields = ['public_id', 'display_image']

    def display_image(self, obj):
        url = helpers.get_cloudinary_image_object(
            obj, 
            field_name='image',
            width=200
        )
        return format_html(f'<img src="{url}" />')

    display_image.short_description = "Current Image"

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrolled_at']
    list_filter = ['course', 'enrolled_at']
    search_fields = ['user__username', 'course__title']
    
@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'completed', 'timestamp']
    list_filter = ['completed', 'timestamp']
    search_fields = ['user__username', 'lesson__title']
    

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Exam)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ExamAttempt)
admin.site.register(StudentAnswer)