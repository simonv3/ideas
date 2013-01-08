from django.contrib.auth.models import User
from app.models import Idea, Slate, Vote
from app import helpers

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect




def user(request, user_id):
    try:
        profile_user = User.objects.get(id = user_id)
    except User.DoesNotExist:
        return HttpResponseRedirect("/")
    your_ideas = Idea.objects.filter(user = profile_user).filter(private=False).order_by('-date')
    ideas_len = len(your_ideas)
    your_slates = Slate.objects.filter(creator = profile_user).order_by('-id')
    slates_len = len(your_slates)
    if request.method == 'POST': #If something has been submitted
            print "post"
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    helpers.vote(voteForm,request.user)

    voted_on = Vote.objects.filter(user = profile_user)
    voted_len = len(voted_on)
    commented_on = profile_user.get_profile().get_ideas_commented_on()
    comments_len = len(commented_on)

    return render_to_response('main/user_profile.html', locals(), context_instance=RequestContext(request))
