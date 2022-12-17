from django.db import models

# Create your models here.
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=50)
    #user_id = models.IntegerField(default=0)


"""class CustomUser(AbstractUser):
    user_type = models.CharField(max_length=255)"""