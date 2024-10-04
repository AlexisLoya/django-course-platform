from django.urls import path

from . import views

urlpatterns = [
    path("", views.course_list_view),
    path("<slug:course_id>/lessons/<slug:lesson_id>/", views.lesson_detail_view),
    path("<slug:course_id>/", views.course_detail_view, name='course_detail'),
    path('<slug:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('<slug:course_id>/create-exam/', views.create_exam_view, name='create_exam'),
    path('exam/<int:exam_id>/add-question/', views.add_question_view, name='add_question'),
    path('exam/<int:exam_id>/', views.exam_detail_view, name='exam_detail'),
    path('exam/<int:exam_id>/take/', views.take_exam_view, name='take_exam'),
    path('exam/result/<int:attempt_id>/', views.exam_result_view, name='exam_result'),
]
