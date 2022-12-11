# Create your models here.
from django.db import models


class Quiz(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    grade_level = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    duration = models.IntegerField()  # add this line to set duration for each question

    def __str__(self):
        return self.text


class Course(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    grade = models.FloatField()

    def __str__(self):
        return self.name


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField()

    def __str__(self):
        return self.text
