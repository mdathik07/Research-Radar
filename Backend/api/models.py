# from django.db import models
# from django.contrib.auth.models import AbstractUser
# # Create your models here.
# class Users(AbstractUser):
#     username = models.CharField(max_length=255)
#     email = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#     interests = models.CharField()
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

# class Papers(models.Model):
#     title=models.CharField()
#     url=models.CharField()
#     abstract=models.CharField()
#     authors=models.CharField()

from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    # Don't re-declare username/password (AbstractUser provides them).
    # Make email the unique identifier for auth:
    email = models.EmailField(unique=True)

    # Use TextField for potentially long interests
    interests = models.TextField(blank=True, default="")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # username still required on create_superuser

    def __str__(self):
        return self.email or self.username


class Papers(models.Model):
    title = models.CharField(max_length=512)
    url = models.URLField(max_length=2048, blank=True)
    abstract = models.TextField(blank=True)
    authors = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:80]

