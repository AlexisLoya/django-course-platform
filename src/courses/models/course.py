import uuid
import helpers
from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from courses.utils import AccessRequirement, PublishStatus, LessonType
from django.core.exceptions import ValidationError
from django_summernote.fields import SummernoteTextField
from django.conf import settings


helpers.cloudinary_init()

def handle_upload(instance, filename):
    return f"{filename}"

def generate_public_id(instance, *args, **kwargs):
    title = instance.title
    unique_id = str(uuid.uuid4()).replace("-", "")
    if not title:
        return unique_id
    slug = slugify(title)
    unique_id_short = unique_id[:5]
    return f"{slug}-{unique_id_short}"


def get_public_id_prefix(instance, *args, **kwargs):
    if hasattr(instance, 'path'):
        path = instance.path
        if path.startswith("/"):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]
        return path
    public_id = instance.public_id
    model_class = instance.__class__
    model_name = model_class.__name__
    model_name_slug = slugify(model_name)
    if not public_id:
        return f"{model_name_slug}"
    return f"{model_name_slug}/{public_id}"

def get_display_name(instance, *args, **kwargs):
    if hasattr(instance, 'get_display_name'):
        return instance.get_display_name()
    elif hasattr(instance, 'title'):
        return instance.title
    model_class = instance.__class__
    model_name = model_class.__name__
    return f"{model_name} Upload"


class Course(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    public_id = models.CharField(max_length=130, blank=True, null=True, db_index=True)
    image = CloudinaryField(
        "image", 
        null=True, 
        public_id_prefix=get_public_id_prefix,
        display_name=get_display_name,
        tags=["course", "thumbnail"]
    )
    access = models.CharField(
        max_length=5, 
        choices=AccessRequirement.choices,
        default=AccessRequirement.EMAIL_REQUIRED
    )
    status = models.CharField(
        max_length=10, 
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT
        )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # before save
        if self.public_id == "" or self.public_id is None:
            self.public_id = generate_public_id(self)
        super().save(*args, **kwargs)
        # after save

    def get_absolute_url(self):
        return self.path
    
    @property
    def path(self):
        return f"/courses/{self.public_id}"

    @property
    def enrollment_count(self):
        return self.enrollments.count()

    def get_display_name(self):
        return f"{self.title} - Course"

    def get_thumbnail(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self, 
            field_name='image',
            as_html=False,
            width=382
        )

    def get_display_image(self):
        if not self.image:
            return None
        return helpers.get_cloudinary_image_object(
            self, 
            field_name='image',
            as_html=False,
            width=750
        )

    @property
    def is_published(self):
        return self.status == PublishStatus.PUBLISHED
    

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
    