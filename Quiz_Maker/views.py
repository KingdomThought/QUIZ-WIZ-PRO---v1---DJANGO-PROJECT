import secrets
import time

from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

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

        # Create a Quiz object and add it to the database
        quiz = Quiz(name=name, subject=subject, grade_level=grade_level, num_ques=num_ques)
        quiz.save()

        # Query the database for the id of the Quiz model
        quiz_id = quiz.id
        quiz_name = quiz.name

        # Call the create_question function, passing the num_ques argument
        return create_question(request, quiz_id=quiz.id, num_ques=num_ques)
    else:
        # Render the create_question.html template
        return render(request, 'create_quiz.html')


def quiz_create_success(request):
    # Render the quiz_create_success.html template
    return render(request, 'quiz_create_success.html')


def create_question(request, quiz_id, num_ques):
    # Check if the request method is POST
    if request.method == 'POST':
        # Try to get the question text from the request.POST dictionary
        text = request.POST.get('question_text', '')  # Set the default value of text to an empty string

        # Get the answers from the request.POST dictionary
        answer_1 = request.POST.get('answer_1', "")
        answer_2 = request.POST.get('answer_2', "")
        answer_3 = request.POST.get('answer_3', "")
        answer_4 = request.POST.get('answer_4', " ")

        # Create the question object
        question = Question(quiz_id=quiz_id, text=text, duration=60)
        question.save()

        # Create the answer objects
        a1 = Answer(text=answer_1, is_correct=True, question_id=question.id)
        a2 = Answer(text=answer_2, is_correct=False, question_id=question.id)
        a3 = Answer(text=answer_3, is_correct=False, question_id=question.id)
        a4 = Answer(text=answer_4, is_correct=False, question_id=question.id)
        a1.save()
        a2.save()
        a3.save()
        a4.save()

        # Decrement the number of questions
        num_ques = int(num_ques)
        num_ques -= 1

        # If there are still questions left, reload the page
        if int(num_ques) > 0:
            return redirect('create_question', quiz_id=quiz_id, num_ques=num_ques)
        else:
            return redirect('quiz_create_success')
    else:
        # If num_ques is 0 or less, return immediately
        if num_ques <= 0:
            return redirect('quiz_create_success')

        # Pass the quiz_id and num_ques to the create_question.html template
        return render(request, 'create_question.html', {'quiz_id': quiz_id, 'num_ques': num_ques})


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
