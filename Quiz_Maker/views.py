import secrets
import time

from django.urls import reverse

from .models import Quiz

from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.html import escape
from datetime import datetime
from .models import Quiz, Question, Answer, Assignment, Course
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# @csrf_protect
def dashboard_view(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        # Redirect the user to the login page if not authenticated
        return redirect('login_view')

    # Render the dashboard template
    return render(request, 'dashboard.html')


def create_quiz(request):
    if request.method == 'POST':
        # Get the name, subject, and grade level from the request
        name = request.POST['name']
        subject = request.POST['subject']
        grade_level = request.POST['grade_level']
        num_ques = request.POST['num_ques']

        # Create a context object with the name, subject, grade level, and number of questions
        context = {
            'name': name,
            'subject': subject,
            'grade_level': grade_level,
            'num_ques': num_ques
        }

        # Render the create_quiz.html template using the context
        return render(request, 'create_question.html', context)
    else:
        # Render the create_question.html template
        return render(request, 'create_quiz.html')


def create_question(request):
    # Use the context provided by the create_quiz view
    context = request.POST

    if request.method == 'POST':
        # Get the quiz_id and number of questions from the context
        quiz_id = context['quiz_id']
        num_ques = context['num_ques']

        # Create the specified number of questions for the quiz
        for i in range(num_ques):
            # Get the text and duration for each question
            text = context[f'text_{i}']
            duration = context[f'duration_{i}']

            # Create a new question instance
            question = Question.objects.create(quiz_id=quiz_id, text=text, duration=duration)

            # Create the correct answer for this question
            correct_answer_text = context[f'correct_answer_{i}']
            correct_answer = Answer.objects.create(
                question=question,
                text=correct_answer_text,
                is_correct=True
            )

            # Create the incorrect answers for this question
            for j in range(3):
                incorrect_answer_text = context[f'incorrect_answer_{i}_{j}']
                incorrect_answer = Answer.objects.create(
                    question=question,
                    text=incorrect_answer_text,
                    is_correct=False
                )

        return render(request, 'quiz_create_success.html')
    else:
        # Pass the context to the create_question.html template
        return render(request, 'create_question.html', context)


def create_answer(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        text = request.POST['text']
        is_correct = request.POST['is_correct']

        answer = Answer.objects.create(question_id=question_id, text=text, is_correct=is_correct)

        return HttpResponse('Answer created successfully!')
    else:
        return render(request, 'create_answer.html')


def quiz_edit(request):
    pass


def take_quiz(request):
    if request.method == 'POST':
        quiz_id = request.POST['quiz_id']
        answers = request.POST['answers']

        # get quiz and its questions and answers
        quiz = Quiz.objects.get(id=quiz_id)
        questions = quiz.question_set.all()
        answers = quiz.answer_set.all()

        # start timer for each question
        for question in questions:
            start = time.time()
            end = start + question.duration
            if time.time() >= end:
                # stop quiz if timer has expired
                return render(request, 'quiz_results.html', {
                    'grade': 0,
                    'status': 'fail',
                })
            else:
                # calculate time remaining for each question
                time_remaining = end - time.time()
                question.time_remaining = time_remaining

        # grade quiz
        num_correct = 0
        for question in questions:
            correct_answer = question.answer_set.get(is_correct=True)
            if answers[str(question.id)] == correct_answer.id:
                num_correct += 1

        # calculate grade and pass/fail status
        grade = num_correct / len(questions)
        if grade >= 0.7:
            status = 'pass'
        else:
            status = 'fail'

        return render(request, 'quiz_results.html', {
            'grade': grade,
            'status': status,
        })
    else:
        return render(request, 'take_quiz.html')


def final_grade(request):
    # get all courses and assignments for student
    courses = Course.objects.all()
    assignments = Assignment.objects.all()

    # calculate final grade for each course
    for course in courses:
        total_grade = 0
        num_assignments = 0
        for assignment in assignments:
            if assignment.course == course:
                total_grade += assignment.grade
                num_assignments += 1
        final_grade = total_grade / num_assignments
        course.final_grade = final_grade

    return render(request, 'final_grade.html', {
        'courses': courses,
    })


from django.shortcuts import render, redirect
