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

from django.core.files.base import ContentFile
from notifications.signals import notify

from docfish.settings import (
    BASE_DIR, 
    MEDIA_ROOT
)

from django.contrib.auth.models import User
from docfish.apps.users.utils import (
    get_user
)

from docfish.apps.pubmed.utils import get
from docfish.apps.main.models import Collection

from django.core.exceptions import PermissionDenied, ValidationError
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

import pickle
import json
import os

media_dir = os.path.join(BASE_DIR,MEDIA_ROOT)

@login_required
def search_view(request):
    collections = Collection.objects.filter(owner=request.user)
    context = {"collections":collections}
    return render(request, 'pubmed/search.html',context)



@login_required
def searching_view(request,page=None):
    '''this is the function to do the search using pubmed (Entrez) utility
    ''' 
    if page is None:
        retstart = 0
        page = 0
    else:
        page = int(page)
        retstart = page * 50

    q = None
    uid = None
    if request.is_ajax():
        q = request.GET.get('q')
        uid = request.GET.get('uid')
    if request.method == "POST":
        q = request.POST.get('q')
        uid = request.POST.get('uid')
    if q is not None:            
        results = get(query=q,
                      user=request.user,
                      retstart=retstart,
                      retmax=50)
 
        context = {"results":results,
                   "submit_result": "anything"}

        if uid is not None:
            user = User.objects.get(id=uid)
            context['collections'] = Collection.objects.filter(owner=user)
            context['page'] = page
            context['next_page'] = page + 1
            context['query'] = q
            if page > 0:
                context['previous_page'] = page - 1

        if request.is_ajax():
            return render(request,'pubmed/result.html', context)

    return redirect('search_pubmed')
