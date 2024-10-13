import helpers
from django.db import models
from django.conf import settings
from .course import Course, generate_public_id, get_public_id_prefix, get_display_name
from courses.utils import AccessRequirement, PublishStatus, LessonType
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from django_summernote.fields import SummernoteTextField



"""
- Lessons
    - Title
    - Description
    - Video
    - Status: Published, Coming Soon, Draft
"""

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # course_id 
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    lesson_type = models.CharField(
        max_length=10,
        choices=LessonType.choices,
        default=LessonType.VIDEO
    )
    content = SummernoteTextField(default='', help_text="Content for blog/text lessons")
    thumbnail = CloudinaryField("image", 
                public_id_prefix=get_public_id_prefix,
                display_name=get_display_name,
                tags = ['thumbnail', 'lesson'],
                blank=True, null=True)
    video = CloudinaryField("video", 
            public_id_prefix=get_public_id_prefix,
            display_name=get_display_name,                
            blank=True, 
            null=True, 
            type='private',
            tags = ['video', 'lesson'],
            resource_type='video')
    order = models.IntegerField(default=1)
    can_preview = models.BooleanField(default=False, help_text="If user does not have access to course, can they see this?")
    status = models.CharField(
        max_length=10, 
        choices=PublishStatus.choices,
        default=PublishStatus.PUBLISHED
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-updated']
        unique_together = ('course', 'order')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return self.path

    @property
    def path(self):
        course_path = self.course.path
        if course_path.endswith("/"):
            course_path = course_path[:-1]
        return f"{course_path}/lessons/{self.public_id}"

    @property
    def requires_email(self):
        return self.course.access == AccessRequirement.EMAIL_REQUIRED

    def get_display_name(self):
        return f"{self.title} - {self.course.get_display_name()}"

    @property
    def is_coming_soon(self):
        return self.status == PublishStatus.COMING_SOON
    
    @property
    def has_video(self):
        return self.video is not None
    
    def get_thumbnail(self):
        width = 382
        if self.lesson_type == LessonType.VIDEO and self.thumbnail:
            return helpers.get_cloudinary_image_object(
                self, 
                field_name='thumbnail',
                format='jpg',
                as_html=False,
                width=width
            )
        elif self.lesson_type == LessonType.VIDEO and self.video:
            return helpers.get_cloudinary_image_object(
            self, 
            field_name='video',
            format='jpg',
            as_html=False,
            width=width
        )
        return None
    
    def mark_as_completed(self, user):
        progress, created = Progress.objects.get_or_create(user=user, lesson=self)
        progress.completed = True
        progress.save()

    def is_completed_by(self, user):
        return Progress.objects.filter(user=user, lesson=self, completed=True).exists()
    
    def clean(self):
        super().clean()
        if Lesson.objects.filter(course=self.course, order=self.order).exclude(pk=self.pk).exists():
            raise ValidationError(f"already exists a lesson with order {self.order} for this course.")
        if self.lesson_type == LessonType.VIDEO and not self.video:
            raise ValidationError("Video field is required for video lessons.")
        if self.lesson_type == LessonType.BLOG and not self.content:
            raise ValidationError("Content field is required for blog/text lessons.")
        
class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name='progress', on_delete=models.CASCADE)

    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Completed' if self.completed else 'Incomplete'}"
    
    @staticmethod
    def get_last_completed_lesson(user, course):
        return Progress.objects.filter(
            user=user,
            lesson__course=course,
            completed=True
        ).order_by('-timestamp').first()
