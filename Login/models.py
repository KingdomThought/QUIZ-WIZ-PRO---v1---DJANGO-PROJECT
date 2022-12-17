from django.db import models


class UserType(models.Model):
    id = models.AutoField(primary_key=True)
    user_type = models.CharField(max_length=50)



