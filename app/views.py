# Create your views here.
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages

from app.forms import IdeaForm, VoteForm, CommentForm, EmailForm

from app.models import Idea,Tag,Vote,Comment

from settings import FACEBOOK_SECRET, FACEBOOK_ID

import urllib
import json


def splash(request):

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
                    vote(voteForm,request.user)
            if 'submit_email' in request.POST:
                emailForm = EmailForm(request.POST)
                if emailForm.is_valid():
                    clean = emailForm.cleaned_data
                    user.email = clean['email']
                    from django.core.mail import EmailMultiAlternatives
                    import hashlib
                    m = hashlib.sha224("some_salt1234"+user.username)
                    m.hexdigest()
                    import base64
                    encoded_email = clean['email']#base64.b64encode(clean['email'])
                    link_url = request.build_absolute_uri("/accounts/verify/"+user.username+"/"+m.hexdigest())
                    subject, from_email = 'Idea Otter Registration', 'Idea Otter<no-reply@ideaotter.com>'
                    text_content = 'Hey,\n\n To complete e-mail verification, use the following link:\n\n '+link_url+'/\n\n Thanks, Simon'
                    html_content = '<h2>Welcome to Idea!</h2><p>To complete e-mail verification, click <a href="'+link_url+'">here</a></p>'
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    user.save()
            if 'submit_idea' in request.POST:
                ideaForm = IdeaForm(request.POST) # A form bound to the POST data
                if ideaForm.is_valid(): # All validation rules pass
                    # Process the data in form.cleaned_data
                    # ...
                    clean = ideaForm.cleaned_data
                    idea = Idea(idea=clean['idea_content'], user = request.user)
                    idea.save()
                    filterTags(clean['tags'], idea)
        voteUpForm = VoteForm({'vote':'+'})
        voteDownForm = VoteForm({'vote':'-'})
        ideaForm = IdeaForm() # An unbound form

        emailForm = EmailForm({'email':user.email})
        all_ideas = Idea.objects.all().order_by('-date')
        return render_to_response("main/home.html",locals(),
                context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def idea(request,idea_id, edit=False):
    try:
        idea = Idea.objects.get(id =idea_id)
    except Idea.DoesNotExist:
        return HttpResponseRedirect("/")
    tags = Tag.objects.filter(idea = idea)
    relevant_comments = Comment.objects.filter(idea = idea).order_by("-date_posted")
    if request.method == 'POST': #If something has been submitted
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    vote(voteForm,request.user)
            if 'edit_idea' in request.POST:
                ideaForm = IdeaForm(request.POST)
                if ideaForm.is_valid():
                    clean = ideaForm.cleaned_data
                    idea.idea = clean['idea_content']
                    filterTags(clean['tags'], idea)
                    idea.save()

            if 'submit_comment' in request.POST:
                commentForm = CommentForm(request.POST)
                if commentForm.is_valid():
                    clean = commentForm.cleaned_data
                    comment = Comment(text = clean['comment'],idea=idea,user = request.user)
                    comment.save()
                    all_comments_idea = Comment.objects.filter(idea = idea)
                    #if the user posting the comment doesn't own the idea, send the email to the user who owns the idea
                    if request.user != idea.user:
                        send_comment_email(True, request, idea, idea.user.email, comment.text)
                    #add the user who owns the idea to the list, because either they've already received it from above, or they're the ones posting the comment
                    user_emails_sent = [idea.user,]
                    #for every comment on the idea
                    for comment_for_idea in all_comments_idea:
                        #if the commenter is not the request user we want to send the email, but
                        if comment_for_idea.user != request.user:
                            #only if the comment hasn't already been sent an email.
                            if not comment_for_idea.user in user_emails_sent:

                                user_emails_sent.append(comment_for_idea.user)
                                send_comment_email(False, request, idea, comment_for_idea.user.email, comment.text)
                                        #encoded_email = user.email
    voteUpForm = VoteForm({'vote':'+'})
    if edit and (idea.user == request.user):
        tagString = ''
        for tag in tags:
            tagString += tag.tag + ","
        tagString = tagString[0:(len(tagString)-1)]
        ideaForm = IdeaForm({'idea_content':idea.idea, 'tags':tagString})
    else:
        edit = False
    voteDownForm = VoteForm({'vote':'-'})
    commentForm = CommentForm()
    return render_to_response('main/idea.html',locals(),
            context_instance=RequestContext(request))



@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user
    your_ideas = Idea.objects.filter(user = user).order_by('-date')

    if request.method == 'POST': #If something has been submitted
            if 'vote' in request.POST:
                voteForm = VoteForm(request.POST)
                if voteForm.is_valid():
                    vote(voteForm,request.user)

    voted_on = Vote.objects.filter(user = user)
    #print user.first_name
    return render_to_response('main/profile.html', locals(), context_instance=RequestContext(request))


def register(request):
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
                from django.contrib.auth import authenticate, login
                user_in_db = authenticate(username=formcd['username'],password=formcd['password1'])
                login(request,user_in_db)
                return HttpResponseRedirect("/accounts/profile/")

    else:
        data, errors = {}, {}

    return render_to_response("main/register.html", locals(),
            context_instance=RequestContext(request))


    

def vote(voteForm, user):
    clean = voteForm.cleaned_data
    idea = Idea.objects.get(id = clean['idea'])
    try:
        vote= Vote.objects.get(user = user, idea = idea)
    except:
        vote = Vote(vote = clean['vote'], user = user, idea = idea)
        vote.save()
    else:
        vote.vote = clean['vote']
        vote.save()


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
                    idea = Idea(idea=clean['idea_content'], user = request.user)
                    idea.save()
                    filterTags(clean['tags'], idea)
                    posted = True
    ideaForm = IdeaForm()
    return render_to_response("main/bookmarklet.html", locals(),
            context_instance=RequestContext(request))

def verify(request,username, verify_hash):
    import hashlib
    m = hashlib.sha224("some_salt1234"+username)
    m.hexdigest()
    if verify_hash == m.hexdigest():
        v_user = User.objects.get(username=username)
        #v_user.groups.add(id=1)
        #v_user.save()
        verified_group = Group.objects.get(name='verified')
        v_user.groups.add(verified_group)
        

    return HttpResponseRedirect("/")

def filterTags(cleanedTags, idea):
    Tag.objects.filter(idea = idea).delete()
    for tag in cleanedTags.split(','):
        tag = Tag(tag=tag, idea = idea)
        tag.save()

def send_comment_email(owner, request, idea, email, comment_text):
    from django.core.mail import EmailMultiAlternatives

    link_url = request.build_absolute_uri("/idea/"+str(idea.id)+"/")
    #temp_string = owner ? 'your idea' : 'an idea you commented on'
    subject, from_email, to = 'Someone commented on your idea' if owner else 'Someone commented on an idea you commented on', 'Idea Otter<no-reply@ideaotter.com>', 'to@example.com'
    text_content = 'Hey,\n\n Looks like someone commented idea \n\n ' + idea.idea + ' \n\n which you can see here:\n\n '+link_url+'/\n\n Discuss away!'
    html_content = '<h2>'+request.user.username+' commented on idea:</h2><p>"'+idea.idea+'"</p><h3>With the comment:</h3><p>"'+comment_text+'"<p>Check it out <a href="'+link_url+'">here</a>!</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


#
# Facebook Integration
#

def facebook(request):
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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return HttpResponseRedirect("/accounts/profile/")

