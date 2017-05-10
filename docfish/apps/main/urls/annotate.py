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

    # Collections, annotate newly selected image or text
    url(r'^collections/(?P<cid>\d+)/images/annotate$',views.collection_annotate_image,name='collection_annotate_image'),
    url(r'^collections/(?P<cid>\d+)/text/annotate$',views.collection_annotate_text,name='collection_annotate_text'),

    # Collections or teams, update an annotation or text. Teams pass the team_id via the request.POST
    url(r'^annotate/images/(?P<uid>\d+)/update$',views.update_image_annotation,name='update_image_annotation'),
    url(r'^annotate/images/(?P<uid>\d+)/clear$',views.clear_image_annotations,name='clear_image_annotations'),
    url(r'^annotate/text/(?P<uid>\d+)/update$',views.update_text_annotation,name='update_text_annotation'),
    url(r'^annotate/text/(?P<uid>\d+)/clear$',views.clear_text_annotations,name='clear_text_annotations'),
 
    # Teams, annotate first image or text
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/annotate$',views.team_annotate_text,name='team_annotate_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/annotate$',views.team_annotate_image,name='team_annotate_image'),

    # Teams, annotate specific image or text
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/text/(?P<uid>\d+)/annotate$',views.team_annotate_text,name='team_annotate_text'),
    url(r'^teams/(?P<tid>\d+)/collection/(?P<cid>\d+)/images/(?P<uid>\d+)/annotate$$',views.team_annotate_image,name='team_annotate_image'),

   
]
