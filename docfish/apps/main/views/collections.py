'''

collections views

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

from docfish.apps.main.forms import CollectionForm
from docfish.apps.main.stats import (
    count_collection_annotations,
    count_task_annotations
)

from docfish.apps.main.permission import (
    has_collection_annotate_permission,
    has_collection_edit_permission,
    get_permissions
)

from docfish.apps.main.utils import *
from docfish.apps.main.views.labels import view_label

from docfish.apps.users.utils import (
    get_user
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


###############################################################################################
# Contributors ################################################################################
###############################################################################################

@login_required
def edit_contributors(request,cid):
    '''edit_contributors is the view to see, add, and delete contributors for a set.
    '''
    collection = get_collection(cid)
    if request.user == collection.owner:

        # Who are current contributors?
        contributors = collection.contributors.all()

        # Any user that isn't the owner or already a contributor can be added
        invalid_users = [x.id for x in contributors] + [request.user.id]
        contenders = [x for x in User.objects.all() if x.username != 'AnonymousUser']
        contenders = [x for x in contenders if x.id not in invalid_users]

        context = {'contributors':contributors,
                   'collection':collection,
                   'contenders':contenders}
        
        return render(request, 'collections/edit_collection_contributors.html', context)

    # Does not have permission, return to collection
    messages.info(request, "You do not have permission to perform this action.")
    return redirect('collection_details',kwargs={'cid':collection.id})


@login_required
def add_contributor(request,cid):
    '''add a new contributor to a collection
    :param did: the collection id
    '''
    collection = get_collection(cid)
    if request.user == collection.owner:
        if request.method == "POST":
            user_id = request.POST.get('user',None)
            if user_id:
                user = get_user(user_id)
                collection.contributors.add(user)
                collection.save()

                # Alert the user of the status change
                message = """You have been added as a contributor to the %s.""" %(collection.name)
                notify.send(collection.owner, recipient=user, verb=message)
                messages.success(request, 'User %s added as contributor to collection.' %(user))

    return edit_contributors(request,did)


@login_required
def remove_contributor(request,cid,uid):
    '''remove a contributor from a collection
    :param did: the collection id
    :param uid: the contributor (user) id
    '''
    collection = get_collection(cid)
    user = get_user(uid)
    contributors = collection.contributors.all()
    if request.user == collection.owner:
        if user in contributors:    
            collection.contributors = [x for x in contributors if x != user]
            collection.save()
            messages.success(request, 'User %s is no longer a contributor to the collection.' %(contributor))

    return redirect('edit_contributors',cid)



###############################################################################################
# Collections #################################################################################
###############################################################################################


# View all collections
def view_collections(request):
    has_collections = False
    collections = Collection.objects.all()
    context = {"collections":collections,
               "page_title":"Collections"}
    return render(request, 'collections/all_collections.html', context)


# Personal collections
@login_required
def my_collections(request):
    collections = Collection.objects.filter(owner=request.user)
    context = {"collections":collections,
               "page_title":"My Collections"}
    return render(request, 'collections/all_collections.html', context)


@login_required
def view_collection(request,cid):
    collection = get_collection(cid)
    entity_count = collection.entity_set.count()
    context = {"collection":collection,
               "entity_count":entity_count}

    # Get all permissions, context must have collection as key
    context = get_permissions(request,context)

    return render(request, 'collections/collection_details.html', context)


@login_required
def collection_explorer(request,cid):

    collection = get_collection(cid)
    if has_collection_edit_permission(request,collection) or collection.private is False:
        entity_count = collection.entity_set.count()
        context = {"collection":collection,
                   "entity_count":entity_count,
                   "nosidebar":"iloveparsnips"}

        # Get all permissions, context must have collection as key
        context = get_permissions(request,context)
        return render(request, 'collections/collection_explorer.html', context)
    
    messages.info(request, '''This collection is private. 
                              You must be an owner or contributor to explore this collection.''')
    return redirect("collections")


@login_required
def collection_stats(request,cid):
    '''return basic stats (counts) for collection
    '''
    collection = get_collection(cid)
    entity_count = collection.entity_set.count()
    image_count = Image.objects.filter(entity__collection=collection).count()
    text_count = Text.objects.filter(entity__collection=collection).count()
    counts = count_collection_annotations(collection)
    context = {"collection":collection,
               "entity_count":entity_count,
               "image_count":image_count,
               "text_count":text_count,
               "counts":counts,
               "nosidebar":"iloveparsnips"}

    return render(request, 'collections/collection_stats.html', context)


def collection_stats_detail(request,cid,fieldtype):
    '''return detailed stats (counts) for collection fieldtype
    '''
    collection = get_collection(cid)
    entity_count = collection.entity_set.count()
    image_count = Image.objects.filter(entity__collection=collection).count()
    text_count = Text.objects.filter(entity__collection=collection).count()
    counts = count_task_annotations(collection,fieldtype)
    if counts is not None:
        context = {"collection":collection,
                   "fieldtype":fieldtype,
                   "entity_count":entity_count,
                   "image_count":image_count,
                   "text_count":text_count,
                   "counts":counts,
                   "nosidebar":"iloveparsnips"}
        return render(request, 'collections/collection_stats_detail.html', context)
    messages.info(request,"collection %s does not have any counts for task %s" %(collection.name,fieldtype))
    return redirect('collection_stats',cid=cid)
    


# Edit collection
@login_required
def edit_collection(request, cid=None):
    '''edit_collection is the view to edit an existing collection, or 
    generate a new one, in the case that cid is not provided.
    :param cid: the collection id
    '''
    # If a cid is provided, we are editing an existing collection
    if cid:
        collection = get_collection(cid)
    else:
        collection = Collection(owner=request.user)

    # Only owners allowed to edit collections
    if request.user != collection.owner:
        messages.info(request, "You don't have permission to edit this collection.")
        return view_collections(request)
        
    if request.method == "POST":
        form = CollectionForm(request.POST,instance=collection)
        if form.is_valid():
 
            # Update annotators and contributors
            previous_contribs = set()
            if form.instance.id is not None:
                previous_contribs = set(form.instance.contributors.all())
            collection = form.save(commit=False)
            collection.save()

            form.save_m2m()  # save contributors

        messages.info(request,"Collection information updated.")
        return HttpResponseRedirect(collection.get_absolute_url())
    
    form = CollectionForm(instance=collection)
    edit_permission = has_collection_edit_permission(request,collection)
    context = {"form": form,
               "collection":collection,
               "edit_permission": edit_permission}

    return render(request, "collections/edit_collection.html", context)


@login_required
def delete_collection(request,cid):
    '''delete_collection will delete a collection.
    '''
    collection = get_collection(cid)

    if request.user == collection.owner:
        collection.delete()
        messages.info(request,"Collection successfully deleted.")
    else:                
        messages.info(request, "You do not have permission to perform this action.")
        return HttpResponseRedirect(collection.get_absolute_url())
    return redirect('collections')



@login_required
def collection_change_privacy(request,cid):
    '''make collection private or public.
    '''
    collection = get_collection(cid)

    if request.user == collection.owner:
        collection.private = not collection.private
        collection.save()
        if collection.private == True:
            messages.info(request,"Collection is now private.")
        else:
            messages.info(request,"Collection is now public.")
    else:                
        messages.info(request, "You do not have permission to perform this action.")
        return HttpResponseRedirect(collection.get_absolute_url())
    return redirect('collections')




@login_required
def collection_activate(request,cid,fieldtype=None):
    '''collection activate will turn an annotation or markup view on or off, or an entire
    collection on or off.
    '''
    collection = get_collection(cid)
    if request.user == collection.owner:

        # A fieldtype indicates we are turning a specific entry on or off
        if fieldtype is not None:
            if fieldtype in collection.status:

                # For fieldtype "image_annotation" and "text_annotation" the user needs labels
                if fieldtype in ['image_annotation','text_annotation']:
                    if collection.status[fieldtype]['active'] is False and collection.allowed_annotations.count() == 0:
                        messages.info(request,"You must create labels before using annotation.")
                        return view_label(request,collection.id)

                # Otherwise, let them freely change it
                collection.status[fieldtype]['active'] = not collection.status[fieldtype]['active']
                collection.save()
                if collection.status[fieldtype]['active'] == True:
                    status = "Active"
                else:
                    status = "Inactive"
                messages.info(request,"%s now has class %s." %(fieldtype,status))
            else:
                message.info(request,"%s is not a valid annotation or markup type for a Collection.")
    else:
        messages.info(request,"You don't have permission to perform this action.")
    return redirect('collection_start',cid=cid)
 


@login_required
def collection_start(request,cid,status=None):
    '''collection start is the primary annotation portal to show links to all annotation options
    for the collection, depending on the data present. This is also the view for the collection owner
    to make changes
    '''
    collection = get_collection(cid)
    if status == None:
        status = collection.status

    if collection.private == True:
        if not has_collection_annotate_permission(request,collection):
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
               "nosidebar":"turkeybutt"}

    # Get all permissions, context must have collection as key
    context = get_permissions(request,context)

    return render(request, 'portals/collection_start.html', context)
