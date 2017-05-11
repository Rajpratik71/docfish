'''

markup views

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
    Image,
    ImageMarkup
)
from docfish.apps.main.utils import *
from docfish.apps.main.navigation import (
    get_next_to_markup
)

from docfish.apps.users.utils import (
    get_user,
    get_team,
    get_team_markups
)

from docfish.apps.main.permission import (
    has_collection_annotate_permission
)


from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
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

import os
import re


######################################################################################
# Images #############################################################################
######################################################################################

@login_required 
def collection_markup_image(request,cid):
    '''collection_markup_image will return a new image to markup
    '''
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")


    if collection.has_images():
        next_image = get_next_to_markup(user=request.user,collection=collection)
        if next_image == None:
            messages.info(request,"You have finished marking up the images in this collection. Awesome!") 
            return HttpResponseRedirect(collection.get_absolute_url())

        # Has the user marked up the image previously?
        markup = get_markup(instance=next_image,
                            user=request.user,
                            collection=collection)

        # Has the image base been saved?
        missing_base = not has_image_base(next_image)

        # Pass to view if we need to save a base for the image
        context = {"entity": next_image.entity,
                   "image": next_image,
                   "markup": markup,
                   "collection":collection,
                   "missing_base":missing_base,
                   "nosidebar":"harrypottah"}

        template_type = sniff_template_extension(next_image.get_path())
        return render(request, "annotate/images_markup_%s.html" %(template_type), context)

    messages.info(request,"This collection does not have any images to markup.")
    return HttpResponseRedirect(collection.get_absolute_url())



@login_required
def markup_image(request,cid,uid=None,tid=None):
    '''markup_image will return a (free hand) annotator to markup an image.
    It is assumed that we have already chosen the image for the collection,
    and we will redirect back to the route to choose an image.
    '''
    collaborate = True
    team = get_team(tid,return_none=True)
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection,team):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    # If it's a post, save the markup
    if request.method == "POST": 

        # Retrieve base64 encoded data
        png_data = request.POST.get('pngdata',None)
        base_data = request.POST.get('pngdatabase',None)
        image_id = request.POST.get('image_id',None)
        
        if png_data and image_id is not None:

            image = get_image(image_id)
            if team is not None:
                markup,created = ImageMarkup.objects.update_or_create(team=team,
                                                                      image=image)
            else:
                markup,created = ImageMarkup.objects.update_or_create(creator=request.user,
                                                                      image=image)

            # The interface will send the base image if being annotated for first time
            if base_data not in [None,'']:
                markup = save_markup(markup=markup,
                                     overlay=png_data,
                                     base=base_data,
                                     team=team)

            # Otherwise, try to retrieve the already existing image
            else:
                base_image = get_image_base(image)
                markup = save_markup(markup=markup,overlay=png_data)
                markup.base = base_image
                markup.save()

        else:
            messages.info(request, "No markup detected. Did you annotate the image?")

    if team is not None:  

        if collection.has_images():
            if uid is None:
                collaborate = False
                image,next_image = get_next_to_markup(user=request.user,
                                                      collection=collection,
                                                      team=team,
                                                      N=2)
            else:   
                image = get_image(uid)
                next_image = get_next_to_markup(user=request.user,
                                                collection=collection,
                                                team=team,
                                                skip=image.id)
    
            markup = get_markup(user=request.user,
                                instance=image,
                                team=team,
                                collection=collection)

            # Has the image base been saved?
            missing_base = not has_image_base(image)

            # Pass to view if we need to save a base for the image
            context = {"entity": image.entity,
                       "image": image,
                       "next_image": next_image,
                       "markup": markup,
                       "collection":collection,
                       "missing_base":missing_base,
                       "nosidebar":"harrypottah",
                       "team":team}
            if collaborate:
                context['collaborate'] = "yes"

            template_type = sniff_template_extension(image.get_path())
            return render(request, "collaborate/images_markup_%s.html" %(template_type), context)
    
        messages.info(request,"This collection does not have any images to markup.")
        return HttpResponseRedirect(collection.get_absolute_url())

    return redirect("collection_markup_image", cid=cid)



######################################################################################
# Text ###############################################################################
######################################################################################

@login_required
def collection_markup_text(request,cid):
    '''collection_markup_text will return a new text to markup
    '''
    collection = get_collection(cid)

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    if collection.has_text():
        next_text = get_next_to_markup(user=request.user,
                                       collection=collection,
                                       get_images=False)
 
        if next_text == None:
            messages.info(request,"You have finished marking up the text in this collection. Shaaawing!") 
            return redirect('collection_details',cid=cid)

        # Has the user marked up the image previously?
        markup = get_markup(instance=next_text,
                            user=request.user,
                            collection=collection)

        # Pass to view if we need to save a base for the image
        context = {"entity": next_text.entity,
                   "text": next_text,
                   "markup": markup,
                   "nosidebar":"ronweesley!",
                   "collection":collection}

        return render(request, "annotate/text_markup.html", context)

    messages.info(request,"This collection does not have any text to markup.")
    return redirect('collection_details',cid=cid)



@login_required
def markup_text(request,cid,uid=None,tid=None):
    '''markup_text will return a highlighter to markup a text.
    '''   
    collection = get_collection(cid)
    team = get_team(tid,return_none=True)
    collaborate = True

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")


    if team is not None:  

        if collection.has_text():
            if uid is None:
                collaborate = False
                text,next_text = get_next_to_markup(user=request.user,
                                                    collection=collection,
                                                    team=team,
                                                    get_images=False,
                                                    N=2)
            else:   
                text = get_text(uid)
                next_text = get_next_to_markup(user=request.user,
                                               collection=collection,
                                               team=team,
                                               get_images=False,
                                               skip=text.id)
    
            markup = get_markup(user=request.user,
                                instance=text,
                                team=team,
                                collection=collection)

            # Pass to view if we need to save a base for the image
            context = {"entity": next_text.entity,
                       "text": text,
                       "next_text": next_text,
                       "markup": markup,
                       "nosidebar":"ronweesley!",
                       "collection":collection,
                       "team":team}

            if collaborate:
                context['collaborate'] = "yes"

            return render(request, "collaborate/text_markup.html", context)
    
        messages.info(request,"This collection does not have any text to markup.")
        return HttpResponseRedirect(collection.get_absolute_url())

    return redirect("collection_markup_text", cid=cid)
