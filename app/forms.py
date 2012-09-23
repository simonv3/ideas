from django import forms
from django.forms import ModelForm
from app.models import Idea

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
