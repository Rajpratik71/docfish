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

# Actions are mainly ajax requests/responses to feed into views.

from django.core.files.base import ContentFile
from notifications.signals import notify

from docfish.apps.users.utils import get_team
from docfish.apps.main.models import *
from docfish.apps.main.utils import (
    get_collection,
    get_entity,
    get_image,
    get_text
)

from docfish.settings import (
    BASE_DIR, 
    MEDIA_ROOT
)

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
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

from django.utils import timezone
from django.urls import reverse

import json
import os
import pickle
import re

media_dir = os.path.join(BASE_DIR,MEDIA_ROOT)

###############################################################################################
# Collections #################################################################################
###############################################################################################

@login_required
def flag_text(request,uid):
    text = get_text(uid)
    return flag(request,text)


@login_required
def flag_image(request,uid):
    image = get_image(uid)
    return flag(request,image)


@login_required
def flag(request,instance):
    if request.method == 'POST':
        instance.active = not instance.active
        instance.save()
        response_data = {'result':'Flag change status successfully!',
                         'status':instance.active,
                         'id': instance.id }
        return JsonResponse(response_data)
    return JsonResponse({"Unicorn poop cookies...": "I will never understand the allure."})


###############################################################################################
# Collections #################################################################################
###############################################################################################
    

@login_required
def collection_update_instruction(request,cid):
    '''update the instruction for a particular annotation or markup task
    '''
    collection = get_collection(cid)

    if request.user == collection.owner:

        if request.method == 'POST':
            instruction = request.POST.get("instruction",None)
            fieldtype = request.POST.get("fieldtype",None)
            if instruction not in ["",None] and fieldtype in collection.status:
                collection.status[fieldtype]['instruction'] = instruction
                collection.save()
                response_data = {'result':'Instruction updated',
                                 'status': instruction }
                return JsonResponse(response_data)

    return JsonResponse({"Unicorn poop cookies...": "I will never understand the allure."})
 

def serve_image_metadata(request,uid):
    '''return image metadata as json
    '''
    image = get_image(uid)
    return JsonResponse(image.metadata)


def serve_text_metadata(request,uid):
    '''return text metadata as json
    '''
    text = get_text(uid)
    return JsonResponse(text.metadata)


def serve_text(request,uid):
    '''return raw text
    '''
    text = get_text(uid)
    content = text.get_text()
    return JsonResponse({"original": content})


###############################################################################################
# Annotations #################################################################################
###############################################################################################

def update_annotation(user,allowed_annotation,instance,cid,tid=None):
    '''update_annotation will take a user, and an annotation, some instance
    (text or image) and call the appropriate function to update it.
    :param user: the user object or user id
    :param allowed_annotation: the allowed annotation object or id
    :param instance: the Image or text instance
    '''
    if not isinstance(user,User):
        user = User.objects.get(id=user)
    if not isinstance(allowed_annotation,Annotation):
        allowed_annotation = Annotation.objects.get(id=allowed_annotation)
    if isinstance(instance,Image):
        return update_image_annotation(user,allowed_annotation,instance,tid=tid,cid=cid)
    elif isinstance(instance,Text):
        return update_text_annotation(user,allowed_annotation,instance,tid=tid,cid=cid)


def update_image_annotation(user,allowed_annotation,image,cid,tid=None):
    '''update_image_annotation is called from update_annotation given that the
    user has provided an image
    '''
    if not isinstance(image,Image):
        image = Image.objects.get(id=image)
    collection = get_collection(cid)
    team = get_team(tid)

    # Remove annotations done previously by the user for the image
    if tid is not None:
        previous_annotations = ImageAnnotation.objects.filter(team=team,
                                                              image=image,
                                                              annotation__name=allowed_annotation.name)
        [x.delete() for x in previous_annotations]
        annotation = ImageAnnotation.objects.create(team=team,
                                                    collection=collection,
                                                    image=image,
                                                    annotation=allowed_annotation)

    else:
        previous_annotations = ImageAnnotation.objects.filter(creator=user,
                                                              collection=collection,
                                                              image=image,
                                                              annotation__name=allowed_annotation.name)
        [x.delete() for x in previous_annotations]
        annotation = ImageAnnotation.objects.create(creator=user,
                                                    image=image,
                                                    annotation=allowed_annotation)

    return annotation



def update_text_annotation(user,allowed_annotation,text,cid,tid=None):
    '''update_text_annotation is called from update_annotation given that the
    user has provided text
    '''
    if not isinstance(text,Text):
        text = Text.objects.get(id=text)

    collection = get_collection(cid)
    team = get_team(tid)

    if tid is not None:
        previous_annotations = TextAnnotation.objects.filter(team=team,
                                                             text=text,
                                                             collection=collection,
                                                             annotation__name=allowed_annotation.name)
        [x.delete() for x in previous_annotations]
        annotation = TextAnnotation.objects.create(team=team,
                                                   text=text,
                                                   collection=collection,
                                                   annotation=allowed_annotation)

    else:
        previous_annotations = TextAnnotation.objects.filter(creator=user,
                                                             text=text,
                                                             collection=collection,
                                                             annotation__name=allowed_annotation.name)
        [x.delete() for x in previous_annotations]
        annotation = TextAnnotation.objects.create(creator=user,
                                                   text=text,
                                                   collection=collection,
                                                   annotation=allowed_annotation)

    
    return annotation


def finalize_annotation(previous_annotations,annotation):
    '''finalize_annotation will ensure that an annotation is
    unique, meaning removing all other options.
    :param previous_annotations: any previous annotations with the same name
    :param annotation: the annotation to set/keep
    '''
    for previous in previous_annotations:
        if previous.id != annotation.id:
            previous.delete()

    return annotation


def clear_user_annotations(user,instance,cid):
    '''clear_user_annotations will remove all annotations for a user for
    an instance, whether an image or text.
    :param user: the user
    :param instance: the image or text to clear annotations for
    '''
    collection = get_collection(cid)
    try:
        if isinstance(instance,Text):
            previous_annotations = TextAnnotation.objects.filter(creator=user,
                                                                 text=instance,
                                                                 collection=collection)
        elif isinstance(instance,Image):
            previous_annotations = ImageAnnotation.objects.filter(creator=user,
                                                                  image=instance,
                                                                  collection=collection)

        [x.delete() for x in previous_annotations]

        return True
    except:
        return False


def clear_team_annotations(team,instance,cid):
    collection = get_collection(cid)
    try:
        if isinstance(instance,Text):
            previous_annotations = TextAnnotation.objects.filter(team=team,
                                                                 collection=collection,
                                                                 text=instance)
        elif isinstance(instance,Image):
            previous_annotations = ImageAnnotation.objects.filter(team=team,
                                                                  collection=collection,
                                                                  text=instance)

        [x.delete() for x in previous_annotations]
        return True
    except:
        return False



@login_required
def update_annotations(request,cid,instance):
    '''update_annotation_view is a general view to handle update of an annotation for a
    text or image instance
    '''
    if request.method == 'POST':
        try:
            new_annotations = json.loads(request.POST.get('annotations'))
            tid = request.POST.get("team_id",None)
        except:
            return JsonResponse({"error": "error parsing array!"})

        # Update the annotations
        result = {'annots':new_annotations,'tid':tid}
        pickle.dump(result,open('tmp.pkl','wb'))
        for new_annotation in new_annotations:
            if new_annotation['value'] == "on":
                aname,alabel = new_annotation['name'].split('||')
                annotation_object = Annotation.objects.get(name=aname,
                                                           label=alabel)
                annot = update_annotation(user=request.user,
                                          allowed_annotation=annotation_object,
                                          instance=instance,
                                          tid=tid,
                                          cid=cid)
        response_data = {'result':'Create post successful!'}
        return JsonResponse(response_data)

    return JsonResponse({"have you ever seen...": "a radiologist ravioli?"})



def clear_annotations(request,cid,instance):
    '''clear annotations view clears all annotations for a text or image instance
    :param instance: the text or image instance
    '''
    if request.method == 'POST':
        try:
            tid = request.POST.get("team_id",None)
            team = get_team(tid,return_none=True)
            if team is not None:
                status = clear_team_annotations(team=team,
                                                instance=image,
                                                cid=cid)
            else:
                status = clear_user_annotations(user=request.user,
                                                instance=image,
                                                cid=cid)
            response_data = {'result':'Annotations successfully cleared',
                             'status': status}
        except:
            response_data = {'result':'Error clearing annotations.'}
        return JsonResponse(response_data)
    return JsonResponse({"have you ever seen...": "a researcher rigatoni?"})


###############################################################################################
# Markup ######################################################################################
###############################################################################################


@login_required
def update_text_markup(request,cid,uid):
    '''update_text_markup will update a user's text annotation
    '''
    collection = get_collection(cid)
    text = get_text(uid)

    if request.method == 'POST':
        try:
            pickle.dump(dict(request.POST),open('tmp.pkl','wb'))
            markups = json.loads(request.POST.get('markup'))
            textstr = request.POST.get('text')
            tid = request.POST.get('team_id',None)
        except:
            return JsonResponse({"error": "error parsing markup!"})

        if tid is not None:
            team = get_team(tid)
            text_markup,created = TextMarkup.objects.get_or_create(team=team,
                                                                   text=text,
                                                                   collection=collection)
        else:
            text_markup,created = TextMarkup.objects.get_or_create(creator=request.user,
                                                                   text=text,
                                                                   collection=collection)
        text_markup.locations = {"text":textstr,"markups":markups}
        text_markup.save()
        response_data = {'result':markups}
        return JsonResponse(response_data)

    return JsonResponse({"nope...": "nopenope"})
