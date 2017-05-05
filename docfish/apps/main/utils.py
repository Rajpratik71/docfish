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
from django.contrib.auth.models import User
from django.core.files.uploadedfile import (
    UploadedFile, 
    InMemoryUploadedFile
)

from django.core.files.base import ContentFile
from django.core.files import File
from django.db.models.aggregates import Count
from itertools import chain

from docfish.apps.main.models import *
from base64 import b64decode
from docfish.settings import MEDIA_ROOT
from random import randint
from numpy.random import shuffle
import numpy
import json
import operator
import pandas
import shutil
import os
import re


#### GETS #############################################################

def get_entity(eid):
    keyargs = {'id':eid}
    try:
        entity = Entity.objects.get(**keyargs)
    except Entity.DoesNotExist:
        raise Http404
    else:
        return entity


def get_image(uid):
    keyargs = {'id':uid}
    try:
        image = Image.objects.get(**keyargs)
    except Image.DoesNotExist:
        raise Http404
    else:
        return image


def get_text(uid):
    keyargs = {'id':uid}
    try:
        text = Text.objects.get(**keyargs)
    except Text.DoesNotExist:
        raise Http404
    else:
        return text


def get_collection(cid):
    '''get a single collection, or return 404'''
    keyargs = {'id':cid}
    try:
        collection = Collection.objects.get(**keyargs)
    except Collection.DoesNotExist:
        raise Http404
    else:
        return collection


def get_collection_users(collection):
    '''get_collection_users will return a list of all owners and contributors for
    a collection
    :param collection: the collection object to use
    '''
    contributors = collection.contributors.all()
    owner = collection.owner
    return list(chain(contributors,[owner]))


def get_annotations(instance,user=None,team=None,return_dict=True):
    '''get_annotations will return the Annotation objects for a user and image.
    :param user: the user to return objects for
    :param image: the image to find annotations for
    :param return_dict: if True, convert Annotation objects to dictionary
    '''
    annotations = []
    if user is None and team is None:
        return annotations

    if team is not None:
        annotations = get_team_annotations(instance,team)
    else:
        annotations = get_user_annotations(instance,user)

    if return_dict == True:
        annotations = summarize_annotations(annotations)   
    return annotations


def get_user_annotations(instance,user):
    '''perform a query to retrieve and count image or text annotations for a user'''
    if isinstance(instance,Image):
        counter = Count('annotation_of_image', distinct=True)
        annotations = Annotation.objects.filter(annotation_of_image__image_id=instance.id,
                                                annotation_of_image__creator=user).annotate(counter)
    else:
        counter = Count('annotation_of_text', distinct=True)
        annotations = Annotation.objects.filter(annotation_of_text__text_id=instance.id,
                                                annotation_of_text__creator=user).annotate(counter)
    return annotations


def get_team_annotations(instance,team):
    '''perform a query to retrieve and count image or text annotations for a team'''
    if isinstance(instance,Image):
        counter = Count('annotation_of_image', distinct=True)
        annotations = Annotation.objects.filter(annotation_of_image__image_id=instance.id,
                                                annotation_of_image__team=team).annotate(counter)
    else:
        counter = Count('annotation_of_text', distinct=True)
        annotations = Annotation.objects.filter(annotation_of_text__text_id=instance.id,
                                                annotation_of_text__team=team).annotate(counter)
    return annotations



def summarize_annotations(annotations):
    '''summarize_annotations will return a list of annotations for an image, with key value
    corresponding to name:label, and also include the count for each. This function is typically
    called by get_annotations after the annotations have been "annotated" with counts.
    :param annotations: a list (queryset) of annotations
    '''
    summary = dict()
    counts = dict()
    for annotation in annotations:
        summary[annotation.annotation.name] = annotation.annotation.label
        counts[annotation.annotation.name] = annotation.annotation__count
    result = {"labels":summary,
              "counts":counts}
    return result


###########################################################################################
## SELECTION ALGORITHMS
###########################################################################################

def sniff_template_extension(filename):
    '''sniff_extension will determine the extension, and return a descriptor
    for the correct template.
    '''
    template_type = None

    # standard web format
    if re.search('.png$|.jpg$|.jpeg|.tiff|.gif',filename.lower()):
        template_type = "web"

    elif re.search('.dcm$',filename.lower()):
        template_type = "dicom"

    elif re.search('.nii$|.nii.gz$',filename.lower()):
        template_type = "nifti"

    elif filename.lower().endswith('pdf'):
        template_type = "pdf"

    return template_type



###########################################################################################
## Papaya params
###########################################################################################

def get_image_basepath(image,full_path=False):
    '''get_base_image determines if a base image is saved for an image. This is to later match
    it to it's overlay.
    :param full_path: returns full path (False)
    '''
    filename = get_upload_folder(image,"base-%s.png" %(image.uid))
    filename_path = "%s/%s" %(MEDIA_ROOT,filename)
    if os.path.exists(filename_path):
        if full_path:
            return filename_path
        return filename
    return None


def has_image_base(image):
    '''has_base_image returns a boolean value for get_image_basepath to determine
    if the base image has been saved
    '''
    #TODO: need to think about if we should save base for web ready images... no?
    if isinstance(image,ImageFile):
        if get_image_basepath(image) is not None:
            return True
        return False
    return True


def get_image_base(image):
    '''get image base will return the ContentFile for a particular
    image.
    :param image: the image to get the base for
    '''
    image_base = None
    image_basepath = get_image_basepath(image)
    contenders = ImageMarkup.objects.filter(base=image_basepath)
    if len(contenders) > 0:
        image_base = contenders[0].base
    return image_base


def save_markup(markup,overlay=None,base=None):
    '''save markup is intended to be used to save png data to a markup.
    It handles naming the file based on the user, and adding optional
    png data
    :param markup: the markup object
    :param overlay: the png data of the overlay to save
    :param base: the base image to save
    '''
    markup_name = "%s-%s.png" %(markup.creator.username,markup.image.uid)
    if overlay != None:
        if markup.overlay != None:
            markup.overlay.delete()
        markup.overlay.save(markup_name, ContentFile(png2base64(overlay)))
    if base != None:
        if markup.base != None:
            markup.base.delete()
        markup.base.save("base-%s.png" %(markup.image.uid), ContentFile(png2base64(base)))
    return markup

def png2base64(data):
    data = data.split(',')[1]
    return b64decode(data)


def get_markup(instance,user,team=None):
    '''get_markup will return a user's markup of an image, if it exists.
    otherwise, None is returned.
    :param image: the image object
    :param user: the user to get the markup for
    '''
    markup = None
    if isinstance(instance,Image):
        if team is not None:
            markups = ImageMarkup.objects.filter(image=instance,team=team).first()
        else:
            markups = ImageMarkup.objects.filter(image=instance,creator=user).first()
    elif isinstance(instance,Text):
        if team is not None:
            markups = TextMarkup.objects.filter(text=instance,team=team).first()
        else:
            markups = TextMarkup.objects.filter(text=instance,creator=user).first()
    return markup


def get_description(user,instance,team=None):
    '''get_description will return a user's description of an 
    image or text, if it exists.
    otherwise, None is returned.
    :param image: the image object
    :param user: the user to get the markup for
    '''
    description = None
    if isinstance(instance,Image):
        if team is not None:
            description = ImageDescription.objects.filter(image=instance,team=team).first()
        else:
            description = ImageDescription.objects.filter(image=instance,creator=user).first()
    elif isinstance(instance,Text):
        if team is not None:
            description = TextDescription.objects.filter(text=instance,team=team).first()
        else:
            description = TextDescription.objects.filter(text=instance,creator=user).first()
    return description


def filter_collection_start(collection,filters):
    '''filter collection start will return the collection.status entries
    that are present in a particular list.
    '''
    status = dict()
    for fieldtype, fieldvalues in collection.status.items():
        if fieldtype in filters:
            status[fieldtype] = fieldvalues
    return status
