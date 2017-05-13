'''

labels views

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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.http.response import (
    HttpResponseRedirect, 
    HttpResponseForbidden, 
    Http404
)

from docfish.apps.users.utils import get_team
from docfish.apps.main.models import Annotation
from docfish.apps.main.utils import get_collection
from docfish.apps.main.permission import (
    has_collection_edit_permission
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
# Annotation Labels
######################################################################################

def view_label(request,cid,tid=None):
    '''view_label is a general template to return a view of labels
    '''
    collection = get_collection(cid)
    team = get_team(tid,return_none=True)

    if has_collection_edit_permission(request,collection):

        # Labels associated with collection
        collection_labels = collection.allowed_annotations.all()
        labels = [x for x in Annotation.objects.all() if x not in collection_labels]

        context = {'labels':labels,
                   'collection':collection,
                   'collection_labels':collection_labels,
                   'team':team}

        # send back json response success
        return render(request,'collections/new_collection_label.html', context)

    messages.info(request, "You do not have permission to perform this action.")
    return HttpResponseRedirect(collection.get_absolute_url())
    

@login_required
def create_label(request,cid,lid=None):
    '''create_label will allow a user to create a new label to be associated with a collection. The user
    will be able to select from other collection labels
    :param cid: the collection id to associate the label with (not required, but no url accessible for it) 
    :param lid: if provided on a post, the label will be added to the collection as an allowed annotation
    '''
    collection = get_collection(cid)

    if request.method == "POST":
        if request.user == collection.owner:

            # If lid is defined, we are adding an already existing annotation label to collection
            if lid is not None:
                try:
                    allowed_annotation = Annotation.objects.get(id=lid)
                    collection.allowed_annotations.add(allowed_annotation)
                    collection.save()
                    label_name = "%s:%s" %(allowed_annotation.name,
                                           allowed_annotation.label)
                    response_text = {"result": "New annotation label %s added successfully." %(label_name)}
                except BaseException as e:
                    response_text = {"error": "Error retrieving allowed annotation %s, %s" %(lid,e.message)}
                return JsonResponse(response_text)

            # The user wants a new one
            else:
                name = request.POST.get('annotation_name', None)
                if name is not None:
                    for key in request.POST.keys():
                        if re.search('annotation_label',key):
                            new_label = request.POST.get(key).upper()
                            allowed_annot,created = Annotation.objects.get_or_create(name=name,
                                                                                     label=new_label)                       
                            if created == True:
                                allowed_annot.save()
                            collection.allowed_annotations.add(allowed_annot)

                    messages.info(request,"Label generation successful.")
                else:
                    messages.info(request,"An annotation name is required.")
        else:                
            messages.info(request, "You do not have permission to perform this action.")
            return HttpResponseRedirect(collection.get_absolute_url())

    return redirect('view_label',cid=cid)


@login_required
def remove_label(request,cid,lid):
    '''remove_label will remove a label from a collection.
    :param cid: the collection id to associate the label with (not required, but no url accessible for it) 
    :param lid: if provided on a post, the label will be added to the collection as an allowed annotation
    '''
    collection = get_collection(cid)

    if request.user == collection.owner:
        allowed_annotation = Annotation.objects.get(id=lid)
        collection.allowed_annotations.remove(allowed_annotation)
        collection.save()
        messages.info(request,"Label removed successfully.")
    else:                
        messages.info(request, "You do not have permission to perform this action.")
        return HttpResponseRedirect(collection.get_absolute_url())
    return redirect('view_label',cid=cid,tid=tid)


