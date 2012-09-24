from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import user_passes_test, login_required

from app import helpers
from app.forms import SlateForm, IdeaForm, VoteForm
from app.models import Slate

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
    if request.method == 'POST':
        idea = helpers.add_idea(request, slate_id=slate.id)
    ideaForm = IdeaForm()
    voteUpForm = VoteForm({'vote':'+'})
    ideas = ideaForm
    slate_ideas = slate.ideas.all()
    return render_to_response("main/view_slate.html", locals(),
            context_instance = RequestContext(request))
