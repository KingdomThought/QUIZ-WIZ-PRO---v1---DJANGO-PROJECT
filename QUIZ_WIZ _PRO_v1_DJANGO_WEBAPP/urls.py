"""QUIZ_WIZ _PRO_v1_DJANGO_WEBAPP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin

from django.contrib.auth import login
from django.urls import path
from django.urls import include
from Login.views import login_view
from Quiz_Maker.views import dashboard_view, student_dashboard_view
from Login.views import register_view, login_view, forgot_password_view
from Quiz_Maker import views
from Quiz_Maker.views import take_quiz, create_question, create_quiz

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Quiz_Maker/create-quiz/', create_quiz, name='create_quiz'),
    path('take-quiz/', take_quiz, name='take_quiz'),
    path('', login_view, name='login_view'),
    path('take_quiz/', views.take_quiz, name='take_quiz'),
    path('register.html', register_view, name='register_view'),
    path('Quiz_Maker/dashboard.html', dashboard_view, name='dashboard'),
    path('Quiz_Maker/student_dashboard.html', student_dashboard_view, name='student_dashboard'),
    path('forgotpassword/', forgot_password_view, name='forgot_password_view'),
    path('Quiz_Maker/create-question/<int:quiz_id>/<int:num_ques>/', views.create_question, name='create_question'),
    path('Quiz_Maker/quiz_create_success', views.quiz_create_success, name='quiz_create_success'),

]
