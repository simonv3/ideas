from django import forms
from django.forms import ModelForm
from app.models import Idea, UserProfile

# CREATE FORMS HERE

class IdeaForm(forms.Form):
    idea_content = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(max_length=240,required=False)
    elaborate = forms.CharField(widget=forms.Textarea,required=False)
    private = forms.BooleanField(required=False)

class VoteForm(forms.Form):
    vote = forms.CharField(widget=forms.HiddenInput)
    idea = forms.CharField(widget=forms.HiddenInput)

class VoteDownForm(forms.Form):
    vote = forms.CharField(widget=forms.HiddenInput)
    idea = forms.CharField(widget=forms.HiddenInput)

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)

class EmailForm(forms.Form):
    email = forms.EmailField()

class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())
    repeat_password = forms.CharField(widget=forms.PasswordInput())

class SearchForm(forms.Form):
    query = forms.CharField(max_length=240)

class SlateForm(forms.Form):
    name = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)

class InviteForm(forms.Form):
    invite_list = forms.CharField(widget=forms.Textarea)

class ProfileForm(forms.ModelForm):
        class Meta:
            model = UserProfile
            exclude = ('user')

