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


from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.urls import reverse
#from social_django.utils import load_strategy, load_backend
import hashlib

def index_view(request):
    return render(request, 'base/index.html')

def about_view(request):
    return render(request, 'base/about.html')

def data_view(request):
    return render(request, 'base/data.html')

def user_guide_view(request):
    return render(request, 'base/user_guide.html')

# SAML Authentication

#def saml_metadata_view(request):
#    complete_url = reverse('social:complete', args=("saml", ))
#    saml_backend = load_backend(
#        load_strategy(request),
#        "saml",
#        redirect_uri=complete_url,
#    )
#    metadata, errors = saml_backend.generate_metadata_xml()
#    if not errors:
#        return HttpResponse(content=metadata, content_type='text/xml')


# Error Pages ##################################################################

def handler404(request):
    return render(request,'base/404.html')

def handler500(request):
    return render(request,'base/500.html')
