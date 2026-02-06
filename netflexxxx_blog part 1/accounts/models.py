from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    
    def __str__(self):
        return self.username
