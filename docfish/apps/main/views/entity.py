'''

entity views

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

from docfish.apps.main.models import Entity
from docfish.apps.main.permission import get_permissions

from docfish.apps.main.utils import *
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

import os
import re
import tempfile


@login_required
def view_entity(request,cid,eid):
    collection = get_collection(cid)
    entity = get_entity(eid)

    context = {"entity":entity,
               "collection":collection}

    # Get all permissions, context must have collection as key
    context = get_permissions(request,context)

    return render(request, 'entities/entity_details.html', context)
    

@login_required
def remove_entity(request,cid,eid):
    collection = get_collection(cid)
    entity = get_entity(eid)

    if request.user == collection.owner:
        if entity.collection.count() == 1:
            entity.delete()
        else:
            collection.entity_set.remove(entity)
        messages.info(request,"Entity successfully removed from collection.")
    else:
        messages.info(request, "You do not have permission to perform this action.")
    return HttpResponseRedirect(collection.get_absolute_url())


@login_required
def delete_collection_entities(request,cid):
    '''delete_collection_entities will remove entities from a collection,
    and delete the collection.
    '''
    collection = get_collection(cid)

    if request.user == collection.owner:
        for entity in collection.entity_set.all():
            if entity.collection.count() == 1:
                entity.delete()
            else:
                collection.entity_set.remove(entity)
        messages.info(request,"Collection entities successfully removed.")
    else:                
        messages.info(request, "You do not have permission to perform this action.")
    return HttpResponseRedirect(collection.get_absolute_url())


