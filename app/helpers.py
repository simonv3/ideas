from django.core.mail import EmailMultiAlternatives
from app.models import Idea,Tag,Vote,Comment,Slate,Invitee
from app.forms import IdeaForm
from django.contrib import messages

import settings
import hashlib

import base64

def send_comment_email(owner, request, idea, email, comment_text):
    link_url = request.build_absolute_uri("/idea/"+str(idea.id)+"/")
    #temp_string = owner ? 'your idea' : 'an idea you commented on'
    subject, from_email, to = 'Someone commented on your idea' if owner else 'Someone commented on an idea you commented on', 'Idea Otter<no-reply@ideaotter.com>', 'to@example.com'
    text_content = 'Hey,\n\n Looks like someone commented on idea \n\n ' + idea.idea + ' \n\n which you can see here:\n\n '+link_url+'/\n\n Discuss away!'
    html_content = '<h2>'+request.user.username+' commented on idea:</h2><p>"'+idea.idea+'"</p><h3>With the comment:</h3><p>"'+comment_text+'"<p>Check it out <a href="'+link_url+'">here</a>!</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except Exception:
        print Exception
        messages.error(request,(
                "We had a problem sending the e-mail, the"
                " problem has been reported"
                ))

def vote(voteForm, user):
    clean = voteForm.cleaned_data
    idea = Idea.objects.get(id = clean['idea'])
    try:
        vote= Vote.objects.get(user = user, idea = idea)
    except:
        vote = Vote(vote = clean['vote'], user = user, idea = idea)
        vote.save()
    else:
        vote.delete()
        


def filter_tags(cleanedTags, idea):
    Tag.objects.filter(idea = idea).delete()
    if cleanedTags:
        for tag in cleanedTags.split(','):
            if tag != '':
                tag = Tag(tag=tag.strip(), idea = idea)
                tag.save()



def add_idea(request, slate_id=None):
    print slate_id
    ideaForm = IdeaForm(request.POST)
    if ideaForm.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        # ...
        clean = ideaForm.cleaned_data
        idea = Idea(
                idea=clean['idea_content'], 
                user = request.user, 
                private = clean['private'],
                )
        idea.save()
        if slate_id:
            print "add to slate"
            slate = Slate.objects.get(id=slate_id)
            slate.ideas.add(idea)
            slate.save()
        filter_tags(clean['tags'], idea)
        print "returning idea"
        return idea

def send_verify_email(email, user, request):
    m = hashlib.sha224("some_salt1234"+str(user.id))
    encoded_email = email#base64.b64encode(clean['email'])
    link_url = request.build_absolute_uri("/accounts/verify/"+str(user.id)+"/"+m.hexdigest())
    subject, from_email = 'Idea Otter Registration', 'Idea Otter<contact@ideaotter.com>'
    text_content = 'Hey,\n\n To complete e-mail verification, use the following link:\n\n '+link_url+'/\n\n Thanks, Simon'
    html_content = '<h2>Welcome to Idea!</h2><p>To complete e-mail verification, click <a href="'+link_url+'">here</a></p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def register_invites(v_user):
    invite_list = Invitee.objects.filter(email=v_user.email)
    for invite in invite_list:
            print "user invited"
            slate = Slate.objects.get(id= invite.slate.id)
            slate.users.add(v_user)
            slate.save()
            invite.delete()
            messages.info(request, (
                    "you've been added to slate %s"
                    ) % (slate.name))

def handle_uploaded_file(f, url, file_type):
    print url
    if f.size > 400000:
        return False, "large"
    with open(url, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
        return True, "success"

def process_ideas(user, ideas):
    processed_ideas = []
    for idea in ideas:
        if idea.idea_on_slate.all():
            continue
        else:
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


