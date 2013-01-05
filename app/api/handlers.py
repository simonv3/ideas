from piston.handler import BaseHandler
from django.contrib.auth.models import  User
from app.models import Idea, Slate, Comment
from app.forms import IdeaForm, CommentForm
from app import helpers

from app.api.auth import key_check, secrets
from django.contrib.auth import authenticate


class UserHandler(BaseHandler):
    allowed_methods= ('GET',)
    model = User
    fields = ('username','is_active','last_login','email','date_joined','get_profile')
    def read(self, request, user_id=None):
        base = User.objects
        if user_id:

            try:
                return base.get(pk=user_id)
            except User.DoesNotExist as e:
                return {'error':e}
        else:
            return {'error':'Supply user information'}


class UserIdeasHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Idea
    fields = ((
        'user', 
        ('id', 'username', 'email', 'date_joined', 'last_login',)), 
        'idea', 'id', 'date')
    def read(self, request,  apikey, apisignature, user_id=None):
        base = Idea.objects

        query="/user/"+user_id+"/ideas/"
        #print user_id
        if not key_check(apikey, apisignature,query):
            return {'error':'authentication required'}
        elif user_id:
            return base.filter(user = user_id)
        else:
            return  {'error':'supply user information'}


class UserSlatesHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Slate
    fields = ((
        'creator', 
        ('id', 'username', 'email', 'date_joined', 'last_login',)), 
        'name', 'users' ,'id', 'date_created','description','ideas')
    def read(self, request,  apikey, apisignature, user_id=None):
        base = Slate.objects
        query="/user/"+user_id+"/slates/"
        if not key_check(apikey, apisignature,query):
            return {'error':'authentication required'}
        elif user_id:
            return base.filter(creator = user_id)
        else:
            return  {'error':'supply user information'}


class PostIdeaHandler(BaseHandler):
    allowed_methods = ('POST',)
    fields = ('id', 'idea', 
        ('user', ('id', 'username', 'email', 'date_joined', 'last_login',)),
        'date')
    model = Idea
    def create(self, request, apikey, apisignature):
        if not key_check( apikey, apisignature, '/idea/post/'):
            return {'error':'authentication failed'}
        else:
            tags = False
            try:
                ideaForm = IdeaForm({"idea_content":request.POST['idea_text'],"tags":request.POST['idea_tags']})
            except: 
                ideaForm = IdeaForm({"idea_content":request.POST['idea_text'],})
            else:
                tags = True #set tags if the user submitted them
            if ideaForm.is_valid():
                clean = ideaForm.cleaned_data
                print clean
                print request.POST['user_id']
                idea = Idea(idea=clean['idea_content'], user = User.objects.get(id = request.POST['user_id']))
                idea.save()
                if tags:
                    helpers.filter_tags(clean['tags'], idea)
                print idea
                return idea
            else:
                return {'error':'no idea'}

class CommentOnIdeaHandler(BaseHandler):
    print "handling"
    allowed_methods = ('POST',)
    fields = ('id', 'idea', 
        ('user', ('id', 'username', 'email', 'date_joined', 'last_login',)),
        'date_posted', 'text')
    model = Comment
    def create(self, request, apikey, apisignature):
        print "creating"
        if not key_check( apikey, apisignature, '/idea/comment/'):
            return {'error':'authentication failed'}
        else:
            print "elsing"
            commentForm = CommentForm({"comment":request.POST['comment']})
            if commentForm.is_valid():
                print "form valid"
                clean = commentForm.cleaned_data
                print clean
                print request.POST
                idea = Idea.objects.get(id = request.POST['idea_id'])
                print idea
                try:
                    print "trying"
                    comment = Comment(
                        text=clean['comment'], 
                        user = User.objects.get(id = request.POST['user_id']), 
                        idea = idea)
                    print comment
                except Idea.DoesNotExist:
                    return {'error':'no idea'}
                except User.DoesNotExist:
                    return {'error':'no user'}
                else:
                    comment.save()
                    #helpers.filter_tags(clean['tags'], idea)
                    print comment
                    return comment
            else:
                return {'error':'no comment'}


class IdeaHandler(BaseHandler):
    allowed_methods = ('GET',)
    fields = ('id','idea','user','date')
    model = Idea
    def read(self, request, idea_id=None):
        base = Idea.objects
        if idea_id:
            return base.get(pk=idea_id)
        else:
            return base.all()

class UserRegistrationHandler(BaseHandler):
    allowed_methods = ('POST',)
    def create(
            self, request, apikey, apisignature, 
            ):
        if not key_check(
                apikey, apisignature, 
                '/register/'):
            return {'error': 'authentication failed'}
        try: 
            User.objects.get(username=request.POST['username'])
            return {'registration' : 'failure', 'reason' : 'exists' }
        except:
            try:
                user = User.objects.create_user(request.POST['username'],'',request.POST['password'])
            except:
                return {'error':'FormPOSTError'}
            user.save()
            return user
        #return tigatag.views.login.register_basic(request, username, password, email)


class UserLogInHandler(BaseHandler):
    allowed_methods = ('POST',)
    fields = ('id', 
        'username', 
        'email', 
        'date_joined', 
        'last_login')
    def create(
            self, request, apikey, apisignature):
        if not key_check(
                apikey, apisignature, 
                '/login/'):
            return {'error': 'APIAuthFailure'}
        else:
            if request.method == "POST":
                try:
                    user_in_db = authenticate(username=request.POST['username'],password=request.POST['password'])
                except:
                    return {'error':'FormAuthError'}
                if user_in_db:
                    return user_in_db
                else:
                    return {'error':'User.DoesNotExist'}
            else:
                return {'error':'FormPOSTError'}


class AuthenticateUser(BaseHandler):
    allow_methods = ('POST',)
    model = User
