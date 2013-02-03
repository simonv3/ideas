from piston.handler import BaseHandler
from django.contrib.auth.models import  User
from django.db.models import Count
from django.contrib.auth import authenticate

from app.models import Idea, Slate, Comment, Vote
from app.forms import IdeaForm, CommentForm
from app import helpers


from app.api.auth import key_check, secrets

class UserHandler(BaseHandler):
    model = User
    # model = User
    fields = ('id','username','is_active','last_login','email','date_joined','extra')
    def read(self, request, user_id=None):
        base = User.objects
        if user_id:
            try:
                return base.get(pk=user_id)
            except User.DoesNotExist as e:
                return {'error':e}
        else:
            return {'error':'Supply user information'}

class IdeasHandler(BaseHandler):
    model = Idea
    fields = ((
        'user', 
        ('id', 'username', 'email', 'date_joined', 'last_login',)), 
        'idea', 'id', 'date', 'elaborate')

    def read(self, request, user_id, fetch_all, apikey=None, apisignature=None):
        """
        Returns all Ideas by a user if user_id is given, else it returns all Ideas
        """
        base = Idea.objects
        if user_id:
            query="/user/"+user_id+"/"+fetch_all+"/ideas/"
            if not key_check(apikey, apisignature,query):
                return {'error':'authentication required'}
            else:
                user = User.objects.get(id=user_id)
                if fetch_all == "0":
                    all_ideas = helpers.process_ideas(user, base.filter(user = user_id).annotate(votes=Count('vote_on')))
                else:
                    all_ideas = helpers.process_ideas(user, base.exclude(private = True).annotate(votes=Count('vote_on')))

                return all_ideas

    def create(self, request, apikey, apisignature):
        """
        Creates an Idea
        """
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
                idea = Idea(idea=clean['idea_content'], user = User.objects.get(id = request.POST['user_id']))
                idea.save()
                if tags:
                    helpers.filter_tags(clean['tags'], idea)
                if request.POST['slate']:
                    slate = Slate.objects.get(id=request.POST['slate'])
                    slate.ideas.add(idea)
                    slate.save()

                return idea
            else:
                return {'error':'no idea'}

    def delete(self, request, apikey, apisignature, idea_id, user_id):
        """
        Deletes an idea
        """
        try:
            idea = Idea.objects.get(id=idea_id)
        except Idea.DoesNotExist:
            return {'error':'idea didn\'t exist'}
        else:
            if not user_id == idea.user.id:
                idea.delete()
                return {'success':'idea deleted'}
            else:
                return {'error':'wrong owner'}
        




class SlatesHandler(BaseHandler):
    model = Slate
    fields = (
        ('creator', 
        ('id', 'username', 'email', 'date_joined', 'last_login',)), 
        'name', 
        ('users', ('id','username')),
        'id', 'date_created','description','ideas')
    def read(self, request,  apikey, apisignature, user_id=None):
        base = Slate.objects
        query="/user/"+user_id+"/slates/"
        if not key_check(apikey, apisignature,query):
            return {'error':'authentication required'}
        elif user_id:
            return base.filter(creator = user_id)
        else:
            return  {'error':'supply user information'}

class VoteHandler(BaseHandler):
    model = Vote
    def read(self, request, idea_id, user_id, vote_value, apikey, apisignature):
        print vote_value
        """
        POST a vote
        """
        base = Vote.objects
        try:
            user = User.objects.get(id=user_id)
            idea = Idea.objects.get(id=idea_id)
        except:
            return {'error':'idea or user not found'}
        else:
            try:
                #check if the vote already exists
                vote = Vote.objects.get(user = user, idea = idea)
            except:
                vote = Vote(vote = vote_value, user = user, idea = idea)
                vote.save()
                return {'success':'true'}
            else:
                vote.delete()
                return {'success':'false'}




class CommentHandler(BaseHandler):
    fields = ('id', 'idea', 
        ('user', ('id', 'username', 'email', 'date_joined', 'last_login',)),
        'date_posted', 'text')
    model = Comment
    def read(self, request, apikey, apisignature, idea_id=None):
        """
        GET all comments on an idea.
        """
        base = Comment.objects
        if idea_id:
            query = "/idea/"+idea_id+"/comments/"
            if not key_check(apikey, apisignature,query):
                return {'error':'authentication required'}
            else:
                return base.filter(idea = idea_id)
        else:
            return  {'error':'supply idea information'}   
    def create(self, request, apikey, apisignature):
        print "creating"
        if not key_check( apikey, apisignature, '/idea/comment/'):
            return {'error':'authentication failed'}
        else:
            print 
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
                        text = clean['comment'], 
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

class UserRegistrationHandler(BaseHandler):
    def create(
            self, request, apikey, apisignature, 
            ):
        if not key_check(
                apikey, apisignature, 
                '/register/'):
            return {'error': 'authentication failed'}
        try: 
            User.objects.get(username=request.POST['username'])
            return {'error' : 'exists' }
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

