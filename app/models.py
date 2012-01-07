from django.db import models
from django.contrib.auth.models import User
# in models.py

from django.db.models.signals import post_save

# definition of UserProfile from above



from datetime import datetime

# Create models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='extra')


# attaches the user profile to the user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
    
