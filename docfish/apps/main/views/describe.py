'''

describe views

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

from docfish.apps.main.models import (
    ImageDescription,
    TextDescription
)

from docfish.apps.main.utils import *
from docfish.apps.main.permission import has_collection_annotate_permission
from docfish.apps.main.navigation import get_next_to_describe

from docfish.apps.users.utils import (
    get_team,
    get_team_descriptions
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



@login_required
def collection_describe_image(request,cid):
    '''collection_describe_image will return a new image to describe
    '''
    collection = get_collection(cid)
    
    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_images():
        
        next_image = get_next_to_describe(user=request.user,
                                          collection=collection)

        # Next image will never be none for a team, keeps cycling
        if next_image == None:
            messages.info(request,"You have finished describing images in this collection. Great work!") 
            return HttpResponseRedirect(collection.get_absolute_url())

        description = get_description(user=request.user,
                                      instance=next_image)
    
        # Pass to view if we need to save a base for the image
        context = {"entity":next_image.entity,
                   "image": next_image,
                   "collection":collection,
                   "description": description,
                   "nosidebar":"pancakes"}
    
        template_type = sniff_template_extension(next_image.get_path())
        return render(request, "annotate/images_description_%s.html" %(template_type), context)

    messages.info(request,"This collection does not have any images to describe.")
    return HttpResponseRedirect(collection.get_absolute_url())


@login_required
def video_describe_web(request):
    '''clear all annotations for a specific image'''
    tid=1
    context = {'collaborate':'yes'}
    team = get_team(tid,return_none=True)
    return render(request, "collaborate/video_describe_web.html", context)



@login_required
def describe_image(request,cid,uid=None,tid=None):
    '''describe_image will return a static view of an image to describe.
    :param uid: the unique id of the image. This is always the image id that is desired to be 
    seen. In the case of a post, the last image's uid is obtained from the post data. 
    If this is a team description (tid is provided) the view returns uid. If not, the user
    is redirected to the collection_describe_image that will randomly select the next. 
    '''
    collaborate = True
    collection = get_collection(cid)
    team = get_team(tid,return_none=True)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection,team):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    # If it's a post, save the description
    if request.method == "POST": 

        # Retrieve base64 encoded data
        description_text = request.POST.get('description',None)
        image_id = request.POST.get('image_id',None)

        if description_text not in [None,''] and image_id not in [None,'']:
            if team is not None:
                description,created = ImageDescription.objects.get_or_create(team=team,
                                                                             image__id=image_id,
                                                                             description=description_text)
            else:
                description,created = ImageDescription.objects.get_or_create(creator=request.user,
                                                                             image__id=image_id,
                                                                             description=description_text)
            description.save()


    # Team description has (somewhat) controlled movement through images
    if team is not None:  

        if collection.has_images():
            if uid is None:
                collaborate = False
                image,next_image = get_next_to_describe(user=request.user,
                                                        collection=collection,
                                                        team=team)
            else:   
                image = get_image(uid)
                next_image = get_next_to_describe(user=request.user,
                                                  collection=collection,
                                                  team=team,
                                                  skip=image.id)
    
            description = get_description(user=request.user,
                                          instance=image,
                                          team=team)
    
            # Pass to view if we need to save a base for the image
            context = {"entity":image.entity,
                       "image": image,
                       "next_image": next_image,
                       "collection": collection,
                       "description": description,
                       "nosidebar":"pancakes",
                       "team":team}
            if collaborate:
                context["collaborate"] = "yes"
    
            template_type = sniff_template_extension(image.get_path())
            return render(request, "collaborate/images_description_%s.html" %(template_type), context)

        messages.info(request,"This collection does not have any images to describe.")
        return HttpResponseRedirect(collection.get_absolute_url())

    # Regular markup (no team)
    return redirect("collection_describe_image", cid=collection.id)



# Text

@login_required
def collection_describe_text(request,cid):
    collection = get_collection(cid)
    
    if collection.private == True:
        if not has_collection_annotate_permission(request,collection,team):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_text():
        next_text = get_next_to_describe(user=request.user,
                                         collection=collection,
                                         get_images=False)
        if next_text == None:
            messages.info(request,"You have finished describing the text in this collection. Thanks!") 
            return redirect('collection_details',cid=cid)

        description = get_description(user=request.user,
                                      instance=next_text)
    
        # Pass to view if we need to save a base for the image
        context = {"entity":next_text.entity,
                   "text": next_text,
                   "collection":collection,
                   "description": description,
                   "nosidebar":"pancakes"}

        return render(request, "annotate/text_description.html", context)

    messages.info(request,"This collection does not have any text to describe.")
    return HttpResponseRedirect(collection.get_absolute_url())



@login_required
def describe_text(request,cid,uid=None,tid=None):
    '''describe_text will return a static view of text to describe. 
    '''
    collaborate = True
    team = get_team(tid,return_none=True)
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if request.method == "POST": 

        # Retrieve base64 encoded data
        description_text = request.POST.get('description',None)
        text_id = request.POST.get('text_id',None)

        if description_text not in [None,''] and text_id not in [None,'']:
            if team:
                description,created = TextDescription.objects.get_or_create(team=team,
                                                                            text__id=text_id,
                                                                            description=description_text) 
            else:
                description,created = TextDescription.objects.get_or_create(creator=request.user,
                                                                            text__id=text_id,
                                                                            description=description_text)
            description.save()

    # Team description has (somewhat) controlled movement through texts
    if team is not None:  

        if collection.has_text():
            if uid == None:
                collaborate = False
                text, next_text = get_next_to_describe(user=request.user,
                                                       collection=collection,
                                                       team=team,
                                                       N=2,
                                                       get_images=False)
            else:
                text = get_text(uid)
                next_text = get_next_to_describe(user=request.user,
                                                 collection=collection,
                                                 team=team,
                                                 get_images=False,
                                                 skip=text.id)

            description = get_description(user=request.user,
                                          instance=text,
                                          team=team)
    
            # Pass to view if we need to save a base for the image
            context = {"entity":text.entity,
                       "text": text,
                       "next_text": next_text,
                       "collection": collection,
                       "description": description,
                       "nosidebar":"pancakes",
                       "team":team}

            if collaborate:
                context["collaborate"] = "yes"
            return render(request, "collaborate/text_description.html", context)

        messages.info(request,"This collection does not have any texts to describe.")
        return HttpResponseRedirect(collection.get_absolute_url())

    return redirect("collection_describe_text", cid=collection.id)
