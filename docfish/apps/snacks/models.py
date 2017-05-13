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
from taggit.managers import TaggableManager

from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models

from docfish.settings import (
    MEDIA_ROOT,
    SNACK_PRICE
)

import collections
import operator
import os


#######################################################################################################
# Supporting Functions and Variables ##################################################################
#######################################################################################################


# Get path to where images are stored for snacks
def get_image_path(instance, filename):
    snack_folder = os.path.join(MEDIA_ROOT,'snacks')
    if not os.path.exists(snack_folder):
        os.mkdir(snack_folder)
    # This is relative to media root
    return os.path.join('snacks', filename)

ACTIVE_CHOICES = ((False, 'Inactive. The snack is not available for selection.'),
                  (True, 'Active. The snack is available for selection.'))


#######################################################################################################
# Snacks ##############################################################################################
#######################################################################################################

class Snack(models.Model):
    '''A snack is a delicious prize awarded for obtaining docfish gils
    '''
    name = models.CharField(max_length=250, null=False, blank=False,verbose_name="Snack Name")
    url = models.CharField(max_length=1000, null=False, blank=False,verbose_name="Snack URL")

    image = models.ImageField(upload_to=get_image_path,null=True,blank=True, 
                              help_text="saved snack image", verbose_name="Snack Image URL")
    
    gils = models.PositiveIntegerField(blank=True,null=True,verbose_name="price of the snack.", default=100)
    tags = TaggableManager()

    active = models.BooleanField(choices=ACTIVE_CHOICES, 
                                 default=True,
                                 verbose_name="Is the snack available for selection?")

    def __str__(self):
        return "%s" %(self.name)

    def __unicode__(self):
        return "%s" %(self.name)

    def get_absolute_url(self):
        return_cid = self.id
        return reverse('snack_details', args=[str(return_cid)])

    def get_label(self):
        return "snacks"

    class Meta:
        app_label = 'snacks'


class SnackBox(models.Model):
    '''The snackbox shows a user's snack preferences
    '''
    user = models.OneToOneField(User,null=False, blank=False)
    gils_earned = models.PositiveIntegerField(default=0,verbose_name="points the user has earned")
    gils_spent = models.PositiveIntegerField(default=0,verbose_name="points the user has used")
    snacks = models.ManyToManyField(Snack, 
                                    related_name="user_snacks",
                                    related_query_name="user_snacks", blank=True, 
                                    help_text="A user's chosen snacks.")
                                    
    def __str__(self):
        return "%s" %(self.id)

    def __unicode__(self):
        return "%s" %(self.id)

    def earned_snack(self):
        if self.gils_earned >= SNACK_PRICE:
            return True
        return False


    def get_absolute_url(self):
        return_cid = self.user.id
        return reverse('my_snacks', args=[str(return_cid)])

    def get_label(self):
        return "snacks"

    class Meta:
        app_label = 'snacks'
