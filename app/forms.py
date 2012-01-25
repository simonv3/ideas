from django import forms
from django.forms import ModelForm
from app.models import Idea

# CREATE FORMS HERE

class IdeaForm(forms.Form):
    idea = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(widget=forms.Textarea,required=False)

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

