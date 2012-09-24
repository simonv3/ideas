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
from app.models import Slate
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
                        continue
                    else:
                        try:
                            user = User.objects.get(email = invite)
                        except User.DoesNotExist:
                            # user doesn't exist, send email TODO
                            pass
                        else:
                            # user exists, add them to the project
                            if slate.users.get(id=user.id):
                                #user already in project, continue with next
                                #iteration of the loop
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
                            msg.send()


    ideaForm = IdeaForm()
    inviteForm = InviteForm()
    voteUpForm = VoteForm({'vote':'+'})
    ideas = ideaForm
    participants = slate.users.all()
    slate_ideas = slate.ideas.all()
    slate_ideas = slate_ideas.order_by('-date')
    return render_to_response("main/view_slate.html", locals(),
            context_instance = RequestContext(request))
