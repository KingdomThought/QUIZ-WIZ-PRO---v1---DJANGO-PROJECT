import secrets
import time

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


def create_dash(request):
    return redirect()

def create_quiz(request):
    if request.method == 'POST':
        name = request.POST['name']
        subject = request.POST['subject']
        grade_level = request.POST['grade_level']

        quiz = Quiz.objects.create(name=name, subject=subject, grade_level=grade_level)



        return redirect('create_question.html')
    else:
        return render(request, 'create_quiz.html')


def create_question(request):
    if request.method == 'POST':
        quiz_id = request.POST['quiz_id']
        text = request.POST['text']

        question = Question.objects.create(quiz_id=quiz_id, text=text)

        return HttpResponse('create_answer.html')
    else:
        return render(request, 'create_question.html')


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
