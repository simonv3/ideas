# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages

from app.forms import IdeaForm, VoteForm, CommentForm, EmailForm, ResetPasswordForm, SearchForm

from app.models import Idea,Tag,Vote,Comment,Slate,Invitee

from settings import FACEBOOK_SECRET, FACEBOOK_ID, CLIENT_SUB_DOMAIN

from app import helpers

import urllib
import json
import base64
import hashlib
import datetime




def splash(request,show=''):
    client_sub_domain = CLIENT_SUB_DOMAIN
    if not request.user.is_authenticated():
        form = AuthenticationForm()
        if request.method=="POST":
            register(request)
            return HttpResponseRedirect("/")
        else:
            return render_to_response("main/splash.html", locals(),
                    context_instance=RequestContext(request))

    #
    # else there is a user and we can just show the general page
    #


    else:
        user = request.user
        #if user.has_perm(app.idea.can_add):
        #    post_idea = True
        #else:
        #    post_idea = False
        if request.method == 'POST': #If something has been submitted
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    helpers.vote(voteForm,request.user)
            if 'submit_email' in request.POST:
                emailForm = EmailForm(request.POST)
                if emailForm.is_valid():

                    clean = emailForm.cleaned_data
                    exists = User.objects.filter(email=clean['email'])
                    if len(exists) > 0:
                        messages.error(request, (
                            "That e-mail address is "
                            "already in use, have you signed up before "
                            "using a different username?"))
                        return HttpResponseRedirect("/")
                    
                    user.email = clean['email']

                    helpers.send_verify_email(clean['email'],user,request)

                    user.save()
            if 'submit_idea' in request.POST:
                idea = helpers.add_idea(request)
            if 'submit_idea_elaborate' in request.POST:
                idea = helpers.add_idea(request)
                if idea:
                    return HttpResponseRedirect(reverse('edit-idea', args=[idea.id]))

        voteUpForm = VoteForm({'vote':'+'})
        voteDownForm = VoteForm({'vote':'-'})
        ideaForm = IdeaForm()
        searchForm = SearchForm() 
        emailForm = EmailForm({'email':user.email})
        all_ideas = Idea.objects.exclude(private=True).annotate(votes=Count('vote_on'))
        if show == 'started':
            all_ideas = Idea.objects.filter(started=True).exclude(private=True).annotate(votes=Count('vote_on'))
        elif show == 'not-started':
            all_ideas = Idea.objects.exclude(started=True).exclude(private=True).annotate(votes=Count('vote_on'))
        if show == 'top':
            all_ideas = all_ideas.order_by('-votes')
        else:
            all_ideas = all_ideas.order_by('-date')
        all_ideas = process_ideas(user, all_ideas)
        return render_to_response("main/home.html",locals(),
                context_instance=RequestContext(request))

def process_ideas(user, ideas):
    processed_ideas = []
    for idea in ideas:
            try:
                Vote.objects.get(idea = idea, user = user)
            except:
                new_idea = {
                        "idea":idea.idea,
                        "id":idea.id,
                        "started":idea.started,
                        "date":idea.date,
                        "voted_on":False,
                        "votes":idea.votes,
                        "user":idea.user,
                        }
                processed_ideas.append(new_idea)
            else:
                new_idea = {
                        "idea":idea.idea,
                        "started":idea.started,
                        "user":idea.user,
                        "id":idea.id,
                        "votes":idea.votes,
                        "date":idea.date,
                        "voted_on":True
                        }
                processed_ideas.append(new_idea)
    return processed_ideas


@login_required(login_url='/accounts/login/')
def idea(request,idea_id, edit=False):
    try:
        idea = Idea.objects.get(id =idea_id)
    except Idea.DoesNotExist:
        return HttpResponseRedirect("/")
    tags = Tag.objects.filter(idea = idea)
    try:
        voted_on = idea.vote_on.get(user = request.user)
    except:
        pass
    relevant_comments = Comment.objects.filter(idea = idea).order_by("date_posted")
    commentForm = CommentForm(request.POST or None)
    
    if request.method == 'POST': #If something has been submitted
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    helpers.vote(voteForm,request.user)
            if 'edit_idea' in request.POST:
                ideaForm = IdeaForm(request.POST)
                if ideaForm.is_valid():
                    clean = ideaForm.cleaned_data
                    idea.idea = clean['idea_content']
                    idea.elaborate = clean['elaborate']
                    helpers.filter_tags(clean['tags'], idea)
                    idea.save()
                    edit = False
                    return HttpResponseRedirect("/idea/"+str(idea.id)+"/")
            if 'submit_comment' in request.POST:
                commentForm = CommentForm(request.POST)
                if commentForm.is_valid():
                    clean = commentForm.cleaned_data
                    comment = Comment(text = clean['comment'],idea=idea,user = request.user)
                    comment.save()
                    all_comments_idea = Comment.objects.filter(idea = idea)
                    #if the user posting the comment doesn't own the idea, send the email to the user who owns the idea
                    if request.user != idea.user:
                        helpers.send_comment_email(True, request, idea, idea.user.email, comment.text)
                    #add the user who owns the idea to the list, because either they've already received it from above, or they're the ones posting the comment
                    user_emails_sent = [idea.user,]
                    #for every comment on the idea
                    for comment_for_idea in all_comments_idea:
                        #if the commenter is not the request user we want to send the email, but
                        if comment_for_idea.user != request.user:
                            #only if the comment hasn't already been sent an email.
                            if not comment_for_idea.user in user_emails_sent:

                                user_emails_sent.append(comment_for_idea.user)
                                helpers.send_comment_email(False, request, idea, comment_for_idea.user.email, comment.text)
                                        #encoded_email = user.email
    voteUpForm = VoteForm({'vote':'+'})
    if edit and (idea.user == request.user):
        tagString = ''
        for tag in tags:
            tagString += tag.tag + ","
        tagString = tagString[0:(len(tagString)-1)]
        ideaForm = IdeaForm({
            'idea_content':idea.idea,
            'elaborate':idea.elaborate,
            'tags':tagString})
    else:
        edit = False
    voteDownForm = VoteForm({'vote':'-'})
    commentForm = CommentForm(None)
    return render_to_response('main/idea.html',locals(),
            context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def delete_idea(request, idea_id):
    idea = Idea.objects.get(id = idea_id)
    if not request.user == idea.user:
        messages.error(request, "You're not the author of this idea")
    else:
        Idea.delete(idea)
    return HttpResponseRedirect("/")

@login_required(login_url='/accounts/login/')
def start_idea(request, idea_id):
    idea = Idea.objects.get(id = idea_id)
    if not request.user == idea.user:
        messages.error(request, "You're not the author of this idea")
    else:
        idea.started = True
        idea.save()
    return HttpResponseRedirect("/idea/"+str(idea.id)+"/")



@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user
    your_ideas = Idea.objects.filter(user = user).order_by('-date')
    ideas_len = len(your_ideas)
    your_slates = Slate.objects.filter(creator = user).order_by('-id')
    slates_len = len(your_slates)

    if request.method == 'POST': #If something has been submitted
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    helpers.vote(voteForm,request.user)

    voted_on = Vote.objects.filter(user = user)
    voted_len = len(voted_on)
    commented_on = user.get_profile().get_ideas_commented_on()
    comments_len = len(commented_on)

    return render_to_response('main/profile.html', locals(), context_instance=RequestContext(request))


def register(request):
    client_sub_domain = CLIENT_SUB_DOMAIN
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    form = UserCreationForm()
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserCreationForm(request.POST)
        if form.is_valid():
            formcd = form.cleaned_data
            if formcd['password1'] == formcd['password2']:
                user = User.objects.create_user(formcd['username'],'',formcd['password1'])
                user.save()
                user_in_db = authenticate(username=formcd['username'],password=formcd['password1'])
                login(request,user_in_db)

                try: 
                    #if user uses an e-mail address to sign up
                    #send an e-mail right away
                    validate_email ( formcd['username'] )
                except:
                    #can fail silently, because then everything is just normal 
                    pass
                else:
                    user_in_db.email = formcd['username']
                    user_in_db.save()
                    helpers.send_verify_email(formcd['username'], user, request)
                return HttpResponseRedirect("/")

    else:
        data, errors = {}, {}

    return render_to_response("main/register.html", locals(),
            context_instance=RequestContext(request))


@login_required(login_url='/accounts/login/')
def bookmarklet(request):
    posted = False
    if request.method == 'POST': #If something has been submitted
        if 'submit_idea' in request.POST:
                ideaForm = IdeaForm(request.POST) # A form bound to the POST data
                if ideaForm.is_valid(): # All validation rules pass
                    # Process the data in form.cleaned_data
                    # ...
                    clean = ideaForm.cleaned_data
                    idea = Idea(idea=clean['idea_content'], user =
                            request.user, private=clean['private'])
                    idea.save()
                    helpers.filter_tags(clean['tags'], idea)
                    posted = True
    ideaForm = IdeaForm()
    return render_to_response("main/bookmarklet.html", locals(),
            context_instance=RequestContext(request))

def search(request, query=""):
    searchForm = SearchForm(request.GET or None)
    if request.method == "GET":
        if searchForm.is_valid():
            cd = searchForm.cleaned_data
            #redirect to this function, but send the search into the query. 
            #print "redirecting"
            return HttpResponseRedirect("/search/"+cd['query']+"/")
    idea_results = []
    if query != "":
        ideas_with_tags = Tag.objects.filter(tag__contains=query)
        all_ideas = Idea.objects.filter(idea__contains=query)
        for idea in ideas_with_tags:
            idea_results.append(idea.idea)
        for idea in all_ideas:
            if idea not in idea_results:
                idea_results.append(idea)
    return render_to_response("main/idea_list.html", locals(),
            context_instance=RequestContext(request))

def verify(request,id, verify_hash):
    m = hashlib.sha224("some_salt1234"+str(id))
    m.hexdigest()
    if verify_hash == m.hexdigest():
        v_user = User.objects.get(id=id)
        verified_group = Group.objects.get(name='verified')
        v_user.groups.add(verified_group)
        helpers.register_invites(v_user)
        v_user.save()
        return HttpResponseRedirect("/")



#
# Password management
#

def password(request):

    if request.user.is_authenticated():
        form = ResetPasswordForm()
        if request.method=="POST":
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                clean = form.cleaned_data
                if clean['password'] == clean['repeat_password']:
                    request.user.set_password(clean['password'])
                    request.user.save()
                    return HttpResponseRedirect("/accounts/profile/")
        return render_to_response("main/reset_password.html", locals(),
                context_instance=RequestContext(request))
    else:
        form = EmailForm()
        if request.method=="POST":
            form = EmailForm(request.POST)
            if form.is_valid():
                clean = form.cleaned_data
                email = clean['email']
                user = User.objects.get(email = email)
                temp_date = datetime.datetime.now()
                user.get_profile().temp_hash = str(temp_date)
                user.get_profile().save()
                m = hashlib.sha224(str(temp_date)).hexdigest()
                rel_url = "/accounts/pw_rst/"+str(user.id)+"/"+m+"/"
                link_url = request.build_absolute_uri(rel_url)
                print link_url
                subject, from_email, to = 'Password Reset' , 'Idea Otter<no-reply@ideaotter.com>', 'to@example.com'
                text_content = 'Hey,\n\n You (or someone else) has asked to reset your password. Click on the url to it\n\n ' +link_url +'\n\n'
                html_content = '<h2>Password Reset</h2><p>You requested a password reset</p><p>Click <a href="'+link_url+'">here</a>!</p>'
                print text_content
                print html_content
                msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
                msg.attach_alternative(html_content, "text/html")
                print msg
                msg.send()
        return render_to_response("main/lost_password.html", locals(),
                context_instance=RequestContext(request))


def password_reset(request, user_id,hashed):
    if request.method=="POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            if clean['password'] == clean['repeat_password']:
                user = User.objects.get(id = user_id)
                temp_date = user.get_profile().temp_hash
                m = hashlib.sha224(str(temp_date)).hexdigest()
                if m != hashed:
                    return HttpResponseRedirect("/")
                user.set_password(clean['password'])
                user.save()
                return HttpResponseRedirect("/")
            else:
                messages.error(request, "Please make sure the passwords are the same")
    form = ResetPasswordForm()
    return render_to_response("main/reset_password.html", locals(),
            context_instance=RequestContext(request))

#
# About
#

def about(request):
    return render_to_response("main/about.html", locals(),
            context_instance=RequestContext(request))

#
# Contact
#

def contact(request):
    return render_to_response("main/contact.html", locals(),
            context_instance=RequestContext(request))


#
# Facebook Integration
#

def facebook(request):
    client_sub_domain = CLIENT_SUB_DOMAIN
    
    if request.method == 'GET':
        if 'error' in request.GET:
            messages.error(request, 'To use Facebook to log in, please give' +
                    'the IdeaOtter permission to use your details.')
            return redirect('django.contrib.auth.views.login')
        else:
            url = ('https://graph.facebook.com/oauth/access_token?' +
                    'client_id=' + str(FACEBOOK_ID) +
                    '&redirect_uri=http://localhost:8000/accounts/facebook/' +
                    '&client_secret=' + str(FACEBOOK_SECRET) +
                    '&code=' + request.GET['code'])
            request.GET['state']
            fetchedinfo = urllib.urlopen(url)
            access_token = fetchedinfo.read()
            if 'error' in access_token:
                messages.error(request, 'Something went wrong when ' +
                        'activating your account, please try again later'+
                        access_token)
                return redirect('django.contrib.auth.views.login')
            url = 'https://graph.facebook.com/me?'+access_token
            fetchedinfo = urllib.urlopen(url)
            user_info = json.loads(fetchedinfo.read())
            try:
                user = User.objects.get(username = user_info['username'])
            except User.DoesNotExist:
                user = User.objects.create_user(
                        user_info['username'],
                        user_info['email'],
                        ''
                        )
                user.first_name=user_info['first_name']
                user.last_name=user_info['last_name']
                user.save()
            user_profile = user.get_profile()
            user_profile.facebook_access_token = access_token
            user_profile.save()
            verified_group = Group.objects.get(name='verified')
            user.groups.add(verified_group)
            helpers.register_invites(user)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            login(request, user)
            return HttpResponseRedirect("/")

