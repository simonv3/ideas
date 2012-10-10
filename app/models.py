from django.db import models
from django.contrib.auth.models import User
# in models.py

from django.db.models.signals import post_save
import datetime

# Create models here.

class Idea(models.Model):
    user = models.ForeignKey(User, related_name='user_idea')
    idea = models.TextField()
    elaborate = models.TextField(blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)
    started = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    def __unicode__(self):
        return "idea by %s: %s" %(self.user, self.idea)

class Tag(models.Model):
    idea = models.ForeignKey(Idea, related_name='tag_idea')
    tag = models.CharField(max_length=100)

    def __unicode__(self):
        return "tag for %s: %s" %(self.idea,self.tag)

class Vote(models.Model):
    VOTE_CHOICES = (
            (u'+', u'Vote Up'),
            (u'-', u'Vote Down'),
        )
    user = models.ForeignKey(User, related_name='user_vote')
    vote = models.CharField(max_length=2, choices=VOTE_CHOICES)
    idea = models.ForeignKey(Idea, related_name='vote_on')
    def __unicode__(self):
        return "vote %s for %s by %s" %(self.vote,self.idea,self.user)

class Comment(models.Model):
    user = models.ForeignKey(User, related_name='user_comment')
    idea = models.ForeignKey(Idea, related_name='idea_comment')
    text = models.TextField()
    date_posted = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return "comment %s for %s by %s" %(self.text,self.idea,self.user)


class UserProfile(models.Model):
    temp_hash = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, related_name='extra')
    facebook_access_token = models.CharField(blank=True, max_length=200)
    default_private = models.BooleanField(default=False)
    emails = models.BooleanField(default=True)
    photo  = models.ImageField(upload_to = 'users/', null=True, blank=True)

    def get_ideas_commented_on(self):
        idea = Idea.objects.filter(idea_comment__user = self.user).distinct()
        return idea

    def comments_on_owned_ideas(self, num_days):
        user = self.user
        commented_on_ideas = user.user_idea.filter(
                    idea_comment__date_posted__gte=datetime.date.today()-datetime.timedelta(num_days)
                    ).distinct()
        return commented_on_ideas
    
    def new_ideas_in_slate(self, num_days):
        user = self.user
        ideas = user.slates


    def get_image(self):
        if not self.image:
            # depending on your template
            return "ideaotter.png"
        else:
            return self.image

    def __unicode__(self):
        return self.user.username + " profile"


# attaches the user profile to the user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



post_save.connect(create_user_profile, sender=User)



class Slate(models.Model):
    creator = models.ForeignKey(User, related_name='slate_creator',blank=True)
    date_created = models.DateTimeField(auto_now_add=True,
            default=datetime.datetime.now())
    users = models.ManyToManyField(User, related_name='slates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ideas = models.ManyToManyField(Idea, related_name='idea_on_slate')

    def __unicode__(self):
        return "slate %s" %(self.name)

class Invitee(models.Model):
    email = models.CharField(max_length=200)
    slate = models.ForeignKey(Slate, related_name="invite_for")
    def __unicode__(self):
        return "Invite for %s on %s" %(self.email, self.slate)

#class Email_Message(models.Model):
#    content = models.TextField()
#    sent = models.BooleanField()
#    date = models.DateField(auto_now = True)
