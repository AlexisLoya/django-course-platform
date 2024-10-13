from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path("", views.course_list_view),
    path("<slug:course_id>/lessons/<slug:lesson_id>/", views.lesson_detail_view),
    path("<slug:course_id>/", views.course_detail_view, name='course_detail'),
    path('<slug:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),
]
