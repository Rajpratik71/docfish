'''

annotate views

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

from docfish.apps.main.models import *

from docfish.apps.main.permission import (
    has_collection_annotate_permission,
    has_collection_edit_permission
)

from docfish.apps.main.utils import *
from docfish.apps.main.navigation import (
    get_next_to_annotate
)

from docfish.apps.main.actions import (
    clear_annotations,
    update_annotations
)

from docfish.apps.users.utils import (
    get_user,
    get_team,
    get_team_annotations
)

from django.contrib.auth.decorators import login_required
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

from docfish.apps.main.permission import (
    has_collection_annotate_permission,
    has_collection_edit_permission
)

# Annotate

@login_required
def collection_annotate_image(request,cid):
    '''annotate_image is the view for an image annotation interface for a particular report id
    '''
    team = get_team(tid,return_none=True)
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_images():

        next_image = get_next_to_annotate(user=request.user,
                                          collection=collection)
        if next_image == None:
            messages.info(request,"You have finished annotating the images in this collection. Woot!") 
            return HttpResponseRedirect(collection.get_absolute_url())

        annotations = get_annotations(user=request.user,
                                      instance=next_image)

        allowed_annotations = collection.get_annotations()

        context = { "entity": next_image.entity,
                    "image": next_image,
                    "collection":collection,
                    "annotations": annotations['labels'],
                    "counts": annotations['counts'],
                    "nosidebar":"pizzapizza",
                    "allowed_annotations": allowed_annotations}

        template_type = sniff_template_extension(next_image.get_path())
        return render(request, "annotate/images_annotate_%s.html" %(template_type), context)

    messages.info(request,"This collection does not have any images to annotate.")
    return redirect('collection_details',cid=cid)



@login_required
def clear_image_annotations(request,uid):
    '''clear all annotations for a specific image'''
    image = Image.objects.get(id=uid)
    return clear_annotations(request,instance=image)


@login_required
def update_image_annotation(request,uid,tid=None):
    '''update_image_annotation is the view to update an annotation when it changes. 
    It should return a JSON response.
    Given a team annotation, the team_id should be in the request.POST
    '''
    image = Image.objects.get(id=uid)
    return update_annotations(request,instance=image)



@login_required
def collection_annotate_text(request,cid):
    '''annotate_text is the view for a text annotation interface for a particular text id
    :param uid: if not None, this is a team annotation, and the url is associated with the page
    :param tid: the team id, will be present for a particular uid
    '''
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_text():
        next_text = get_next_to_annotate(user=request.user,
                                         collection=collection,
                                         get_images=False)

        if next_text == None:
            messages.info(request,"You have finished annotating the text in this collection. Eggcellent!") 
            return redirect('collection_details',cid=cid)

        annotations = get_annotations(user=request.user,
                                      instance=next_text)

        allowed_annotations = collection.get_annotations()

        context = { "entity": next_text.entity,
                    "text": next_text,
                    "collection":collection,
                    "annotations": annotations['labels'],
                    "counts": annotations['counts'],
                    "nosidebar":"pizzapizza",
                    "allowed_annotations": allowed_annotations}
 
        return render(request, "annotate/text_annotate.html", context)

    messages.info(request,"This collection does not have any text to annotate.")
    return HttpResponseRedirect(collection.get_absolute_url())



# Team annotation

@login_required
def team_annotate_text(request,cid,tid,uid=None):
    '''team_annotate_text is the view for a text annotation interface for a team. If
    a text id (uid) is provided, this is the text returned. If not, it is assumed this
    if the first text being annotated
    '''
    collection = get_collection(cid)
    team = get_team(tid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection,team):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_text():

        collaborate = True
        if uid is None:
            collaborate = False
            text,next_text = get_next_to_annotate(user=request.user,
                                                  collection=collection,
                                                  get_images=False,
                                                  team=team,
                                                  N=2)
        else:
            collaborate = True
            text = get_text(uid) 
            next_text = get_next_to_annotate(user=request.user,
                                             collection=collection,
                                             get_images=False,
                                             team=team,
                                             skip=text.id)
        
        annotations = get_annotations(user=request.user,
                                      instance=text,
                                      team=team)

        allowed_annotations = collection.get_annotations()

        context = { "entity": text.entity,
                    "next_text": next_text,
                    "text": text,
                    "collection":collection,
                    "annotations": annotations['labels'],
                    "counts": annotations['counts'],
                    "nosidebar":"pizzapizza",
                    "allowed_annotations": allowed_annotations,
                    "team":team}

        if collaborate:
            context['collaborate'] = "yes"
 
        return render(request, "collaborate/text_annotate.html", context)

    messages.info(request,"This collection does not have any text to annotate.")
    return HttpResponseRedirect(collection.get_absolute_url())


@login_required
def team_annotate_image(request,cid,tid,uid=None):
    team = get_team(tid,return_none=True)
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_images():

        collaborate = True
        if uid is None:
            collaborate = False
            image,next_image = get_next_to_annotate(user=request.user,
                                                    collection=collection,
                                                    team=team,
                                                    N=2)
        else:
            image = get_image(uid)
            next_image = get_next_to_annotate(user=request.user,
                                              collection=collection,
                                              team=team,
                                              skip=image.id)
        
        annotations = get_annotations(user=request.user,
                                      instance=image,
                                      team=team)

        allowed_annotations = collection.get_annotations()

        context = { "entity": image.entity,
                    "image": image,
                    "next_image": next_image,
                    "collection": collection,
                    "annotations": annotations['labels'],
                    "counts": annotations['counts'],
                    "nosidebar":"pizzapizza",
                    "allowed_annotations": allowed_annotations,
                    "team": team}

        if collaborate:
            context['collaborate'] = "yepp"

        template_type = sniff_template_extension(next_image.get_path())
        return render(request, "collaborate/images_annotate_%s.html" %(template_type), context)

    messages.info(request,"This collection does not have any images to annotate.")
    return redirect('collection_details',cid=cid)


@login_required
def clear_text_annotations(request,uid):
    '''clear all annotations for a specific image'''

    text = Text.objects.get(id=uid)
    return clear_annotations(request,instance=text)


@login_required
def update_text_annotation(request,uid):
    '''update_text_annotation is the view to update an annotation when it changes. 
    It should return a JSON response.
    '''
    text = Text.objects.get(id=uid)
    return update_annotations(request,instance=text)


