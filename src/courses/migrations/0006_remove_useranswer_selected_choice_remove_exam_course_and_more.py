# Generated by Django 5.0 on 2024-10-04 03:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_course_creator_enrollment_progress_exam_examattempt_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useranswer',
            name='selected_choice',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='course',
        ),
        migrations.RemoveField(
            model_name='exam',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='question',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='examattempt',
            name='exam',
        ),
        migrations.RemoveField(
            model_name='examattempt',
            name='user',
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='attempt',
        ),
        migrations.RemoveField(
            model_name='useranswer',
            name='question',
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
        migrations.DeleteModel(
            name='Exam',
        ),
        migrations.DeleteModel(
            name='ExamAttempt',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='UserAnswer',
        ),
    ]
