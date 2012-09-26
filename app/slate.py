from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.core.mail import EmailMultiAlternatives


from app import helpers
from app.forms import SlateForm, IdeaForm, VoteForm, InviteForm
from app.models import Slate, Invitee, Idea
from django.contrib.auth.models import User

from django.contrib import messages

@login_required(login_url='/accounts/login/')
def slate(request):
    slateForm = SlateForm(request.POST or None)
    if request.method == 'POST':
        #create slate
        if slateForm.is_valid():

            clean = slateForm.cleaned_data
            if request.user.slate_creator.count() <= 19:
                slate = Slate(
                        name = clean['name'],
                        creator = request.user,
                        description = clean['description']
                        )
                slate.save()
                slate.users.add(request.user)
                return redirect('view-slate', slate_id = slate.id)
            else:
                messages.error(request, 
                        "We're limiting slates to 20 per user for now,"+
                        " we figure that this is more than anyone will really"+
                        " need, but you really want more, contact us at "+
                        "contact@ideaotter.com")

    your_slates = Slate.objects.filter(creator=request.user)
    return render_to_response("main/slate.html", locals(),
            context_instance = RequestContext(request))

@login_required(login_url='/accounts/login/')
def view_slate(request, slate_id):
    slate = Slate.objects.get(id=slate_id)
    try:
        slate.users.get(id = request.user.id)
    except User.DoesNotExist:
        return redirect("slate")

    if request.method == 'POST':
        if 'submit_idea' in request.POST:
            idea = helpers.add_idea(request, slate_id=slate.id)
        if 'submit_idea_elaborate' in request.POST:
            idea = helpers.add_idea(request, slate_id=slate.id)
            if idea:
                return HttpResponseRedirect(reverse('edit-idea', args=[idea.id]))
        if 'invite' in request.POST:
            inviteForm = InviteForm(request.POST)
            if inviteForm.is_valid():
                clean = inviteForm.cleaned_data
                invites = clean['invite_list'].split(',')
                participants = slate.users.count()
                if len(invites) > (6 - participants):
                    messages.error(request, "You can\'t have"+
                            "more than 6 people on a slate."
                            )
                    return redirect("view-slate", slate_id = slate.id)
                for invite in clean['invite_list'].split(','):
                    try:
                        validate_email( invite )
                    except ValidationError:
                        #not an email address, continue with next invite
                        continue
                    else:
                        try:
                            user = User.objects.get(email = invite)
                        except User.DoesNotExist:
                            # user doesn't exist
                            # create an invitee item
                            try:
                                invite = Invitee.objects.get(email = invite,
                                        slate = slate.id)
                            except Invitee.DoesNotExist:
                                pass
                            else:
                                continue
                            invite = Invitee.objects.create(
                                    email=invite,slate=slate)
                            invite.save()
                            link_url = request.build_absolute_uri("/slate/"+str(slate.id)+"/")
                            subject =   (
                                    "%s invited you to a slate %s on "
                                    "IdeaOtter"
                                    ) %(
                                    request.user.username, slate.name
                                    )
                            from_email = "Idea Otter <contact@ideaotter.com>"
                            text_content = (
                                        "Hey, \n\n %s invited you to slate"
                                        " %s you can view it here: \n\n %s "
                                        ) % (
                                                request.user.username, slate.name,
                                                link_url
                                                )
                            html_content = (
                                    "<h2>%s Invited you to:</h2>"
                                    "<p>slate %s</p><p>Check it out <a "
                                    "href=%s>here</a>!</p>"
                                    "<p>IdeaOtter is a site for storing ideas"
                                    "and getting people brainstorming together"
                                    "</p>"
                                    ) % (
                                            request.user.username,slate.name,
                                            link_url)
                            msg = EmailMultiAlternatives(subject, text_content,
                                    from_email, [invite.email])
                            msg.attach_alternative(html_content, "text/html")
                            try:
                                msg.send()
                            except:
                                print "email failed to send"
                                print html_content
                                pass
                        else:
                            # user exists, add them to the project
                            try:
                                slate.users.get(id=user.id)
                                #user already in project, continue with next
                                #iteration of the loop
                            except User.DoesNotExist:
                                #everything is normal
                                pass
                            else:
                                #user is already here
                                continue
                            slate.users.add(user)
                            slate.save()
                            link_url = request.build_absolute_uri("/slate/"+str(slate.id)+"/")
                            subject =   "%s invited you to slate %s" %(
                                    request.user.username, slate.name
                                    )
                            from_email = "Idea Otter <contact@ideaotter.com>"
                            text_content = (
                                        "Hey, \n\n %s invited you to slate"
                                        " %s view it here: \n\n %s "
                                        ) % (
                                                request.user.username, slate.name,
                                                link_url
                                                )
                            html_content = '<h2>'+request.user.username+' invited you to:</h2><p>"'+slate.name+'"</p><p>Check it out <a href="'+link_url+'">here</a>!</p>'
                            msg = EmailMultiAlternatives(subject, text_content,
                                    from_email, [user.email])
                            msg.attach_alternative(html_content, "text/html")
                            try:
                                msg.send()
                            except:
                                #email failed to send
                                print "failed to send email"
                                print html_content
                                pass


    ideaForm = IdeaForm()
    inviteForm = InviteForm()
    voteUpForm = VoteForm({'vote':'+'})
    ideas = ideaForm
    participants = slate.users.all()
    slate_ideas = slate.ideas.all()
    slate_ideas = slate_ideas.order_by('-date')
    return render_to_response("main/view_slate.html", locals(),
            context_instance = RequestContext(request))

@login_required(login_url='/accounts/login/')
def convert_idea(request, idea_id):
    print "converting idea"
    idea = Idea.objects.get(id = idea_id)

    #check whether the user is the creator of the idea
    if request.user != idea.user:
        return redirect("idea", idea_id)
    #create a slate for the idea
    slate = Slate(
            creator = request.user,
            name = idea.idea,
            description = idea.elaborate
            )
    slate.save()

    #set the idea to private and add it to the slate
    slate.users.add(request.user)
    idea.private = True
    idea.started = True
    idea.save()
    slate.ideas.add(idea)
    #
    return redirect("view-slate", slate_id)

def clean_slate(request, slate_id):
    #remove ideas from slate
    slate = Slate.objects.get(id=slate_id)
    
    if request.user != slate.creator:
        return redirect("slate", slate_id)

    slate.ideas.all().delete()
    slate.save()
    return redirect("view-slate", slate_id)

def release_slate(request, slate_id):
    slate = Slate.objects.get(id=slate_id)
    #get the ideas and set each item to not private.
    if request.user != slate.creator:
        return redirect("slate", slate_id)

    ideas = slate.ideas.all()
    for idea in ideas:
        idea.private = False
        idea.save()
        slate.ideas.remove(idea)
        slate.save()
    return redirect("view-slate", slate_id)
    
