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

from django.contrib.auth.models import User
from django.http.response import (
    HttpResponseRedirect, 
    HttpResponseForbidden, 
    Http404
)
from django.shortcuts import (
    get_object_or_404, 
    render_to_response, 
    render, 
    redirect
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files.base import File
from docfish.apps.main.models import *
import collections
from datetime import datetime
from datetime import timedelta
from itertools import chain
from taggit.models import Tag
from numpy.random import choice
from numpy import unique
import operator
import os

from sendgrid.helpers.mail import *
import sendgrid
import os

from docfish.apps.snacks.models import (
    Snack,
    SnackBox
)

from docfish.settings import (
    DOMAIN_NAME,
    SNACK_PRICE,
    SENDGRID_API_KEY
)

def get_snack(sid):
    '''get a single snack, or return 404'''
    keyargs = {'id':sid}
    try:
        snack = Snack.objects.get(**keyargs)
    except Snack.DoesNotExist:
        raise Http404
    else:
        return snack


def get_snacks(tag_ids=None,active=True,limit=None):
    '''get_snacks will return all snacks, or snacks filtered to a set of tags
    '''
    if tag_ids != None:
        if not isinstance(tag_ids,list):
            tag_ids = [tag_ids]
        snacks = Snack.objects.filter(tags__id__in=tag_ids,active=active)
    else:    
        snacks = Snack.objects.filter(active=active)
    if limit != None:
        if limit > len(snacks):
            limit = len(snacks)

        snacks = choice(snacks,limit).tolist()
    return snacks


def get_snacks_tags(snacks=None,distinct=True,active=True):
    '''get_snacks_tags will return a list of tags for one or more snacks
    '''
    if snacks == None:
        snacks = get_snacks()

    if isinstance(snacks,Snack):
        snacks = [snacks]
    snack_ids = [snack.id for snack in snacks]
    if distinct == True:
        return Tag.objects.filter(snack__id__in=snack_ids).distinct()
    return Tag.objects.filter(snack__id__in=snack_ids)


def get_user_snacks(user,return_snackbox=False,return_ids=True, by_tag=False):
    '''get_user_snacks returns the list of snacks for a user, via the
    snackbox. If return snackbox == True, the entire snackbox is returned
    :param return_ids: return ids, only an option if not returning snackbox
    :param by_tag: takes preference to return_ids, and again can
    only be use if not returning snackbox
    '''
    snackbox,created = SnackBox.objects.get_or_create(user=user)
    if created == True:
        snackbox.save()
    if return_snackbox == True:
        return snackbox
    snacks = snackbox.snacks.filter(active=True)

    # Return a list, each with snacks and tag
    if by_tag == True:
        categories = []
        tags = get_snacks_tags(snacks)
        for tag in tags:
            entry = {'name':tag.name,
                     'id':tag.id,
                     'snacks': snacks.filter(tags=tag)}
            categories.append(entry)
        return categories

    # Does the user want ids instead?
    if return_ids == True:
        snack_ids = [x.id for x in snacks]
        return snack_ids
    return snacks


def paginate_results(objects,size,page=1):
    '''paginate results will return a subject of objects, based on a page
    of interest.
    '''
    page = int(page)
    start = (page-1)*size

    # Find the best start
    while len(objects) <= start:
        start = start - size

    # Find the best end
    end = start + size
    if end > len(objects):
        end = len(objects)

    return objects[start:end]    


def request_snack(snackbox,message=None):
    '''request_snack will send a user message to request a snack, including the snack preferences
    '''
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)
    from_email = Email("vsochat@stanford.edu")
    to_email = Email("vsochat@stanford.edu")
    subject = "[docfish] Snack Request!"
    if message == None:
        content = Content("text/plain", 
                          "User %s has requested a snack: %s/users/snacks/%s" %(user.username,DOMAIN_NAME,user.id))
    else:
        content = Content("text/plain", 
                          """User %s has requested a snack: %s/users/snacks/%s

                          %s
                          """ %(user.username,DOMAIN_NAME,user.id,message))

    mail = Mail(from_email, subject, to_email, content)
    if snackbox.gils_earned >= SNACK_PRICE:
        response = sg.client.mail.send.post(request_body=mail.get())
        snackbox.gils_earned = snackbox.gils_earned - SNACK_PRICE
        snackbox.gils_spent = snackbox.gils_spent + SNACK_PRICE
        snackbox.save()   
        #print(response.status_code)
        #print(response.body)
        #print(response.headers)

    return snackbox


def upload_snack_image(snack,image_path):
    '''add an image from the filesystem to the snack image'''
    with open(image_path,'rb') as filey:
        django_file = File(filey)
        snack.image.save(os.path.basename(image_path),
                                          django_file,save=True)  
    snack.save()
    return snack
