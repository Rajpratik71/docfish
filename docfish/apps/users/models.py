'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models

from docfish.apps.main.models import (
    Collection
)

from docfish.settings import MEDIA_ROOT

import collections
import operator
import os


#######################################################################################################
# Supporting Functions and Variables ##################################################################
#######################################################################################################


# Create a token for the user when the user is created (with oAuth2)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Get path to where images are stored for teams
def get_image_path(instance, filename):
    team_folder = os.path.join(MEDIA_ROOT,'teams')
    if not os.path.exists(team_folder):
        os.mkdir(team_folder)
    return os.path.join('teams', filename)


#######################################################################################################
# Teams ###############################################################################################
#######################################################################################################


class Team(models.Model):
    '''A user team is a group of individuals that are annotating reports together. They can be reports across collections, or 
    institutions, however each user is only allowed to join one team.
    '''
    name = models.CharField(max_length=250, null=False, blank=False,verbose_name="Team Name")
    created_at = models.DateTimeField('date of creation', auto_now_add=True)
    updated_at = models.DateTimeField('date of last update', auto_now=True)
    team_image = models.ImageField(upload_to=get_image_path, blank=True, null=True)    
    metrics_updated_at = models.DateTimeField('date of last calculation of rank and annotations',blank=True,null=True)
    ranking = models.PositiveIntegerField(blank=True,null=True,
                                          verbose_name="team ranking based on total number of annotations, calculated once daily.")
    annotation_count = models.IntegerField(blank=False,null=False,
                                           verbose_name="team annotation count, calculated once daily.",
                                           default=0)
    members = models.ManyToManyField(User, 
                                     related_name="team_members",
                                     related_query_name="team_members", blank=True, 
                                     help_text="Members of the team. By default, creator is made member.")
                                     # would more ideally be implemented with User model, but this will work
                                     # we will constrain each user to joining one team on view side

    def __str__(self):
        return "<%s:%s>" %(self.id,self.name)

    def __unicode__(self):
        return "<%s:%s>" %(self.id,self.name)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('team_details', args=[str(return_cid)])

    def get_label(self):
        return "users"

    class Meta:
        app_label = 'users'
