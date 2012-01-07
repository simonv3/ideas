# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required


def splash(request):
    return render_to_response("main/splash.html", locals(),
            context_instance=RequestContext(request))

    
@login_required(login_url='/accounts/login/')
def profile(request):
    user = request.user
    print user.first_name
    return render_to_response('main/profile.html', locals(), context_instance=RequestContext(request))


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        data = request.POST.copy()
        form = UserCreationForm(request.POST)
        print form
        if form.is_valid():
            formcd = form.cleaned_data
            print formcd
            if formcd['password1'] == formcd['password2']:
                user = User.objects.create_user(formcd['username'],'',formcd['password1'])
                user.save()
                return HttpResponseRedirect("/accounts/profile/")
                
                
    else:
        data, errors = {}, {}

    return render_to_response("main/register.html", locals(),
            context_instance=RequestContext(request))

