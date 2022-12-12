from django import forms

from django.contrib.auth.models import User


class MyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        labels = {"username", "password"}
