from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import logout, authenticate,login

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template import Context

from django.template.defaultfilters import slugify

from django.core.mail import EmailMultiAlternatives


from app import helpers
from app.forms import SlateForm, IdeaForm, VoteForm, InviteForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from app.models import Slate, Invitee, Idea
from django.contrib.auth.models import User, Group

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

    your_slates = Slate.objects.filter(users=request.user)
    return render_to_response("main/slate.html", locals(),
            context_instance = RequestContext(request))

@login_required(login_url='/accounts/login/')
def view_slate(request, slate_id):
    slate = Slate.objects.get(id=slate_id)
    invites = Invitee.objects.filter(slate = slate_id)
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
                    invite = invite.strip()
                    try:
                        validate_email( invite )
                    except ValidationError:
                        #not an email address, continue with next invite
                        continue
                    else:
                            # user doesn't exist
                            # create an invitee item
                            try:
                                invite = Invitee.objects.get(email = invite,
                                        slate = slate.id)
                            except Invitee.DoesNotExist:
                                pass
                            else:
                                #invite already exists, let's pass
                                continue

                            invite = Invitee.objects.create(
                                    email=invite,slate=slate)
                            invite.save()
                            link_url = request.build_absolute_uri(
                                "/invite/slate/%i/%i/%s/"%(slate.id,invite.id,slugify(slate.name))
                                )
                            subject =   (
                                    "%s invited you to a slate on "
                                    "IdeaOtter"
                                    ) %(
                                    request.user.username
                                    )
                            from_email = "Idea Otter <contact@ideaotter.com>"
                            plaintext = get_template('email/slate_invite.txt')
                            htmly = get_template('email/slate_invite.html')
                            d = Context(
                                { 
                                'username': request.user.email, 
                                'url': link_url,
                                'email': invite.email
                                }
                                )
                            text_content = plaintext.render(d)
                            html_content = htmly.render(d)
                            msg = EmailMultiAlternatives(subject, text_content,
                                    from_email, [invite.email])
                            msg.attach_alternative(html_content, "text/html")
                            try:
                                print "sending email"
                                msg.send()
                            except:
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
    slate.save()
    #
    return redirect("view-slate", slate.id)

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
        idea.save()
        slate.ideas.remove(idea)
        slate.save()
    return redirect("view-slate", slate_id)
    
def accept_invite(request, slate_id, invite_id, slate_name=""):
    slate = Slate.objects.get(id=slate_id)
    invite = Invitee.objects.get(id=invite_id)
    if request.method == 'POST':
        if 'register' in request.POST:
            data = {
                'username':request.POST['username'],
                'password1':request.POST['password1'],
                'password2':request.POST['password1'],
                }
            userCreationForm = UserCreationForm(data)
            #userCreationForm['password2'] = userCreationForm['password1']
            if userCreationForm.is_valid():
                formcd = userCreationForm.cleaned_data
                user = User.objects.create_user(
                    formcd['username'], 
                    invite.email,
                    formcd['password1'],
                    )
                user.save()
                user_in_db = authenticate(
                    username=user.username, 
                    password=formcd['password1']
                    )
                slate.users.add(user_in_db)
                verified_group = Group.objects.get(name='verified')
                user_in_db.groups.add(verified_group)
                Invitee.delete(invite)
                login(request, user_in_db)
                return redirect("view-slate", slate_id)


        elif 'verify' in request.POST:
            authenticationForm = AuthenticationForm(data=request.POST)
            if authenticationForm.is_valid():
                formcd = authenticationForm.cleaned_data
                user_in_db = authenticate(
                    username=formcd['username'], 
                    password=formcd['password']
                    )
                login(request, user_in_db)
                slate.users.add(user_in_db)
                verified_group = Group.objects.get(name='verified')

                user_in_db.groups.add(verified_group)
                Invitee.delete(invite)
                return redirect("view-slate", slate_id)

    if request.user.is_authenticated():
        #user is logged in, let's show them the slate, 
        if request.user.email == invite.email:
            #user was invited, add them to the slate. 
            slate.users.add(request.user)
            slate.save()
        else:
            #the logged in user is not the invited user
            logout(request)
            #TODO: are you maybe user (logged in user)? if so, please verify
    try:
        user = User.objects.get(email = invite.email)
    except User.DoesNotExist:
        #user doesn't exist, so let's tell them about to slate.
        user_creation = True
        form = UserCreationForm({'username':invite.email})
        return render_to_response("main/accept_invite.html", locals(),
            context_instance = RequestContext(request))
    else:
        form = AuthenticationForm(data={'username':invite.email})
        return render_to_response("main/accept_invite.html", locals(),
            context_instance = RequestContext(request))
