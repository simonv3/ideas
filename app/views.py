# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django import forms

from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required

from app.forms import IdeaForm, VoteForm, CommentForm, EmailForm

from app.models import Idea,Tag,Vote,Comment

def splash(request):

    if not request.user.is_authenticated():
        form = UserCreationForm()
        if request.method=="POST":
            register(request)
            return HttpResponseRedirect("/")
        else:
            return render_to_response("main/register.html", locals(),
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
                    subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
                    text_content = 'Hey,\n\n To complete e-mail verification, use the following link:\n\n '+link_url+'/\n\n Thanks, Simon'
                    html_content = '<h2>Welcome to Idea!</h2><p>To complete e-mail verification, click <a href="'+link_url+'">here</a></p>'
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
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
    relevant_comments = Comment.objects.filter(idea = idea)
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
                    encoded_email = user.email
                    all_comments_idea = Comment.objects.filter(idea = idea)
                    if request.user != idea.user:
                        send_comment_email(request, idea, idea.user.email, comment.text)

                    user_emails_sent = [idea.user,]
                    for comment_for_idea in all_comments_idea:
                        if comment_for_idea.user != request.user:
                            #print "send to "+comment_for_idea.user.username
                            #print user_emails_sent
                            #print comment_for_idea.user
                            if not comment_for_idea.user in user_emails_sent:
                                #print "prep email"
                                user_emails_sent.append(comment_for_idea.user)
                                send_comment_email(request, idea, comment_for_idea.user.email, comment.text)
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

    #print user.first_name
    return render_to_response('main/profile.html', locals(), context_instance=RequestContext(request))


def register(request):
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
    print verify_hash
    import hashlib
    m = hashlib.sha224("some_salt1234"+username)
    m.hexdigest()
    if verify_hash == m.hexdigest():
        v_user = User.objects.get(username=username)
        print v_user
        #v_user.groups.add(id=1)
        #v_user.save()
        verified_group = Group.objects.get(name='verified')
        print verified_group
        v_user.groups.add(verified_group)
        

    return HttpResponseRedirect("/")

def filterTags(cleanedTags, idea):
    Tag.objects.filter(idea = idea).delete()
    for tag in cleanedTags.split(','):
        tag = Tag(tag=tag, idea = idea)
        tag.save()

def send_comment_email(request, idea, email, comment_text):
    from django.core.mail import EmailMultiAlternatives

    link_url = request.build_absolute_uri("/idea/"+str(idea.id)+"/")
    subject, from_email, to = 'Someone commented on your idea', 'Idea Otter<no-reply@ideaotter.com>', 'to@example.com'
    text_content = 'Hey,\n\n Looks like someone commented on your idea \n\n ' + idea.idea + ' \n\n which you can see here:\n\n '+link_url+'/\n\n Discuss away!'
    html_content = '<h2>'+request.user.username+' commented on your idea:</h2><p>"'+idea.idea+'"</p><h3>With the comment:</h3><p>"'+comment_text+'"<p>Check it out <a href="'+link_url+'">here</a>!</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

