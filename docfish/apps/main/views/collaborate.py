'''

collaboration (team) views

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

from notifications.signals import notify
from docfish.apps.main.models import *

from docfish.apps.main.permission import (
    has_collection_annotate_permission,
    has_collection_edit_permission,
    get_permissions
)

from docfish.apps.main.utils import *
from docfish.settings import DOMAIN_NAME
from docfish.apps.users.utils import (
    get_user,
    get_team
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

import os
import re

@login_required
def team_video(request,tid):
    team = get_collection(tid)
        
    context = {"team":team,
               "collaborate":"pohyes",
               "nosidebar":"turkeybutt"}

    return render(request, 'collaborate/team_video.html', context)


@login_required
def team_portal(request,tid,cid,status=None):
    team = get_team(tid)
    collection = get_collection(cid)

    if status == None:
        status = collection.status
        
    if collection.private == True:
        if not has_collection_annotate_permission(request,collection,team):
            messages.info(request, '''This collection is private. You must be a contributor
                                      or member of the owner's institution to annotate.''')
            return redirect("collections")

    image_types = [x for x in list(status.keys()) if re.search('^image_',x)]
    text_types = [x for x in list(status.keys()) if re.search('^text_',x)]
    needs_labels = [x for x in list(status.keys()) if re.search('_annotation$',x)]

    # Update collection status based on having images/text or not.
    if collection.has_images() == False:
        for image_type in image_types:
            status[image_type]['active'] = False
    if collection.has_text() == False:
        for text_type in text_types:
            status[text_type]['active'] = False

    # We cannot annotate without labels
    if collection.allowed_annotations.count() < 1:
        for needs_label in needs_labels:
            status[needs_label]['active'] = False

    context = {"collection":collection,
               "collection_status":status,
               "image_types":image_types,
               "text_types":text_types,
               "nosidebar":"turkeybutt",
               "domain":DOMAIN_NAME,
               "team":team}

    # Get all permissions, context must have collection as key
    context = get_permissions(request,context)

    return render(request,'portals/team_start.html',context)
