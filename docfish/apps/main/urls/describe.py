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

from django.conf.urls import url
import docfish.apps.main.views as views

urlpatterns = [

    # Collections, describe new randomly selected image or text
    url(r'^collections/(?P<cid>\d+)/images/describe$',views.collection_describe_image,name='collection_describe_image'),
    url(r'^collections/(?P<cid>\d+)/text/describe$',views.collection_describe_text,name='collection_describe_text'),

    # Collections, save image or text and go to next randomly selected
    url(r'^collections/(?P<cid>\d+)/text/describe$',views.describe_text,name='describe_text'),
    url(r'^collections/(?P<cid>\d+)/images/describe$',views.describe_image,name='describe_image'),

    # Teams, describe first image or text
    url(r'^collections/(?P<cid>\d+)/teams/(?P<tid>\d+)/describe/texts$',views.describe_text,name='team_describe_text'),
    url(r'^collections/(?P<cid>\d+)/teams/(?P<tid>\d+)/describe/images$',views.describe_image,name='team_describe_image'),

    # Teams, describe specific image or text
    url(r'^collections/(?P<cid>\d+)/text/(?P<uid>\d+)/teams/(?P<tid>\d+)/describe$',views.describe_text,name='describe_text'),
    url(r'^collections/(?P<cid>\d+)/images/(?P<uid>\d+)/teams/(?P<tid>\d+)/describe$',views.describe_image,name='describe_image'),
 
   
]
