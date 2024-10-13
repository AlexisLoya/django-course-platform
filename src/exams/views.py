from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from courses.models import Course, Enrollment
from .models import Exam, Question, Choice, ExamAttempt, UserAnswer
from .forms import ExamForm, QuestionForm, ChoiceFormSet, UserAnswerForm

@login_required
def create_exam_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, creator=request.user)
    if hasattr(course, 'exam'):
        return redirect('exam_detail', exam_id=course.exam.id)
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.course = course
            exam.created_by = request.user
            exam.save()
            return redirect('add_question', exam_id=exam.id)
    else:
        form = ExamForm()
    return render(request, 'courses/create_exam.html', {'form': form, 'course': course})


@login_required
def add_question_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)
        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save(commit=False)
            question.exam = exam
            question.save()
            choices = choice_formset.save(commit=False)
            for choice in choices:
                choice.question = question
                choice.save()
            return redirect('add_question', exam_id=exam.id)
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet()
    return render(request, 'courses/add_question.html', {
        'exam': exam,
        'question_form': question_form,
        'choice_formset': choice_formset
    })

@login_required
def exam_detail_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    return render(request, 'courses/exam_detail.html', {'exam': exam, 'questions': questions})

@login_required
def take_exam_view(request, exam_public_id):
    exam = get_object_or_404(Exam, public_id=exam_public_id)
    course = exam.course

    # Check if the user has completed 75% of the course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    progress = enrollment.progress  # Assuming you track progress in Enrollment model
    if progress < 70:
        return redirect('exams:exam_not_allowed', course_id=course.public_id)

    # Check if the user has already passed the exam
    if ExamAttempt.objects.filter(exam=exam, user=request.user, passed=True).exists():
        print("Ya has aprobado este examen y no puedes volver a intentarlo.")
        return redirect('courses:course_detail', course_id=course.public_id)

    # Check if the user has finished the course
    if enrollment.progress == 100:
        print("Ya has completado este curso y no puedes volver a tomar el examen.")
        return redirect('courses:course_detail', course_id=course.public_id)

    # Limit the number of attempts per day
    today = timezone.now().date()
    attempts_today = ExamAttempt.objects.filter(
        exam=exam,
        user=request.user,
        date_started__date=today
    ).count()
    if attempts_today >= exam.tries_allowed_per_day:
        print(f"Has alcanzado el número máximo de intentos permitidos por día ({exam.tries_allowed_per_day}).")
        return redirect('courses:course_detail', course_id=course.public_id)

    if request.method == 'POST':
        # Enforce time limit
        attempt_id = request.session.get('exam_attempt_id')
        if not attempt_id:
            print("No se encontró una sesión de examen válida.")
            return redirect('courses:course_detail', course_id=course.public_id)

        attempt = get_object_or_404(ExamAttempt, id=attempt_id, user=request.user)
        time_elapsed = (timezone.now() - attempt.date_started).total_seconds() / 60  # in minutes

        if time_elapsed > exam.time_limit:
            print("El tiempo límite del examen ha expirado.")
            attempt.date_ended = timezone.now()
            attempt.save()
            del request.session['exam_attempt_id']
            return redirect('exams:exam_result', attempt_public_id=attempt.public_id)

        total_questions = exam.questions.count()
        correct_answers = 0

        for question in exam.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if not selected_choice_id:
                continue
            selected_choice = Choice.objects.get(id=selected_choice_id)
            user_answer = UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_choice=selected_choice
            )
            user_answer.check_if_correct()
            if user_answer.is_correct:
                correct_answers += 1

        score = (correct_answers / total_questions) * 100
        attempt.score = score
        attempt.passed = score >= exam.passing_percentage
        attempt.date_ended = timezone.now()
        attempt.save()

        del request.session['exam_attempt_id']
        return redirect('exams:exam_result', attempt_public_id=attempt.public_id)

    else:
        # Start the exam attempt
        attempt = ExamAttempt.objects.create(exam=exam, user=request.user)
        request.session['exam_attempt_id'] = attempt.id

        questions = exam.questions.prefetch_related('choices')
        return render(request, 'exams/take_exam.html', {
            'exam': exam,
            'questions': questions,
            'attempt': attempt,
            'time_limit': exam.time_limit,
        })


@login_required
def exam_result_view(request, attempt_public_id):
    attempt = get_object_or_404(ExamAttempt, public_id=attempt_public_id, user=request.user)
    return render(request, 'exams/exam_result.html', {'attempt': attempt})

@login_required
def exam_not_allowed_view(request, course_id):
    course = get_object_or_404(Course, public_id=course_id)
    progress = Enrollment.objects.get(user=request.user, course=course).progress
    print(f'progress: {progress}')
    return render(request, 'exams/exam_not_allowed.html', {'course': course, 'progress': progress})