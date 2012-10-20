from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.contrib.auth.models import User

from app.models import Idea, Slate, UserProfile

import datetime

class Command(BaseCommand):
    help = ("Sends the weekly email to each user "
            ", keeping them up to date on activity in Idea Otter."
            )
    def handle(self, *args, **options):
        plaintext = get_template('email/weekly.txt')
        htmly = get_template('email/weekly.html')
        all_users = User.objects.exclude(extra__emails=False)
        for user in all_users:
            # start by finding the ideas posted by a user
            commented_on_ideas = user.get_profile().comments_on_owned_ideas(7)
            self.stdout.write("user %s\n" %user)
            for idea in commented_on_ideas:
                self.stdout.write("you've got new comments on: %s\n" % idea.idea)
            #new_slates = user.slates.all()
            new_slates = user.slates.filter(
                    date_created__gte = datetime.date.today()-datetime.timedelta(7)
                    )
            self.stdout.write("you've joined %i slates \n" % len(new_slates))
            
            d = Context({ 'user': user })
            #actually send the e-mail
            if new_slates and commented_on_ideas:
                subject, from_email, to = 'Weekly Digest', 'contact@ideaotter.com', user.email
                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                if "final" in args:
                    try:
                        msg.send()
                    except:
                        self.stdout.write("failed to send email")
                else:
                    self.stdout.write("test success")
            #user_slates = user.slates.all()
            #for slate in user_slates:
            #    self.stdout.write("slate: %s\n" % slate.name)



