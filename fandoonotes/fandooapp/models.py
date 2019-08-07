# Create your models here.
from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.


class UserProfileInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    portfolio_site = models.URLField(blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)


def __str__(self):
    return self.user.username


# model for profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

# model for update user profile
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


# model for label
class Labels(models.Model):
    title = models.CharField(max_length=20, blank=False)
    is_deleted = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.title


# model class for note
class Notes(models.Model):
    title = models.CharField(max_length=30, blank=False)
    discription = models.TextField(max_length=250, blank=True)
    is_archive = models.BooleanField(default=False, blank=True)
    is_deleted = models.BooleanField(default=False, blank=True)
    color = models.CharField(max_length=20, blank=False)
    image = models.ImageField(upload_to='static/img', blank=True)
    trash = models.BooleanField(default=False, blank=True)
    labels = models.ManyToManyField(Labels,related_name='note_labels', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='owner')
    collaborate = models.ManyToManyField(User, related_name='collaborate_user', blank=True)

    def __str__(self):
        return self.title


