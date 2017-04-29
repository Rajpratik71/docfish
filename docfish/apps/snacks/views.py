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

from django.core import serializers
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, render
from django.template.context import RequestContext

import logging
import os
import pickle

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, 
    JsonResponse,
    HttpResponseBadRequest, 
    HttpResponseRedirect
)

from docfish.settings import (
    PAGINATION_SIZE,
    SNACK_PRICE
)

from docfish.apps.snacks.models import (
    Snack,
    SnackBox
)

from docfish.apps.users.utils import (
    count_annotations_bydate,
    get_user
)

from docfish.apps.snacks.utils import (
    get_snack,
    get_snacks,
    get_user_snacks,
    get_snacks_tags,
    request_snack,
    paginate_results
)

from django.db.models import Q
import hashlib


##################################################################################
# SNACK VIEWS ####################################################################
##################################################################################


def snacks_home(request):
    '''snacks home introduces the user to docfishSnacks
    '''
    context = dict()
    if request.user.is_authenticated():
        snacks = get_user_snacks(request.user)
        context["snacks"] = snacks
    return render(request, "snacks/snacks_home.html", context)


@login_required
def snack_details(request,sid):
    '''allows a user to view details about a snack
    '''
    snack = get_snack(sid)
    snackbox = get_user_snacks(request.user,return_snackbox=True)
    context = {"snack": snack,
               "snackbox":snackbox}
    return render(request, "snacks/snack_details.html", context)


@login_required
def redeem_snacks(request):
    '''allows a user to request a snack
    '''
    snackbox = get_user_snacks(request.user,return_snackbox=True)
    context = {"snackbox": snackbox }

    # If it's a post, they are asking to redeem a snack
    if request.method == "POST":
        message = request.POST.get('message', None)
        if snackbox.earned_snack == True:
            snackbox = request_snack(snackbox,message=message)
            messages.info(request,"Snack request submit!")

    # Can they earn another snack?
    if snackbox.earned_snack == True:
        context['worthy'] = "yes"
    return render(request, "snacks/redeem_snacks.html", context)


@login_required
def snack_category(request,cid,page=None):
    '''allows a user to view snacks filtered to a category
    '''
    snacks = get_snacks(tag_ids=cid)

    return all_snacks(request,
                      page=page,
                      snacks=snacks)

@login_required
def all_snacks(request,page=None,snacks=None,tags=None):
    '''show the user available snacks for selection
    :param page: if defined, return a specific page for a snack
    :param snacks: if defined, don't retrieve entire set
    :param tags: If defined, show custom set of tags
    '''

    if page == None:
        page = 1

    if snacks == None:
        snacks = get_snacks()

    if tags == None:
        tags = get_snacks_tags(snacks)
    
    if len(snacks) >= PAGINATION_SIZE:
        total_pages = int(PAGINATION_SIZE / len(snacks))
        page_list = list(range(1,total_pages+1))

        # Break results into pagination size
        snacks = paginate_results(snacks,
                                  size=PAGINATION_SIZE,
                                  page=page)
    else:
        total_pages = 1
        page_list = [1]

    # Get user snacks for snackbox updating
    usersnacks = get_user_snacks(request.user,
                                 return_ids=True)

    if len(snacks) == 0:
        messages.info(request,"Uhoh, we didn't find any snacks! Why not try a search?")
        return search_view(request)

    context = {"snacks": snacks,
               "nosidebar":'pickledawg',
               "tags": tags,
               "page": page,
               "last_page": total_pages,
               "pages": page_list,
               "usersnacks": usersnacks}

    return render(request, "snacks/all_snacks.html", context)


def view_snacks(request,user=None):
    '''allows a user to view his or her snacks
    '''
    if user == None:
        user = request.user

    # View is not login only, so non authenticated without user need redirect
    elif request.user.is_anonymous():
        messages.info(request,"You must be logged in to see your snacks!")
        return redirect('collections')

    snacks = get_user_snacks(user,by_tag=True)
    snackbox = get_user_snacks(user,return_snackbox=True)
    dates = count_annotations_bydate(user)
    context = {"categories": snacks,
               "user": user,
               "dates":dates,
               "snackbox":snackbox, #TODO: look into why count is off
               "snack_price":SNACK_PRICE}
    return render(request, "snacks/my_snacks.html", context)


def user_snacks(request,uid):
    '''see snackbox of other users
    '''
    user = get_user(uid)
    return view_snacks(request,user=user)


@login_required
def disable_snack(request,sid):
   '''disable a snack
   '''
   snack = get_snack(sid)
   if request.user.is_authenticated():
       snack.active = False
       snack.save()
       return JsonResponse({"message":"Snack disabled"})
   return JsonResponse({"message":"Error disabling snack!"})


@login_required
def enable_snack(request,sid):
   '''enable a snack
   '''
   snack = get_snack(sid)
   if request.user.is_authenticated():
       snack.active = True
       snack.save()
       return JsonResponse({"message":"Snack enabled"})
   return JsonResponse({"message":"Error enabling snack!"})



##################################################################################
# USER SNACK VIEWS ###############################################################
##################################################################################

@login_required
def add_snack(request,sid):
   '''add a snack to a user's set
   '''
   snack = get_snack(sid)

   if request.method == "POST":
       usersnacks = get_user_snacks(request.user,return_snackbox=True)   
       usersnacks.snacks.add(snack)
       usersnacks.save()
       return JsonResponse({"message":"Snack added successfully"})
   return JsonResponse({"message":"Error adding snack!"})


@login_required
def remove_snack(request,sid):
   '''remove a snack from a user's set
   '''
   snack = get_snack(sid)

   if request.method == "POST":
       usersnacks = get_user_snacks(request.user,return_snackbox=True)   
       usersnacks.snacks.remove(snack)
       usersnacks.save()
       return JsonResponse({"message":"Snack removed successfully"})
   return JsonResponse({"message":"Error removing snack!"})



##################################################################################
# SNACK SEARCH VIEWS #############################################################
##################################################################################


def search_view(request):
    tags = get_snacks_tags()
    context = {'tags':tags}
    return render(request, 'search/search.html', context)


def snack_search(request):
    '''snack_search is the ajax driver to show results for a snack search.
    the request can be ajax (from the search page) or live search page (non ajax)
    ''' 
    q = None
    if request.is_ajax():
        q = request.GET.get('q')
    if request.method == "POST":
        q = request.POST.get('q')
    if q is not None:            
        results = Snack.objects.filter(
            Q(tags__name__contains=q) |
            Q(name__contains=q) |
            Q(id__contains=q) |
            Q(url__contains=q)).order_by('name').distinct()

        tags = get_snacks_tags()
 
        context = {"results":results,
                   "submit_result": "anything",
                   "tags":tags}

        if request.is_ajax():
            return render(request,'search/result.html', context)
        return render(request,'search/search_full.html', context)

    return redirect('search')
