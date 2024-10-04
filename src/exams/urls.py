from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('<str:exam_public_id>/take/', views.take_exam_view, name='take_exam'),
    path('result/<str:attempt_public_id>/', views.exam_result_view, name='exam_result'),
]